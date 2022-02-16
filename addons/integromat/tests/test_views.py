# -*- coding: utf-8 -*-
import mock
import pytest
import json
import addons.integromat.settings as integromat_settings

from nose.tools import (assert_equal, assert_equals,
    assert_true, assert_in, assert_false)
from rest_framework import status as http_status
from django.core import serializers
import requests
from framework.auth import Auth
from tests.base import OsfTestCase
from osf_tests.factories import ProjectFactory, AuthUserFactory, InstitutionFactory
from addons.base.tests.views import (
    OAuthAddonConfigViewsTestCaseMixin
)
from addons.integromat.tests.utils import IntegromatAddonTestCase
from website.util import api_url_for
from admin.rdm_addons.utils import get_rdm_addon_option
from datetime import date, datetime, timedelta
from dateutil import parser as date_parse
from addons.integromat.models import (
    UserSettings,
    NodeSettings,
    WorkflowExecutionMessages,
    Attendees,
    AllMeetingInformation,
    AllMeetingInformationAttendeesRelation,
    NodeWorkflows
)
from osf.models import ExternalAccount, OSFUser, RdmAddonOption
from addons.integromat.tests.factories import (
    IntegromatUserSettingsFactory,
    IntegromatNodeSettingsFactory,
    IntegromatAccountFactory,
    IntegromatAttendeesFactory,
    IntegromatWorkflowExecutionMessagesFactory,
    IntegromatAllMeetingInformationFactory,
    IntegromatAllMeetingInformationAttendeesRelationFactory,
    IntegromatNodeWorkflowsFactory
)

pytestmark = pytest.mark.django_db

