# -*- coding: utf-8 -*-
from flask import request
import logging
import json
from addons.zoommeetings import SHORT_NAME
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.zoommeetings.serializer import ZoomMeetingsSerializer
from osf.models import ExternalAccount
from osf.utils.permissions import WRITE
from website.project.decorators import (
    must_have_addon,
    must_be_valid_project,
    must_have_permission,
)
from admin.rdm_addons.decorators import must_be_rdm_addons_allowed
from addons.zoommeetings import utils
from website.oauth.utils import get_service
logger = logging.getLogger(__name__)

zoommeetings_account_list = generic_views.account_list(
    SHORT_NAME,
    ZoomMeetingsSerializer
)

zoommeetings_get_config = generic_views.get_config(
    SHORT_NAME,
    ZoomMeetingsSerializer
)

zoommeetings_import_auth = generic_views.import_auth(
    SHORT_NAME,
    ZoomMeetingsSerializer
)

zoommeetings_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

@must_be_logged_in
@must_be_rdm_addons_allowed(SHORT_NAME)
def zoommeetings_oauth_connect(auth, **kwargs):

    provider = get_service(SHORT_NAME)
    authorization_url = provider.get_authorization_url(provider.client_id)

    return authorization_url

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def zoommeetings_request_api(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    requestData = request.get_data()
    requestDataJsonLoads = json.loads(requestData)
    action = requestDataJsonLoads['actionType']
    updateMeetingId = requestDataJsonLoads['updateMeetingId']
    deleteMeetingId = requestDataJsonLoads['deleteMeetingId']
    requestBody = requestDataJsonLoads['body']

    account = ExternalAccount.objects.get(
        provider='zoommeetings', id=account_id
    )
    if action == 'create':
        createdMeetings = utils.api_create_zoom_meeting(requestBody, account)
        #synchronize data
        utils.grdm_create_zoom_meeting(addon, account, createdMeetings)

    if action == 'update':
        utils.api_update_zoom_meeting(updateMeetingId, requestBody, account)
        #synchronize data
        utils.grdm_update_zoom_meeting(updateMeetingId, requestBody)

    if action == 'delete':
        utils.api_delete_zoom_meeting(deleteMeetingId, account)
        #synchronize data
        utils.grdm_delete_zoom_meeting(deleteMeetingId)
    return {}
