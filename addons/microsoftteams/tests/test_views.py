# -*- coding: utf-8 -*-
import mock
import pytest
import json
import addons.microsoftteams.settings as microsoftteams_settings

from nose.tools import (assert_equal, assert_equals,
    assert_true, assert_in, assert_false)
from rest_framework import status as http_status
from django.core import serializers
import requests
from framework.auth import Auth
from tests.base import OsfTestCase
from osf_tests.factories import ProjectFactory, AuthUserFactory, InstitutionFactory, CommentFactory
from addons.base.tests.views import (
    OAuthAddonConfigViewsTestCaseMixin
)
from addons.microsoftteams.tests.utils import MicrosoftTeamsAddonTestCase, MockResponse
from website.util import api_url_for
from admin.rdm_addons.utils import get_rdm_addon_option
from datetime import date, datetime, timedelta
from dateutil import parser as date_parse
from addons.microsoftteams.models import (
    UserSettings,
    NodeSettings,
    Attendees,
    Meetings
)
from osf.models import ExternalAccount, OSFUser, RdmAddonOption, BaseFileNode, AbstractNode, Comment
from addons.microsoftteams.tests.factories import (
    MicrosoftTeamsUserSettingsFactory,
    MicrosoftTeamsNodeSettingsFactory,
    MicrosoftTeamsAccountFactory,
    MicrosoftTeamsAttendeesFactory,
    MicrosoftTeamsMeetingsFactory
)
from api_tests import utils as api_utils

pytestmark = pytest.mark.django_db

