# -*- coding: utf-8 -*-
from flask import request
import logging
import requests
import json
import time
import pytz
from datetime import datetime, timedelta
from addons.integromat import SHORT_NAME, FULL_NAME
from django.db import transaction
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.integromat.serializer import IntegromatSerializer
from osf.models import ExternalAccount, OSFUser
from django.core.exceptions import ValidationError
from framework.exceptions import HTTPError
from rest_framework import status as http_status
from osf.utils.permissions import ADMIN, READ
from website.project.decorators import (
    must_have_addon,
    must_be_valid_project,
    must_have_permission,
)
from admin.rdm_addons.decorators import must_be_rdm_addons_allowed
from website.ember_osf_web.views import use_ember_app
from addons.integromat import settings
from addons.integromat import models
from osf.models.rdm_grdmapps import RdmWebMeetingApps, RdmWorkflows
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from framework.auth.core import Auth
from admin.rdm import utils as rdm_utils
from osf.models import AbstractNode
from framework.database import get_or_http_error
_load_node_or_fail = lambda pk: get_or_http_error(AbstractNode, pk)

logger = logging.getLogger(__name__)

integromat_account_list = generic_views.account_list(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_get_config = generic_views.get_config(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_import_auth = generic_views.import_auth(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

integromat_set_config = generic_views.set_config(
    SHORT_NAME,
    FULL_NAME,
    IntegromatSerializer,
    ''
)

@must_be_logged_in
@must_be_rdm_addons_allowed(SHORT_NAME)
def integromat_add_user_account(auth, **kwargs):
    """Verifies new external account credentials and adds to user's list"""

    try:
        access_token = request.json.get('integromat_api_token')

    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    #integromat auth
    integromatUserInfo = authIntegromat(access_token, settings.H_SDK_VERSION)

    if not integromatUserInfo:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)
    else:
        integromat_userid = integromatUserInfo['id']
        integromat_username = integromatUserInfo['name']

    user = auth.user

    try:
        account = ExternalAccount(
            provider=SHORT_NAME,
            provider_name=FULL_NAME,
            display_name=integromat_username,
            oauth_key=access_token,
            provider_id=integromat_userid,
        )
        account.save()
    except ValidationError:
        # ... or get the old one
        account = ExternalAccount.objects.get(
            provider='integromat', provider_id=integromat_userid
        )
        if account.oauth_key != access_token:
            account.oauth_key = access_token
            account.save()

    if not user.external_accounts.filter(id=account.id).exists():

        user.external_accounts.add(account)

    user.get_or_add_addon('integromat', auth=auth)

    user.save()

    return {}

def authIntegromat(access_token, hSdkVersion):

    message = ''
    token = 'Token ' + access_token
    payload = {}
    headers = {
        'Authorization': token,
        'x-imt-apps-sdk-version': hSdkVersion
    }

    response = requests.request('GET', settings.INTEGROMAT_API_WHOAMI, headers=headers, data=payload)
    status_code = response.status_code
    userInfo = response.json()

    if status_code != 200:

        if userInfo.viewkeys() >= {'message'}:
            message = userInfo['message']

        logger.info('Failed to authenticate Integromat account' + '[' + str(status_code) + ']' + ':' + message)

        userInfo.clear()

    return userInfo

# ember: ここから
@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_grdmapps(**kwargs):
    return use_ember_app()

def makeInstitutionUserList(users):

    institutionUsers = []
    userInfo = {}
    logger.info(str(users))
    for user in users:
        userInfo = {}
        userInfo['guid'] = user._id
        userInfo['fullname'] = user.fullname
        logger.info(str(userInfo))
        institutionUsers.append(userInfo)

    ret = json.dumps(institutionUsers)

    return ret

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def grdmapps_get_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    auth = kwargs['auth']
    user = auth.user

    workflows = RdmWorkflows.objects.all()
    allWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    webMeetingApps = models.RdmWebMeetingApps.objects.all()
    nodeAttendeesAll = models.Attendees.objects.filter(node_settings_id=addon.id)
    nodeMicrosoftTeamsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(microsoft_teams_mail__exact='').exclude(microsoft_teams_mail__isnull=True)
    nodeWebexMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(webex_meetings_mail__exact='').exclude(webex_meetings_mail__isnull=True)
    nodeWorkflows = models.NodeWorkflows.objects.filter(node_settings_id=addon.id)

    nodeWebMeetingsAttendeesRelation = models.AllMeetingInformationAttendeesRelation.objects.filter(all_meeting_information__node_settings_id=addon.id)

    workflowsJson = serializers.serialize('json', workflows, ensure_ascii=False)
    allWebMeetingsJson = serializers.serialize('json', allWebMeetings, ensure_ascii=False)
    upcomingWebMeetingsJson = serializers.serialize('json', upcomingWebMeetings, ensure_ascii=False)
    previousWebMeetingsJson = serializers.serialize('json', previousWebMeetings, ensure_ascii=False)
    webMeetingAppsJson = serializers.serialize('json', webMeetingApps, ensure_ascii=False)
    nodeAttendeesAllJson = serializers.serialize('json', nodeAttendeesAll, ensure_ascii=False)
    nodeMicrosoftTeamsAttendeesJson = serializers.serialize('json', nodeMicrosoftTeamsAttendees, ensure_ascii=False)
    nodeWebexMeetingsAttendeesJson = serializers.serialize('json', nodeWebexMeetingsAttendees, ensure_ascii=False)
    nodeWorkflowsJson = serializers.serialize('json', nodeWorkflows, ensure_ascii=False)

    nodeWebMeetingsAttendeesRelationJson = serializers.serialize('json', nodeWebMeetingsAttendeesRelation, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)

    institutionUsers = makeInstitutionUserList(users)

    return {'data': {'id': node._id, 'type': 'grdmapps-config',
                     'attributes': {
                         'node_settings_id': addon._id,
                         'all_web_meetings': allWebMeetingsJson,
                         'upcoming_web_meetings': upcomingWebMeetingsJson,
                         'previous_web_meetings': previousWebMeetingsJson,
                         'node_attendees_all': nodeAttendeesAllJson,
                         'node_microsoft_teams_attendees': nodeMicrosoftTeamsAttendeesJson,
                         'node_webex_meetings_attendees': nodeWebexMeetingsAttendeesJson,
                         'node_web_meetings_attendees_relation': nodeWebMeetingsAttendeesRelationJson,
                         'workflows': workflowsJson,
                         'node_workflows': nodeWorkflowsJson,
                         'web_meeting_apps': webMeetingAppsJson,
                         'app_name_microsoft_teams': settings.MICROSOFT_TEAMS,
                         'app_name_webex_meetings': settings.WEBEX_MEETINGS,
                         'institution_users': institutionUsers
                     }}}

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def grdmapps_set_config_ember(**kwargs):

    logger.info('grdmapps_set_config_ember start')
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    auth = kwargs['auth']
    user = auth.user

    allWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    nodeAttendeesAll = models.Attendees.objects.filter(node_settings_id=addon.id)
    nodeMicrosoftTeamsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(microsoft_teams_mail__exact='').exclude(microsoft_teams_mail__isnull=True)
    nodeWebexMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(webex_meetings_mail__exact='').exclude(webex_meetings_mail__isnull=True)
    nodeWorkflows = models.NodeWorkflows.objects.filter(node_settings_id=addon.id)

    nodeWebMeetingsAttendeesRelation = models.AllMeetingInformationAttendeesRelation.objects.filter(all_meeting_information__node_settings_id=addon.id)

    allWebMeetingsJson = serializers.serialize('json', allWebMeetings, ensure_ascii=False)
    upcomingWebMeetingsJson = serializers.serialize('json', upcomingWebMeetings, ensure_ascii=False)
    previousWebMeetingsJson = serializers.serialize('json', previousWebMeetings, ensure_ascii=False)
    nodeAttendeesAllJson = serializers.serialize('json', nodeAttendeesAll, ensure_ascii=False)
    nodeMicrosoftTeamsAttendeesJson = serializers.serialize('json', nodeMicrosoftTeamsAttendees, ensure_ascii=False)
    nodeWebexMeetingsAttendeesJson = serializers.serialize('json', nodeWebexMeetingsAttendees, ensure_ascii=False)
    nodeWorkflowsJson = serializers.serialize('json', nodeWorkflows, ensure_ascii=False)

    nodeWebMeetingsAttendeesRelationJson = serializers.serialize('json', nodeWebMeetingsAttendeesRelation, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)
    institutionUsers = makeInstitutionUserList(users)

    return {'data': {'id': node._id, 'type': 'grdmapps-config',
                     'attributes': {
                         'all_web_meetings': allWebMeetingsJson,
                         'upcoming_web_meetings': upcomingWebMeetingsJson,
                         'previous_web_meetings': previousWebMeetingsJson,
                         'node_attendees_all': nodeAttendeesAllJson,
                         'node_microsoft_teams_attendees': nodeMicrosoftTeamsAttendeesJson,
                         'node_webex_meetings_attendees': nodeWebexMeetingsAttendeesJson,
                         'node_web_meetings_attendees_relation': nodeWebMeetingsAttendeesRelationJson,
                         'node_workflows': nodeWorkflowsJson,
                         'institution_users': institutionUsers
                     }}}

# ember: ここまで

#api for Integromat action
def integromat_api_call(*args, **kwargs):

    auth = Auth.from_kwargs(request.args.to_dict(), kwargs)
    user = auth.user

    # User must be logged in
    if user is None:
        raise HTTPError(http_status.HTTP_401_UNAUTHORIZED)

    logger.info('Integromat called integromat_api_call by ' + str(user) + '.')
    logger.info('GRDM-Integromat connection test scceeeded.')

    return {'email': str(user)}

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_register_meeting(**kwargs):

    logger.info('integromat called integromat_register_meeting')

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    nodeId = addon._id

    appName = request.get_json().get('appName')
    subject = request.get_json().get('subject')
    organizer = request.get_json().get('organizer')
    attendees = request.get_json().get('attendees')
    startDatetime = request.get_json().get('startDatetime')
    endDatetime = request.get_json().get('endDatetime')
    location = request.get_json().get('location')
    content = request.get_json().get('content')
    joinUrl = request.get_json().get('joinUrl')
    meetingId = request.get_json().get('meetingId')
    password = request.get_json().get('password')
    meetingInviteesInfo = request.get_json().get('meetingInviteesInfo')

    try:
        node = models.NodeSettings.objects.get(_id=nodeId)
    except ObjectDoesNotExist:
        logger.error('nodesettings _id is invalid.')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    try:
        webApp = RdmWebMeetingApps.objects.get(app_name=appName)
    except ObjectDoesNotExist:
        logger.error('web app name is invalid.')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    if appName == settings.MICROSOFT_TEAMS:

        try:
            organizer_fullname = models.Attendees.objects.get(node_settings_id=node.id, microsoft_teams_mail=organizer).fullname
        except ObjectDoesNotExist:
            logger.info('organizer is not registered.')
            organizer_fullname = organizer

    elif appName == settings.WEBEX_MEETINGS:

        try:
            organizer_fullname = models.Attendees.objects.get(node_settings_id=node.id, webex_meetings_mail=organizer).fullname
        except ObjectDoesNotExist:
            logger.info('organizer is not registered.')
            organizer_fullname = organizer

    with transaction.atomic():

        meetingInfo = models.AllMeetingInformation(
            subject=subject,
            organizer=organizer,
            organizer_fullname=organizer_fullname,
            start_datetime=startDatetime,
            end_datetime=endDatetime,
            location=location,
            content=content,
            join_url=joinUrl,
            meetingid=meetingId,
            meeting_password=password,
            app_id=webApp.id,
            node_settings_id=node.id,
        )
        meetingInfo.save()

        attendeeIds = []

        if appName == settings.MICROSOFT_TEAMS:

            for attendeeMail in attendees:

                qsAttendee = models.Attendees.objects.get(node_settings_id=node.id, microsoft_teams_mail=attendeeMail)
                attendeeId = qsAttendee.id
                attendeeIds.append(attendeeId)

        elif appName == settings.WEBEX_MEETINGS:

            try:
                meetingInviteesInfoJson = json.loads(meetingInviteesInfo)
            except TypeError:
                logger.error('meetingInviteesInfo is None')
                raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

            for meetingInvitee in meetingInviteesInfoJson:

                meetingInviteeInfo = None

                for attendeeMail in attendees:

                    qsAttendee = models.Attendees.objects.get(node_settings_id=node.id, webex_meetings_mail=attendeeMail)
                    attendeeId = qsAttendee.id
                    attendeeIds.append(attendeeId)

                    if meetingInvitee['email'] == attendeeMail:

                        meetingInviteeInfo = models.AllMeetingInformationAttendeesRelation(
                            attendees_id=attendeeId,
                            all_meeting_information_id=meetingInfo.id,
                            webex_meetings_invitee_id=meetingInvitee['id']
                        )
                        meetingInviteeInfo.save()

        meetingInfo.attendees = attendeeIds
        meetingInfo.save()

    return {}

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_update_meeting_registration(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    nodeId = addon._id

    appName = request.get_json().get('appName')
    subject = request.get_json().get('subject')
    attendees = request.get_json().get('attendees')
    startDatetime = request.get_json().get('startDatetime')
    endDatetime = request.get_json().get('endDatetime')
    location = request.get_json().get('location')
    content = request.get_json().get('content')
    meetingId = request.get_json().get('meetingId')
    meetingCreatedInviteesInfo = request.get_json().get('meetingCreatedInviteesInfo')
    meetingDeletedInviteesInfo = request.get_json().get('meetingDeletedInviteesInfo')
    qsUpdateMeetingInfo = models.AllMeetingInformation.objects.get(meetingid=meetingId)

    qsUpdateMeetingInfo.subject = subject
    qsUpdateMeetingInfo.start_datetime = startDatetime
    qsUpdateMeetingInfo.end_datetime = endDatetime
    qsUpdateMeetingInfo.location = location
    qsUpdateMeetingInfo.content = content

    try:
        node = models.NodeSettings.objects.get(_id=nodeId)
    except ObjectDoesNotExist:
        logger.error('nodesettings _id is invalid.')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    attendeeIds = []
    attendeeIdsFormer = []

    with transaction.atomic():

        if appName == settings.MICROSOFT_TEAMS:

            for attendeeMail in attendees:

                qsAttendee = models.Attendees.objects.get(node_settings_id=node.id, microsoft_teams_mail=attendeeMail)
                attendeeId = qsAttendee.id
                attendeeIds.append(attendeeId)

        elif appName == settings.WEBEX_MEETINGS:

            qsNodeWebMeetingsAttendeesRelation = models.AllMeetingInformationAttendeesRelation.objects.filter(all_meeting_information__meetingid=meetingId)

            try:
                meetingCreatedInviteesInfoJson = json.loads(meetingCreatedInviteesInfo)
                meetingDeletedInviteesInfoJson = json.loads(meetingDeletedInviteesInfo)
            except ObjectDoesNotExist:
                logger.error('meetingInviteesInfo or meetingDeletedInviteesInfoJson is None')
                raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

            for meetingAttendeeRelation in qsNodeWebMeetingsAttendeesRelation:

                attendeeIdsFormer.append(meetingAttendeeRelation.attendees)

            for meetingCreateInvitee in meetingCreatedInviteesInfoJson:

                meetingInviteeInfo = None

                qsAttendee = models.Attendees.objects.get(node_settings_id=node.id, webex_meetings_mail=meetingCreateInvitee['body']['email'])
                attendeeId = qsAttendee.id
                attendeeIdsFormer.append(attendeeId)

                meetingInviteeInfo = models.AllMeetingInformationAttendeesRelation(
                    attendees_id=attendeeId,
                    all_meeting_information_id=qsUpdateMeetingInfo.id,
                    webex_meetings_invitee_id=meetingCreateInvitee['body']['id']
                )
                meetingInviteeInfo.save()

            for meetingDeletedInvitee in meetingDeletedInviteesInfoJson:

                meetingInviteeInfo = None

                qsDeleteMeetingAttendeeRelation = models.AllMeetingInformationAttendeesRelation.objects.get(webex_meetings_invitee_id=meetingDeletedInvitee['value'])
                attendeeId = qsDeleteMeetingAttendeeRelation.attendees
                attendeeIdsFormer.remove(attendeeId)

                qsDeleteMeetingAttendeeRelation.delete()

            attendeeIds = attendeeIdsFormer

        qsUpdateMeetingInfo.attendees = attendeeIds

        qsUpdateMeetingInfo.save()

    return {}

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_delete_meeting_registration(**kwargs):

    meetingId = request.get_json().get('meetingId')

    qsDeleteMeeting = models.AllMeetingInformation.objects.get(meetingid=meetingId)
    qsDeleteMeeting.delete()

    return {}


@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_register_web_meeting_apps_email(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    logger.info(str(requestDataJson))
    _id = requestDataJson['_id']
    guid = requestDataJson['guid']
    fullname = requestDataJson['fullname']
    appName = requestDataJson['appName']
    email = requestDataJson['email']
    username = requestDataJson['username']
    is_guest = requestDataJson['is_guest']

    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)
    nodeId = nodeSettings.id

    if models.Attendees.objects.filter(node_settings_id=nodeId, _id=_id).exists():

        webMeetingAppAttendee = models.Attendees.objects.get(node_settings_id=nodeId, _id=_id)

        if not is_guest:
            webMeetingAppAttendee.fullname = OSFUser.objects.get(guids___id=webMeetingAppAttendee.user_guid).fullname

        if appName == settings.MICROSOFT_TEAMS:

            webMeetingAppAttendee.microsoft_teams_user_name = username
            webMeetingAppAttendee.microsoft_teams_mail = email
        elif appName == settings.WEBEX_MEETINGS:

            webMeetingAppAttendee.webex_meetings_display_name = username
            webMeetingAppAttendee.webex_meetings_mail = email

        webMeetingAppAttendee.save()
    else:

        if not is_guest:
            fullname = OSFUser.objects.get(guids___id=guid).fullname

            if appName == settings.MICROSOFT_TEAMS:

                if models.Attendees.objects.filter(node_settings_id=nodeId, user_guid=guid).exists():

                    webMeetingAppAttendeeInfo = models.Attendees.objects.get(node_settings_id=nodeId, user_guid=guid)
                    webMeetingAppAttendeeInfo.fullname = fullname
                    webMeetingAppAttendeeInfo.microsoft_teams_user_name = username
                    webMeetingAppAttendeeInfo.microsoft_teams_mail = email

                else:

                    webMeetingAppAttendeeInfo = models.Attendees(
                        user_guid=guid,
                        fullname=fullname,
                        is_guest=is_guest,
                        microsoft_teams_user_name=username,
                        microsoft_teams_mail=email,
                        node_settings=nodeSettings,
                    )

            elif appName == settings.WEBEX_MEETINGS:

                if models.Attendees.objects.filter(node_settings_id=nodeId, user_guid=guid).exists():

                    webMeetingAppAttendeeInfo = models.Attendees.objects.get(node_settings_id=nodeId, user_guid=guid)
                    webMeetingAppAttendeeInfo.fullname = fullname
                    webMeetingAppAttendeeInfo.webex_meetings_display_name = username
                    webMeetingAppAttendeeInfo.webex_meetings_mail = email

                else:

                    webMeetingAppAttendeeInfo = models.Attendees(
                        user_guid=guid,
                        fullname=fullname,
                        is_guest=is_guest,
                        webex_meetings_display_name=username,
                        webex_meetings_mail=email,
                        node_settings=nodeSettings,
                    )

        else:

            if appName == settings.MICROSOFT_TEAMS:

                webMeetingAppAttendeeInfo = models.Attendees(
                    user_guid=guid,
                    fullname=fullname,
                    is_guest=is_guest,
                    microsoft_teams_user_name=username,
                    microsoft_teams_mail=email,
                    node_settings=nodeSettings,
                )
            elif appName == settings.WEBEX_MEETINGS:

                webMeetingAppAttendeeInfo = models.Attendees(
                    user_guid=guid,
                    fullname=fullname,
                    is_guest=is_guest,
                    webex_meetings_display_name=username,
                    webex_meetings_mail=email,
                    node_settings=nodeSettings,
                )

        webMeetingAppAttendeeInfo.save()

    return {}

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_start_scenario(**kwargs):

    logger.info('integromat_start_scenario start')

    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    timestamp = requestDataJson['timestamp']

    webhook_url = requestDataJson['webhook_url']

    response = requests.post(webhook_url, data=request.get_data(), headers={'Content-Type': 'application/json'})

    logger.info('webhook response:' + str(response))
    logger.info('integromat_start_scenario end')

    return {
        'timestamp': timestamp
    }

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_req_next_msg(**kwargs):

    logger.info('integromat_req_next_msg start')

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    time.sleep(1)

    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    timestamp = requestDataJson['timestamp']
    nodeId = addon._id

    notify = False
    count = requestDataJson['count']

    integromatMsg = ''
    node = models.NodeSettings.objects.get(_id=nodeId)

    if count == settings.TIME_LIMIT_START_SCENARIO:
        notifyCnt = models.WorkflowExecutionMessages.objects.filter(node_settings_id=node.id, timestamp=timestamp).count()
        if not notifyCnt:
            integromatMsg = 'integromat.error.didNotStart'

    try:
        wem = models.WorkflowExecutionMessages.objects.filter(node_settings_id=node.id, timestamp=timestamp, notified=False).earliest('created')
        integromatMsg = wem.integromat_msg
        wem.notified = True
        wem.save()
    except ObjectDoesNotExist:
        pass

    if integromatMsg:
        notify = True

    return {
        'integromatMsg': integromatMsg,
        'timestamp': timestamp,
        'notify': notify,
        'count': count,
    }

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_register_alternative_webhook_url(**kwargs):

    logger.info('integromat_register_alternative_webhook_url start')

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    requestData = request.get_data()
    requestDataJson = json.loads(requestData)

    workflowDescription = requestDataJson['workflowDescription']
    alternativeWebhookUrl = requestDataJson['alternativeWebhookUrl']

    workflows = RdmWorkflows.objects.get(workflow_description=workflowDescription)

    with transaction.atomic():
        nodeWorkflow, created = models.NodeWorkflows.objects.update_or_create(node_settings_id=addon.id, workflow_id=workflows.id, defaults={'alternative_webhook_url': alternativeWebhookUrl})

    logger.info('integromat_register_alternative_webhook_url end')
    return {}

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_info_msg(**kwargs):

    logger.info('integromat_info_msg start')

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    nodeId = addon._id

    msg = request.json['notifyType']
    timestamp = request.json['timestamp']

    node = models.NodeSettings.objects.get(_id=nodeId)

    wem = models.WorkflowExecutionMessages(
        integromat_msg=msg,
        timestamp=timestamp,
        node_settings_id=node.id,
    )
    wem.save()

    logger.info('integromat_info_msg end')

    return {}

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def integromat_error_msg(**kwargs):

    logger.info('integromat_error_msg start')

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    nodeId = addon._id

    msg = request.json['notifyType']
    timestamp = request.json['timestamp']

    node = models.NodeSettings.objects.get(_id=nodeId)

    wem = models.WorkflowExecutionMessages(
        integromat_msg=msg,
        timestamp=timestamp,
        node_settings_id=node.id,
    )
    wem.save()

    logger.info('integromat_error_msg end')

    return {}

@must_be_valid_project
@must_have_permission(READ)
@must_have_addon(SHORT_NAME, 'node')
def integromat_get_meetings(**kwargs):

    logger.info('integromat_get_meetings start')

    node = kwargs['node'] or kwargs['project']

    addon = node.get_addon(SHORT_NAME)

    tz = pytz.timezone('utc')
    sToday = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    sYesterday = sToday + timedelta(days=-1)
    sTomorrow = sToday + timedelta(days=1)

    recentMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__gte=sYesterday, start_datetime__lt=sTomorrow + timedelta(days=1)).order_by('start_datetime')
    recentMeetingsJson = serializers.serialize('json', recentMeetings, ensure_ascii=False)
    recentMeetingsDict = json.loads(recentMeetingsJson)
    logger.info('integromat_get_meetings end')

    return {
        'recentMeetings': recentMeetingsDict,
    }
