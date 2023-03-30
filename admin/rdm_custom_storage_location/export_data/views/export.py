# -*- coding: utf-8 -*-
import inspect  # noqa
import logging
import os

from celery.contrib.abortable import AbortableAsyncResult, ABORTED
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import authentication as drf_authentication
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from addons.osfstorage.models import Region
from admin.rdm_custom_storage_location import tasks
from osf.models import Institution, ExportDataLocation, ExportData
from website.util import inspect_info  # noqa
from .location import ExportStorageLocationViewBaseView
from ..utils import write_json_file

logger = logging.getLogger(__name__)


class ExportDataBaseActionView(ExportStorageLocationViewBaseView, APIView):
    raise_exception = True
    parser_classes = (JSONParser,)
    authentication_classes = (
        drf_authentication.SessionAuthentication,
    )

    def extract_input(self, request, *args, **kwargs):
        institution_id = request.data.get('institution_id')
        source_id = request.data.get('source_id')
        location_id = request.data.get('location_id')

        # admin not affiliated with this institution
        if not institution_id or (not request.user.is_super_admin and not request.user.is_affiliated_with_institution_id(institution_id)):
            return Response({'message': f'Permission denied for this institution'}, status=status.HTTP_400_BAD_REQUEST)

        institution = Institution.objects.get(pk=institution_id)

        # this institutional storage is not allowed
        if not source_id or not institution.is_allowed_institutional_storage_id(source_id):
            return Response({'message': f'Permission denied for this storage'}, status=status.HTTP_400_BAD_REQUEST)

        source_storage = Region.objects.get(pk=source_id)

        # this storage location is not allowed
        if not location_id or not institution.have_allowed_storage_location_id(location_id):
            return Response({'message': f'Permission denied for this export storage location'}, status=status.HTTP_400_BAD_REQUEST)

        location = ExportDataLocation.objects.get(pk=location_id)

        return institution, source_storage, location


class ExportDataActionView(ExportDataBaseActionView):

    def post(self, request, *args, **kwargs):
        institution, source_storage, location = self.extract_input(request)

        # Create new process record
        try:
            export_data = ExportData.objects.create(
                source=source_storage,
                location=location,
                status=ExportData.STATUS_ERROR,
            )
        except IntegrityError:
            return Response({'message': f'The equivalent process is running'}, status=status.HTTP_400_BAD_REQUEST)

        # create new task
        cookies = request.COOKIES
        cookie = request.user.get_or_create_cookie().decode()
        task = tasks.run_export_data_process.delay(cookies, export_data.id, cookie=cookie)
        task_id = task.task_id
        export_data.task_id = task_id
        export_data.save()

        return Response({
            'task_id': task_id,
            'task_state': task.state,
        }, status=status.HTTP_200_OK)


def export_data_process(task, cookies, export_data_id, **kwargs):
    logger.debug('----{}:{}::{} from {}:{}::{}'.format(*inspect_info(inspect.currentframe(), inspect.stack())))
    # get corresponding export data record
    export_data = None
    while export_data is None:
        export_data_set = ExportData.objects.filter(pk=export_data_id)
        export_data = export_data_set.first()
    assert export_data

    # start process
    export_data.status = ExportData.STATUS_RUNNING
    export_data.save()

    # extract file information
    export_data_json, file_info_json = export_data.extract_file_information_json_from_source_storage()

    if task.is_aborted():  # check before each steps
        return None
    # create export data process folder
    logger.debug(f'creating export data process folder')
    response = export_data.create_export_data_folder(cookies, **kwargs)
    if not task.is_aborted() and response.status_code != 201:
        return export_data_rollback_process(cookies, export_data_id, **kwargs)
    logger.debug(f'created export data process folder')

    # export target file and accompanying data
    if task.is_aborted():  # check before each steps
        return None
    # create 'files' folder
    logger.debug(f'creating files folder')
    response = export_data.create_export_data_files_folder(cookies, **kwargs)
    if not task.is_aborted() and response.status_code != 201:
        return export_data_rollback_process(cookies, export_data_id, **kwargs)
    logger.debug(f'created files folder')

    if task.is_aborted():  # check before each steps
        return None
    # upload file versions
    logger.debug(f'uploading file versions')
    file_versions = export_data.get_source_file_versions_min(file_info_json)
    for file in file_versions:
        project_id, provider, file_path, version, file_name = file
        kwargs.update({'version': version})
        # kwargs.setdefault('version', version)
        if task.is_aborted():  # check before each steps
            return None
        # get content data file from source
        response = export_data.read_data_file_from_source(cookies, project_id, provider, file_path, **kwargs)
        if not task.is_aborted() and response.status_code != 200:
            return export_data_rollback_process(cookies, export_data_id, **kwargs)
        file_data = response.content
        if task.is_aborted():  # check before each steps
            return None
        # transfer content data file to location
        response = export_data.transfer_export_data_file_to_location(cookies, file_name, file_data, **kwargs)
        # 409: file is existing (able diff in path)
        # 201: created
        if not task.is_aborted() and response.status_code != 201 and response.status_code not in (409,):
            return export_data_rollback_process(cookies, export_data_id, **kwargs)
    logger.debug(f'uploaded file versions')

    # temporary file
    temp_file_path = export_data.export_data_temp_file_path

    if task.is_aborted():  # check before each steps
        return None
    # create files' information file
    logger.debug(f'creating files information file')
    write_json_file(file_info_json, temp_file_path)
    response = export_data.upload_file_info_file(cookies, temp_file_path, **kwargs)
    if not task.is_aborted() and response.status_code != 201:
        return export_data_rollback_process(cookies, export_data_id, **kwargs)
    logger.debug(f'created files information file')

    process_end = timezone.make_naive(timezone.now(), timezone.utc)

    if task.is_aborted():  # check before each steps
        return None
    # create export data file
    logger.debug(f'creating export data file')
    export_data_json['process_end'] = process_end.strftime('%Y-%m-%d %H:%M:%S')
    write_json_file(export_data_json, temp_file_path)
    response = export_data.upload_export_data_file(cookies, temp_file_path, **kwargs)
    if not task.is_aborted() and response.status_code != 201:
        return export_data_rollback_process(cookies, export_data_id, **kwargs)
    logger.debug(f'created export data file')

    # remove temporary file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    logger.debug(f'removed temporary file')

    if task.is_aborted():  # check before each steps
        return None
    # re-check status to ensure that it is not in stopping process
    export_data_set = ExportData.objects.filter(pk=export_data_id)
    export_data = export_data_set.first()
    assert export_data

    if export_data.status == ExportData.STATUS_RUNNING:
        # complete process
        export_data_set.update(
            status=ExportData.STATUS_COMPLETED,
            process_end=process_end,
            export_file=export_data.get_export_data_file_path(),
            project_number=export_data_json.get('projects_numb', 0),
            file_number=export_data_json.get('files_numb', 0),
            total_size=export_data_json.get('size', 0),
        )
    logger.debug(f'completed process')