class TestIntegromatViews(IntegromatAddonTestCase, OAuthAddonConfigViewsTestCaseMixin, OsfTestCase):
    def setUp(self):
        super(TestIntegromatViews, self).setUp()

    def tearDown(self):
        super(TestIntegromatViews, self).tearDown()

    @mock.patch('addons.integromat.views.authIntegromat')
    def test_integromat_settings_input_empty_access_key(self, mock_auth_integromat):
        mock_auth_integromat.return_value = {}

        institution = InstitutionFactory()
        self.user.affiliated_institutions.add(institution)
        self.user.save()
        rdm_addon_option = get_rdm_addon_option(institution.id, self.ADDON_SHORT_NAME)
        rdm_addon_option.is_allowed = True
        rdm_addon_option.save()

        url = self.project.api_url_for('integromat_add_user_account')
        rv = self.app.post_json(url, {
            'integromat_api_token': '',
        }, auth=self.user.auth, expect_errors=True)
        assert_equals(rv.status_int, http_status.HTTP_400_BAD_REQUEST)

    @mock.patch('addons.integromat.views.authIntegromat')
    def test_integromat_settings_rdm_addons_denied(self, mock_auth_integromat):
        mock_auth_integromat.return_value = {'id': '1234567890', 'name': 'integromat.user'}
        institution = InstitutionFactory()
        self.user.affiliated_institutions.add(institution)
        self.user.save()
        rdm_addon_option = get_rdm_addon_option(institution.id, self.ADDON_SHORT_NAME)
        rdm_addon_option.is_allowed = False
        rdm_addon_option.save()
        url = self.project.api_url_for('integromat_add_user_account')
        rv = self.app.post_json(url,{
            'integromat_api_token': 'aldkjf',
        }, auth=self.user.auth, expect_errors=True)
        assert_equal(rv.status_int, http_status.HTTP_403_FORBIDDEN)
        assert_in('You are prohibited from using this add-on.', rv.body.decode())

    def test_integromat_remove_node_settings_owner(self):
        url = self.node_settings.owner.api_url_for('integromat_deauthorize_node')
        self.app.delete(url, auth=self.user.auth)
        result = self.Serializer().serialize_settings(node_settings=self.node_settings, current_user=self.user)
        assert_equal(result['nodeHasAuth'], False)

    def test_integromat_remove_node_settings_unauthorized(self):
        url = self.node_settings.owner.api_url_for('integromat_deauthorize_node')
        ret = self.app.delete(url, auth=None, expect_errors=True)

        assert_equal(ret.status_code, 401)

    def test_integromat_get_node_settings_owner(self):
        self.node_settings.set_auth(self.external_account, self.user)
        self.node_settings.save()
        url = self.node_settings.owner.api_url_for('integromat_get_config')
        res = self.app.get(url, auth=self.user.auth)

        result = res.json['result']
        assert_equal(result['nodeHasAuth'], True)
        assert_equal(result['userIsOwner'], True)

    def test_integromat_get_node_settings_unauthorized(self):
        url = self.node_settings.owner.api_url_for('integromat_get_config')
        unauthorized = AuthUserFactory()
        ret = self.app.get(url, auth=unauthorized.auth, expect_errors=True)

        assert_equal(ret.status_code, 403)

    def test_integromat_api_call(self):
        url = self.project.api_url_for('integromat_api_call')

        res = self.app.get(url, auth=self.user.auth)
        resBodyJson = json.loads(res.body)
        assert_equals(self.user.username, resBodyJson['email'])

    def test_integromat_register_meeting_microsoft_teams(self):

        AttendeesFactory = IntegromatAttendeesFactory(node_settings=self.node_settings)
        url = self.project.api_url_for('integromat_register_meeting')

        app_name = 'MicrosoftTeams'

        expected_subject = 'Subject Test'
        expected_organizer = 'testUser3@test.onmicrosoft.com'
        expected_attendees = ['testUser1@test.onmicrosoft.com']
        expected_attendees_id = Attendees.objects.get(user_guid='testuser').id
        expected_startDatetime = datetime.now().isoformat()
        expected_endDatetime = (datetime.now() + timedelta(hours=1)).isoformat()
        expected_location = 'Location Test'
        expected_content = 'Content Test'
        expected_joinUrl = 'teams/microsoft.com/asd'
        expected_meetingId = '1234567890qwertyuiopasdfghjkl'
        expected_password = ''
        expected_meetingInviteesInfo = ''

        expected_startDatetime_format = date_parse.parse(expected_startDatetime).strftime('%Y/%m/%d %H:%M:%S')
        expected_endDatetime_format = date_parse.parse(expected_endDatetime).strftime('%Y/%m/%d %H:%M:%S')

        rv = self.app.post_json(url, {
            'appName': app_name,
            'subject': expected_subject,
            'organizer': expected_organizer,
            'attendees': expected_attendees,
            'startDatetime': expected_startDatetime,
            'endDatetime': expected_endDatetime,
            'location': expected_location,
            'content': expected_content,
            'joinUrl': expected_joinUrl,
            'meetingId': expected_meetingId,
            'password': expected_password,
            'meetingInviteesInfo': expected_meetingInviteesInfo,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)

        result = AllMeetingInformation.objects.get(meetingid='1234567890qwertyuiopasdfghjkl')

        assert_equals(result.subject, expected_subject)
        assert_equals(result.organizer, expected_organizer)
        assert_equals(result.organizer_fullname, expected_organizer)
        assert_equals(result.start_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_startDatetime_format)
        assert_equals(result.end_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_endDatetime_format)
        assert_equals(result.attendees.all()[0].id, expected_attendees_id)
        assert_equals(result.location, expected_location)
        assert_equals(result.content, expected_content)
        assert_equals(result.join_url, expected_joinUrl)
        assert_equals(result.meetingid, expected_meetingId)
        assert_equals(result.meeting_password, expected_password)
        assert_equals(rvBodyJson, {})

        expected_appId = 1639

        assert_equals(result.appid, expected_appId)
        assert_equals(result.node_settings.id, self.node_settings.id)

        rResult = AllMeetingInformationAttendeesRelation.objects.all()
        assert_equals(len(rResult), 0)
        #Attendees table clean
        Attendees.objects.all().delete()

    def test_integromat_update_meeting_registration_microsoft_teams(self):
        AttendeesFactory = IntegromatAttendeesFactory(node_settings=self.node_settings)
        AllMeetingInformationFactory = IntegromatAllMeetingInformationFactory(node_settings=self.node_settings)

        url = self.project.api_url_for('integromat_update_meeting_registration')

        app_name = 'MicrosoftTeams'

        expected_subject = 'Subject Test Update'
        expected_organizer = 'testUser1@test.onmicrosoft.com'
        expected_organizer_fullname = 'TEST USER'
        expected_attendees = ['testUser1@test.onmicrosoft.com']
        expected_attendees_id = Attendees.objects.get(user_guid='testuser').id
        expected_startDatetime = datetime.now().isoformat()
        expected_endDatetime = (datetime.now() + timedelta(hours=1)).isoformat()
        expected_location = 'Location Test Update'
        expected_content = 'Content Test Update'
        expected_meetingId = 'qwertyuiopasdfghjklzxcvbnm'
        expected_meetingCreatedInviteesInfo = ''
        expected_meetingDeletedInviteesInfo = ''
        expected_joinUrl = 'teams/microsoft.com/321'
        expected_password = ''

        expected_startDatetime_format = date_parse.parse(expected_startDatetime).strftime('%Y/%m/%d %H:%M:%S')
        expected_endDatetime_format = date_parse.parse(expected_endDatetime).strftime('%Y/%m/%d %H:%M:%S')

        rv = self.app.post_json(url, {
            'appName': app_name,
            'subject': expected_subject,
            'attendees': expected_attendees,
            'startDatetime': expected_startDatetime,
            'endDatetime': expected_endDatetime,
            'location': expected_location,
            'content': expected_content,
            'meetingId': expected_meetingId,
            'password': expected_password,
            'meetingCreatedInviteesInfo': expected_meetingCreatedInviteesInfo,
            'meetingDeletedInviteesInfo': expected_meetingDeletedInviteesInfo,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)

        result = AllMeetingInformation.objects.get(meetingid='qwertyuiopasdfghjklzxcvbnm')

        assert_equals(result.subject, expected_subject)
        assert_equals(result.organizer, expected_organizer)
        assert_equals(result.organizer_fullname, expected_organizer_fullname)
        assert_equals(result.start_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_startDatetime_format)
        assert_equals(result.end_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_endDatetime_format)
        assert_equals(result.attendees.all()[0].id, expected_attendees_id)
        assert_equals(result.location, expected_location)
        assert_equals(result.content, expected_content)
        assert_equals(result.join_url, expected_joinUrl)
        assert_equals(result.meetingid, expected_meetingId)
        assert_equals(result.meeting_password, expected_password)
        assert_equals(rvBodyJson, {})


        expected_appId = 1639

        assert_equals(result.appid, expected_appId)
        assert_equals(result.node_settings.id, self.node_settings.id)

        rResult = AllMeetingInformationAttendeesRelation.objects.all()
        assert_equals(len(rResult), 0)
        #clear
        Attendees.objects.all().delete()
        AllMeetingInformation.objects.all().delete()

    def test_integromat_delete_meeting_registration(self):

        AllMeetingInformationFactory = IntegromatAllMeetingInformationFactory(node_settings=self.node_settings)

        url = self.project.api_url_for('integromat_delete_meeting_registration')

        meetingId = 'qwertyuiopasdfghjklzxcvbnm'

        rv = self.app.post_json(url, {
            'meetingId': meetingId,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)

        result = AllMeetingInformation.objects.filter(meetingid='qwertyuiopasdfghjklzxcvbnm')

        assert_equals(result.count(), 0)
        assert_equals(rvBodyJson, {})
        #clear
        AllMeetingInformation.objects.all().delete()

    def test_integromat_get_meetings(self):
        AllMeetingInformationFactory = IntegromatAllMeetingInformationFactory(node_settings=self.node_settings)

        url = self.project.api_url_for('integromat_get_meetings')

        res = self.app.get(url, auth=self.user.auth)
        resBodyJson = json.loads(res.body)
        expectedQuery = AllMeetingInformation.objects.all()
        expectedJson = json.loads(serializers.serialize('json', expectedQuery, ensure_ascii=False))

        assert_equals(len(resBodyJson), 1)
        assert_equals(resBodyJson['recentMeetings'], expectedJson)
        #clear
        AllMeetingInformation.objects.all().delete()

    def test_integromat_register_web_meeting_apps_email_register(self):

        AllMeetingInformationFactory = IntegromatAllMeetingInformationFactory(node_settings=self.node_settings)

        osfUser = OSFUser.objects.get(username=self.user.username)
        osfGuids = osfUser._prefetched_objects_cache['guids'].only()
        osfGuidsSerializer = serializers.serialize('json', osfGuids, ensure_ascii=False)
        osfGuidsJson = json.loads(osfGuidsSerializer)
        osfUserGuid = osfGuidsJson[0]['fields']['_id']
        url = self.project.api_url_for('integromat_register_web_meeting_apps_email')

        _id = None
        expected_guid = osfUserGuid
        appName = 'MicrosoftTeams'
        expected_email = 'testUser4@test.onmicrosoft.com'
        expected_username = 'Teams User4'
        expected_is_guest = False
        expected_fullname = osfUser.fullname

        rv = self.app.post_json(url, {
            '_id': _id,
            'appName': appName,
            'guid': expected_guid,
            'email': expected_email,
            'fullname': expected_fullname,
            'username': expected_username,
            'is_guest': expected_is_guest,
        }, auth=self.user.auth)

        rvBodyJson = json.loads(rv.body)

        result = Attendees.objects.get(user_guid=osfUserGuid)

        assert_equals(result.fullname, expected_fullname)
        assert_equals(result.microsoft_teams_mail, expected_email)
        assert_equals(result.microsoft_teams_user_name, expected_username)
        assert_equals(result.webex_meetings_mail, None)
        assert_equals(result.webex_meetings_display_name, None)
        assert_equals(result.is_guest, expected_is_guest)
        assert_equals(rvBodyJson, {})
        #clear
        OSFUser.objects.all().delete()
        AllMeetingInformation.objects.all().delete()

    def test_integromat_register_web_meeting_apps_email_update(self):

        AllMeetingInformationFactory = IntegromatAllMeetingInformationFactory(node_settings=self.node_settings)

        osfUser = OSFUser.objects.get(username=self.user.username)
        osfGuids = osfUser._prefetched_objects_cache['guids'].only()
        osfGuidsSerializer = serializers.serialize('json', osfGuids, ensure_ascii=False)
        osfGuidsJson = json.loads(osfGuidsSerializer)
        osfUserGuid = osfGuidsJson[0]['fields']['_id']

        url = self.project.api_url_for('integromat_register_web_meeting_apps_email')

        _id = '1234567890qwertyuiop'
        expected_guid = osfUserGuid
        appName = 'MicrosoftTeams'
        expected_email = 'testUser4update@test.onmicrosoft.com'
        expected_username = 'Teams User4 update'
        expected_is_guest = False
        expected_fullname = osfUser.fullname

        rv = self.app.post_json(url, {
            '_id': _id,
            'appName': appName,
            'guid': expected_guid,
            'email': expected_email,
            'fullname': expected_fullname,
            'username': expected_username,
            'is_guest': expected_is_guest,
        }, auth=self.user.auth)

        result = Attendees.objects.get(user_guid=osfUserGuid)

        assert_equals(result.fullname, expected_fullname)
        assert_equals(result.microsoft_teams_mail, expected_email)
        assert_equals(result.microsoft_teams_user_name, expected_username)
        assert_equals(result.webex_meetings_mail, None)
        assert_equals(result.webex_meetings_display_name, None)
        assert_equals(result.is_guest, expected_is_guest)
        #clear
        OSFUser.objects.all().delete()
        AllMeetingInformation.objects.all().delete()

    def test_integromat_register_web_meeting_apps_email_guest_update(self):
        url = self.project.api_url_for('integromat_register_web_meeting_apps_email')

        _id = '0987654321poiuytrewq'
        appName = 'MicrosoftTeams'
        fullname = 'Guest User2'
        origin_email = 'testUser5@guest.com'
        origin_username = 'Teams Guest User5'
        origin_is_guest = True
        expected_fullname = ''

        AttendeesFactory = IntegromatAttendeesFactory(
            _id=_id,
            user_guid = 'guest_1234567890',
            fullname=fullname,
            microsoft_teams_mail=origin_email,
            microsoft_teams_user_name=origin_username,
            is_guest=origin_is_guest,
            node_settings=self.node_settings,
        )

        expected_email = 'testUser5Update@guest.com'
        expected_username = 'Teams Guest User5 Update'
        expected_webex_meetings_mail = 'testUser2@test.co.jp'
        expected_webex_meetings_display_name = 'Webex User'
        expected_is_guest = True

        rv = self.app.post_json(url, {
            '_id': _id,
            'appName': appName,
            'guid': None,
            'email': expected_email,
            'fullname': expected_fullname,
            'username': expected_username,
            'is_guest': expected_is_guest,
        }, auth=self.user.auth)

        result = Attendees.objects.get(_id=_id)
        expected_fullname = Attendees.objects.get(_id=_id).fullname

        assert_equals(result.fullname, expected_fullname)
        assert_equals(result.microsoft_teams_mail, expected_email)
        assert_equals(result.microsoft_teams_user_name, expected_username)
        assert_equals(result.webex_meetings_mail, expected_webex_meetings_mail)
        assert_equals(result.webex_meetings_display_name, expected_webex_meetings_display_name)
        assert_equals(result.is_guest, expected_is_guest)

    def test_integromat_req_next_msg(self):

        WorkflowExecutionMessage = IntegromatWorkflowExecutionMessagesFactory(node_settings=self.node_settings)

        url = self.project.api_url_for('integromat_req_next_msg')

        expected_timestamp = '1234567890123'
        count = 1
        expected_integromatMsg = 'integromat.info.message'

        rv = self.app.post_json(url, {
            'timestamp': expected_timestamp,
            'count': count,
        }, auth=self.user.auth)

        rvBodyJson = json.loads(rv.body)

        assert_equals(rvBodyJson['integromatMsg'], expected_integromatMsg)
        assert_equals(rvBodyJson['timestamp'], expected_timestamp)
        assert_equals(rvBodyJson['notify'], True)
        assert_equals(rvBodyJson['count'], count)
        #clear
        WorkflowExecutionMessages.objects.all().delete()

    def test_integromat_req_next_msg_scenario_did_not_start(self):
        url = self.project.api_url_for('integromat_req_next_msg')

        expected_timestamp = '1234567890123'
        count = 15
        expected_integromatMsg = 'integromat.error.didNotStart'

        rv = self.app.post_json(url, {
            'timestamp': expected_timestamp,
            'count': count,
        }, auth=self.user.auth)

        rvBodyJson = json.loads(rv.body)

        assert_equals(rvBodyJson['integromatMsg'], expected_integromatMsg)
        assert_equals(rvBodyJson['timestamp'], expected_timestamp)
        assert_equals(rvBodyJson['notify'], True)
        assert_equals(rvBodyJson['count'], count)

    def test_integromat_info_msg(self):
        WorkflowExecutionMessage = IntegromatWorkflowExecutionMessagesFactory()
        url = self.project.api_url_for('integromat_info_msg')

        expected_notifyType = 'integromat.info.notify'
        expected_timestamp = '0987654321098'

        rv = self.app.post_json(url, {
            'notifyType': expected_notifyType,
            'timestamp': expected_timestamp,
        }, auth=self.user.auth)

        result = WorkflowExecutionMessages.objects.get(timestamp='0987654321098')

        assert_equals(result.integromat_msg, expected_notifyType)
        assert_equals(result.timestamp, expected_timestamp)
        #clear
        WorkflowExecutionMessages.objects.all().delete()

    def test_integromat_error_msg(self):
        WorkflowExecutionMessage = IntegromatWorkflowExecutionMessagesFactory()
        url = self.project.api_url_for('integromat_error_msg')

        expected_notifyType = 'integromat.error.notify'
        expected_timestamp = '6789012345678'

        rv = self.app.post_json(url, {
            'notifyType': expected_notifyType,
            'timestamp': expected_timestamp,
        }, auth=self.user.auth)

        result = WorkflowExecutionMessages.objects.get(timestamp='6789012345678')

        assert_equals(result.integromat_msg, expected_notifyType)
        assert_equals(result.timestamp, expected_timestamp)
        #clear
        WorkflowExecutionMessages.objects.all().delete()

    def test_integromat_register_alternative_webhook_url(self):

        url = self.project.api_url_for('integromat_register_alternative_webhook_url')

        workflowDescription = 'integromat.workflows.web_meeting.description'
        expected_alternativeWebhookUrl = 'https://hook.integromat.com/test'

        rv = self.app.post_json(url, {
            'workflowDescription': workflowDescription,
            'alternativeWebhookUrl': expected_alternativeWebhookUrl,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)
        workflowId = 7895
        result = NodeWorkflows.objects.get(node_settings_id=self.node_settings.id, workflowid=workflowId)

        assert_equals(result.alternative_webhook_url, expected_alternativeWebhookUrl)
        assert_equals(rvBodyJson, {})

    @mock.patch('addons.integromat.views.requests')
    def test_integromat_start_scenario_the_user_attendee_unregistered(self, mock_requests):

        mock_requests.post.return_value.status_code = 200

        email = self.user.username
        url = self.project.api_url_for('integromat_start_scenario')

        expectedTimestamp = '6789012345678'
        appName = 'ZoomMeetings'
        expecitedAttendee = [email]
        webhookUrl = 'https://hook.integromat.com/test'

        rv = self.app.post_json(url, {
            'timestamp': expectedTimestamp,
            'appName': appName,
            'attendees': expecitedAttendee,
            'webhookUrl': webhookUrl,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)
        result = Attendees.objects.get(node_settings_id=self.node_settings.id, zoom_meetings_mail=attendee[0])
        assert_equals(result.zoom_meetings_mail, expecitedAttendee[0])
        assert_equals(rvBodyJson['timestamp'], expectedTimestamp)

    @mock.patch('addons.integromat.views.requests')
    def test_integromat_start_scenario_the_zoom_attendee_unregistered(self, mock_requests):

        mock_requests.post.return_value.status_code = 200

        AttendeesFactory = IntegromatAttendeesFactory(node_settings=self.node_settings, zoom_meetings_email='')
        url = self.project.api_url_for('integromat_start_scenario')

        email = self.user.username
        expectedTimestamp = '6789012345678'
        appName = 'ZoomMeetings'
        expecitedAttendee = [email]
        webhookUrl = 'https://hook.integromat.com/test'

        rv = self.app.post_json(url, {
            'timestamp': expectedTimestamp,
            'appName': appName,
            'attendees': expecitedAttendee,
            'webhookUrl': webhookUrl,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)
        result = Attendees.objects.get(node_settings_id=self.node_settings.id, zoom_meetings_mail=attendee[0])
        assert_equals(result.zoom_meetings_mail, expecitedAttendee[0])
        assert_equals(rvBodyJson['timestamp'], expectedTimestamp)

    @mock.patch('addons.integromat.views.requests')
    def test_integromat_start_scenario_zoom_attendee_exist(self, mock_requests):

        mock_requests.post.return_value.status_code = 200

        email = self.user.username
        AttendeesFactory = IntegromatAttendeesFactory(node_settings=self.node_settings, zoom_meetings_email=email)

        url = self.project.api_url_for('integromat_start_scenario')

        rv = self.app.post_json(url, {
            'timestamp': '1234567890',
            'appName': 'ZoomMeetings',
            'attendees': 'testuser@example.com',
            'webhookUrl': 'https://hook.integromat.com/test',
        }, auth=self.user.auth)

        rvBodyJson = json.loads(rv.body)
        workflowId = 7895
        result = NodeWorkflows.objects.get(node_settings_id=self.node_settings.id, workflowid=workflowId)

        assert_equals(result.alternative_webhook_url, expected_alternativeWebhookUrl)
        assert_equals(rvBodyJson['timestamp'], )

    ## Overrides ##

    def test_folder_list(self):
        pass

    def test_set_config(self):
        pass

    def test_import_auth(self):

        institution = InstitutionFactory()
        self.user.affiliated_institutions.add(institution)
        self.user.save()
        rdm_addon_option = get_rdm_addon_option(institution.id, self.ADDON_SHORT_NAME)
        rdm_addon_option.is_allowed = True
        rdm_addon_option.save()

        ea = self.ExternalAccountFactory()
        self.user.external_accounts.add(ea)
        self.user.save()

        node = ProjectFactory(creator=self.user)
        node_settings = node.get_or_add_addon(self.ADDON_SHORT_NAME, auth=Auth(self.user))
        node.save()
        url = node.api_url_for('{0}_import_auth'.format(self.ADDON_SHORT_NAME))
        res = self.app.put_json(url, {
            'external_account_id': ea._id
        }, auth=self.user.auth)
        assert_equal(res.status_code, http_status.HTTP_200_OK)
        assert_in('result', res.json)
        node_settings.reload()
        assert_equal(node_settings.external_account._id, ea._id)

        node.reload()
        last_log = node.logs.latest()
        assert_equal(last_log.action, '{0}_node_authorized'.format(self.ADDON_SHORT_NAME))