class TestMicrosoftTeamsViews(MicrosoftTeamsAddonTestCase, OAuthAddonConfigViewsTestCaseMixin, OsfTestCase):
    def setUp(self):
        super(TestMicrosoftTeamsViews, self).setUp()

    def tearDown(self):
        super(TestMicrosoftTeamsViews, self).tearDown()

    def test_microsoftteams_remove_node_settings_owner(self):
        url = self.node_settings.owner.api_url_for('microsoftteams_deauthorize_node')
        self.app.delete(url, auth=self.user.auth)
        result = self.Serializer().serialize_settings(node_settings=self.node_settings, current_user=self.user)
        assert_equal(result['nodeHasAuth'], False)

    def test_microsoftteams_remove_node_settings_unauthorized(self):
        url = self.node_settings.owner.api_url_for('microsoftteams_deauthorize_node')
        ret = self.app.delete(url, auth=None, expect_errors=True)

        assert_equal(ret.status_code, 401)

    def test_microsoftteams_get_node_settings_owner(self):
        self.node_settings.set_auth(self.external_account, self.user)
        self.node_settings.save()
        url = self.node_settings.owner.api_url_for('microsoftteams_get_config')
        res = self.app.get(url, auth=self.user.auth)

        result = res.json['result']
        assert_equal(result['nodeHasAuth'], True)
        assert_equal(result['userIsOwner'], True)

    def test_microsoftteams_get_node_settings_unauthorized(self):
        url = self.node_settings.owner.api_url_for('microsoftteams_get_config')
        unauthorized = AuthUserFactory()
        ret = self.app.get(url, auth=unauthorized.auth, expect_errors=True)

        assert_equal(ret.status_code, 403)

    @mock.patch('addons.microsoftteams.utils.api_create_teams_meeting')
    def test_microsoftteams_request_api_create(self, mock_api_create_teams_meeting):

        url = self.project.api_url_for('microsoftteams_request_api')

        expected_action = 'create'
        expected_UpdateMeetinId = ''
        expected_DeleteMeetinId = ''

        expected_subject = 'My Test Meeting'
        expected_attendees_id = Attendees.objects.get(user_guid='teamstestuser').id
        expected_attendees = {
                    'emailAddress': {
                        'address': 'teamstestuser1@test.onmicrosoft.com',
                        'name': 'Teams Test User1'
                    }
                }
        expected_startDatetime = datetime.now().isoformat()
        expected_endDatetime = (datetime.now() + timedelta(hours=1)).isoformat()
        expected_content = 'My Test Content'
        expected_contentExtract = expected_content
        expected_joinUrl = 'teams/microsoft.com/asd'
        expected_meetingId = '1234567890qwertyuiopasdfghjkl'
        expected_body = {
                'subject': expected_subject,
                'start': {
                    'dateTime': expected_startDatetime,
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': expected_endDatetime,
                    'timeZone': 'Asia/Tokyo',
                },
                'body': {
                    'contentType': 'HTML',
                    'content': expected_content,
                },
                'attendees': expected_attendees,
                'isOnlineMeeting': True,
            };
        expected_guestOrNot =={'testuser1@test.onmicrosoft.com': False}

        mock_api_create_teams_meeting.return_value = {
            'id': expected_meetingId,
            'subject': expected_subject,
            'start': {
                'dateTime': expected_startDatetime,
                'timeZone': 'Asia/Tokyo'
            },
            'end': {
                'dateTime': expected_endDatetime,
                'timeZone': 'Asia/Tokyo'
            },
            'attendees': [expected_attendees],
            'bodyPreview': expected_content,
            'organizer': {
                'emailAddress': {
                    'name': 'Teams Test User1',
                    'address': 'teamstestorganizer@test.onmicrosoft.com',
                }
            },
            'onlineMeeting': {
                'joinUrl': expected_joinUrl
            }
        }

        rv = self.app.post_json(url, {
            'action': expected_action,
            'updateMeetingId': expected_UpdateMeetinId,
            'deleteMeetingId': expected_DeleteMeetinId,
            'contentExtract': expected_contentExtract,
            'body': expected_body,
            'guestOrNot': expected_guestOrNot,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)

        result = Meetings.objects.get(meetingid=expected_meetingId)

        expected_startDatetime_format = date_parse.parse(expected_startDatetime).strftime('%Y/%m/%d %H:%M:%S')
        expected_endDatetime_format = date_parse.parse(expected_endDatetime).strftime('%Y/%m/%d %H:%M:%S')

        assert_equals(result.subject, expected_subject)
        assert_equals(result.organizer, expected_organizer)
        assert_equals(result.organizer_fullname, expected_organizer)
        assert_equals(result.start_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_startDatetime_format)
        assert_equals(result.end_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_endDatetime_format)
        assert_equals(result.attendees.all()[0].id, expected_attendees_id)
        assert_equals(result.content, expected_content)
        assert_equals(result.join_url, expected_joinUrl)
        assert_equals(result.meetingid, expected_meetingId)
        assert_equals(result.app_name, microsoftteams_settings.MICROSOFT_TEAMS)
        assert_equals(result.external_account.id, self.account.id)
        assert_equals(result.node_settings.id, self.node_settings.id)
        assert_equals(rvBodyJson, {})

    @mock.patch('addons.microsoftteams.utils.api_update_teams_meeting')
    def test_microsoftteams_request_api_update(self, mock_api_update_teams_meeting):

        updateEmailAddress = 'teamstestuser2@test.onmicrosoft.com'
        updateDisplayName = 'Teams Test User2'

        AttendeesFactory2 = MicrosoftTeamsAttendeesFactory(node_settings=self.node_settings, user_guid='teamstestuser2', fullname='TEAMS TEST USER 2', email_address=updateEmailAddress, display_name=updateDisplayName)
        MeetingsFactory = MicrosoftTeamsMeetingsFactory(node_settings=self.node_settings)

        url = self.project.api_url_for('microsoftteams_request_api')

        expected_action = 'update'
        expected_UpdateMeetinId = 'qwertyuiopasdfghjklzxcvbnm'
        expected_DeleteMeetinId = ''

        expected_subject = 'My Test Meeting EDIT'
        expected_attendees_id = Attendees.objects.get(user_guid='teamstestuser').id
        expected_attendees = {
                    'emailAddress': {
                        'address': 'teamstestuser1@test.onmicrosoft.com',
                        'name': 'Teams Test User1'
                    },
                    'emailAddress': {
                        'address': updateEmailAddress,
                        'name': updateDisplayName
                    },
                }
        expected_startDatetime = datetime.now().isoformat()
        expected_endDatetime = (datetime.now() + timedelta(hours=1)).isoformat()
        expected_content = 'My Test Content EDIT'
        expected_contentExtract = expected_content
        expected_joinUrl = 'teams/microsoft.com/321'
        expected_meetingId = '1234567890qwertyuiopasdfghjkl'
        expected_body = {
                'subject': expected_subject,
                start: {
                    dateTime: expected_startDatetime,
                    timeZone: 'Asia/Tokyo',
                },
                end: {
                    dateTime: expected_endDatetime,
                    timeZone: 'Asia/Tokyo',
                },
                body: {
                    contentType: 'HTML',
                    content: expected_content,
                },
                attendees: expected_attendees,
                isOnlineMeeting: True,
            };
        expected_guestOrNot =={'testuser1@test.onmicrosoft.com': False, updateEmailAddress: False}

        mock_api_update_teams_meeting.return_value = {
            'id': expected_meetingId,
            'subject': expected_subject,
            'start': {
                'dateTime': expected_startDatetime,
                'timeZone': 'Asia/Tokyo'
            },
            'end': {
                'dateTime': expected_endDatetime,
                'timeZone': 'Asia/Tokyo'
            },
            'attendees': [expected_attendees],
            'bodyPreview': expected_content,
            'organizer': {
                'emailAddress': {
                    'name': 'Teams Test User1',
                    'address': 'teamstestorganizer@test.onmicrosoft.com',
                },
                'emailAddress': {
                    'name': updateDisplayName,
                    'address': updateEmailAddress,
                }
            },
            'onlineMeeting': {
                'joinUrl': expected_joinUrl
            }
        }

        rv = self.app.post_json(url, {
            'action': expected_action,
            'updateMeetingId': expected_UpdateMeetinId,
            'deleteMeetingId': expected_DeleteMeetinId,
            'contentExtract': expected_contentExtract,
            'body': expected_body,
            'guestOrNot': expected_guestOrNot,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)

        result = Meetings.objects.get(meetingid=expected_meetingId)

        expected_startDatetime_format = date_parse.parse(expected_startDatetime).strftime('%Y/%m/%d %H:%M:%S')
        expected_endDatetime_format = date_parse.parse(expected_endDatetime).strftime('%Y/%m/%d %H:%M:%S')

        assert_equals(result.subject, expected_subject)
        assert_equals(result.organizer, expected_organizer)
        assert_equals(result.organizer_fullname, expected_organizer)
        assert_equals(result.start_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_startDatetime_format)
        assert_equals(result.end_datetime.strftime('%Y/%m/%d %H:%M:%S'), expected_endDatetime_format)
        assert_equals(result.attendees.all()[0].id, expected_attendees_id)
        assert_equals(result.content, expected_content)
        assert_equals(result.join_url, expected_joinUrl)
        assert_equals(result.meetingid, expected_meetingId)
        assert_equals(result.app_name, microsoftteams_settings.MICROSOFT_TEAMS)
        assert_equals(result.external_account.id, self.account.id)
        assert_equals(result.node_settings.id, self.node_settings.id)
        assert_equals(rvBodyJson, {})

    @mock.patch('addons.microsoftteams.utils.api_delete_teams_meeting')
    def test_microsoftteams_request_api_delete(self, mock_api_delete_teams_meeting):

        mock_api_update_teams_meeting.return_value = {}

        expected_action = 'delete'
        MeetingsFactory = MicrosoftTeamsMeetingsFactory(node_settings=self.node_settings)

        url = self.project.api_url_for('microsoftteams_request_api')

        expected_DeleteMeetinId = 'qwertyuiopasdfghjklzxcvbnm'

        rv = self.app.post_json(url, {
            'action': expected_action,
            'deleteMeetingId': expected_DeleteMeetinId,
        }, auth=self.user.auth)
        rvBodyJson = json.loads(rv.body)

        result = Meetings.objects.filter(meetingid=expected_DeleteMeetinId)

        assert_equals(result.count(), 0)
        assert_equals(rvBodyJson, {})

    @mock.patch('addons.microsoftteams.utils.api_get_microsoft_username')
    def test_microsoftteams_register_email_create(self, mock_api_get_microsoft_username):
        mock_api_get_microsoft_username.return_value = 'Teams Test User A'
        self.node_settings.set_auth(self.external_account, self.user)
        self.node_settings.save()

        osfUser = OSFUser.objects.get(username=self.user.username)
        osfGuids = osfUser._prefetched_objects_cache['guids'].only()
        osfGuidsSerializer = serializers.serialize('json', osfGuids, ensure_ascii=False)
        osfGuidsJson = json.loads(osfGuidsSerializer)
        osfUserGuid = osfGuidsJson[0]['fields']['_id']
        url = self.project.api_url_for('microsoftteams_register_email')

        _id = None
        expected_guid = osfUserGuid
        expected_email = 'teamstestusera@test.onmicrosoft.com'
        expected_username = mock_api_get_microsoft_username.return_value
        expected_is_guest = False
        expected_fullname = osfUser.fullname
        expected_actionType = 'create'
        expected_emailType = 'radio_signInAddress'

        rv = self.app.post_json(url, {
            '_id': _id,
            'guid': expected_guid,
            'email': expected_email,
            'fullname': expected_fullname,
            'is_guest': expected_is_guest,
            'actionType': expected_actionType,
            'emailType': expected_emailType
        }, auth=self.user.auth)

        rvBodyJson = json.loads(rv.body)

        result = Attendees.objects.get(user_guid=osfUserGuid)

        assert_equals(result.user_guid, expected_guid)
        assert_equals(result.fullname, expected_fullname)
        assert_equals(result.email_address, expected_email)
        assert_equals(result.display_name, expected_username)
        assert_equals(result.is_guest, expected_is_guest)
        assert_equals(result.external_account.id, self.account.id)
        assert_equals(result.node_settings.id, self.node_settings.id)
        assert_equals(rvBodyJson, {})

    @mock.patch('addons.microsoftteams.utils.api_get_microsoft_username')
    def test_microsoftteams_register_email_update(self, mock_api_get_microsoft_username):
        mock_api_get_microsoft_username.return_value = 'Teams Test User B EDIT'
        self.node_settings.set_auth(self.external_account, self.user)
        self.node_settings.save()

        expected_id = '1234567890qwertyuiop'
        expected_guid = 'teamstestuser'
        expected_email = 'teamstestuserbedit@test.onmicrosoft.com'
        expected_username = mock_api_update_teams_meeting.return_value
        expected_is_guest = False
        expected_fullname = 'TEST RDM USER'
        expected_actionType = 'update'
        expected_emailType = 'radio_signInAddress'

        rv = self.app.post_json(url, {
            '_id': expected_id,
            'guid': expected_guid,
            'email': expected_email,
            'is_guest': expected_is_guest,
            'actionType': expected_actionType,
            'emailType': expected_emailType
        }, auth=self.user.auth)

        rvBodyJson = json.loads(rv.body)

        result = Attendees.objects.get(user_guid=expected_guid)

        assert_equals(result.user_guid, expected_guid)
        assert_equals(result.fullname, expected_fullname)
        assert_equals(result.email_address, expected_email)
        assert_equals(result.display_name, expected_username)
        assert_equals(result.is_guest, expected_is_guest)
        assert_equals(result.external_account.id, self.account.id)
        assert_equals(result.node_settings.id, self.node_settings.id)
        assert_equals(rvBodyJson, {})

    def test_microsoftteams_register_email_delete(self):

        self.node_settings.set_auth(self.external_account, self.user)
        self.node_settings.save()
        url = self.project.api_url_for('microsoftteams_register_email')

        expected_id = '1234567890qwertyuiop'

        rv = self.app.post_json(url, {
            '_id': expected_id,
        }, auth=self.user.auth)

        rvBodyJson = json.loads(rv.body)

        result = models.Attendees.objects.get(node_settings_id=self.node_settings.id, expected_id=_id)

        assert_equals(result.count(), 0)
        assert_equals(rvBodyJson, {})

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