class StopExportDataActionView(ExportDataBaseActionView):

    def post(self, request, **kwargs):
        institution, source_storage, location = self.extract_input(request)
        task_id = request.data.get('task_id')

        # get corresponding export data record
        export_data_set = ExportData.objects.filter(source=source_storage, location=location, task_id=task_id)
        if not task_id or not export_data_set.exists():
            return Response({'message': f'Permission denied for this export process'}, status=status.HTTP_400_BAD_REQUEST)

        export_data = export_data_set.first()
        task = AbortableAsyncResult(task_id)
        if export_data.status != ExportData.STATUS_RUNNING:
            return Response({
                'task_id': task_id,
                'task_state': task.state,
                'status': export_data.status,
                'message': f'Cannot stop this export process'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Abort the corresponding task_id
        task.abort()
        # task.revoke(terminate=True)
        if task.state != ABORTED:
            return Response({'message': f'Cannot abort this export process'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete export data file which created on export process
        cookie = request.user.get_or_create_cookie().decode()
        cookies = request.COOKIES
        task = tasks.run_export_data_rollback_process.delay(cookies, export_data.id, cookie=cookie)
        task_id = task.task_id
        export_data.task_id = task_id
        export_data.save()

        return Response({
            'task_id': task_id,
            'task_state': task.state,
        }, status=status.HTTP_200_OK)


def export_data_rollback_process(cookies, export_data_id, **kwargs):
    logger.debug('----{}:{}::{} from {}:{}::{}'.format(*inspect_info(inspect.currentframe(), inspect.stack())))
    # get corresponding export data record
    export_data_set = export_data = None
    while export_data is None:
        export_data_set = ExportData.objects.filter(pk=export_data_id)
        export_data = export_data_set.first()
    assert export_data

    # when exception
    if export_data.status in [ExportData.STATUS_STOPPING, ExportData.STATUS_STOPPED]:
        logger.debug(f'stop-processing')
        return None

    if export_data.status == ExportData.STATUS_RUNNING:
        # stop it
        export_data_set.update(
            status=ExportData.STATUS_STOPPING,
        )
    logger.debug(f'stopping process')

    file_path = export_data.export_data_temp_file_path
    if os.path.exists(file_path):
        os.remove(file_path)
    logger.debug(f'removed temporary file')

    export_data_status = ExportData.STATUS_STOPPED
    # delete export data file
    logger.debug(f'deleting export data file')
    response = export_data.delete_export_data_folder(cookies, **kwargs)
    if response.status_code != 204:
        export_data_status = ExportData.STATUS_ERROR
    logger.debug(f'deleted export data file')

    # stop it
    export_data_set.update(
        status=export_data_status,
        process_end=timezone.make_naive(timezone.now(), timezone.utc),
        export_file=None,
    )
    logger.debug(f'stopped process')


class CheckStateExportDataActionView(ExportDataBaseActionView):

    def post(self, request, **kwargs):
        institution, source_storage, location = self.extract_input(request)
        task_id = request.data.get('task_id')

        # get corresponding export data record
        export_data_set = ExportData.objects.filter(source=source_storage, location=location, task_id=task_id)
        if not task_id or not export_data_set.exists():
            return Response({'message': f'Permission denied for this export process'}, status=status.HTTP_400_BAD_REQUEST)

        export_data = export_data_set.first()
        task = AbortableAsyncResult(task_id)

        return Response({
            'task_id': task_id,
            'task_state': task.state,
            'result': task.result if isinstance(task.result, str) or isinstance(task.result, dict) else {},
            'status': export_data.status,
        }, status=status.HTTP_200_OK)


class CheckDataExportDataActionView(ExportDataBaseActionView):

    def post(self, request, **kwargs):
        institution, source_storage, location = self.extract_input(request)

        has_data = ExportData.objects.filter(
            location=location,
            source=source_storage,
            status__in=ExportData.EXPORT_DATA_AVAILABLE,
            is_deleted=False
        ).exists()

        return Response({
            'has_data': has_data,
        }, status=status.HTTP_200_OK)