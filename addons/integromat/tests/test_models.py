# from nose.tools import *  # noqa
import unittest
import json
import mock
import pytest
from nose.tools import (assert_false, assert_true,
                        assert_equal, assert_is_none)

from addons.base.tests.models import (
    OAuthAddonNodeSettingsTestSuiteMixin,
    OAuthAddonUserSettingTestSuiteMixin
)
from addons.integromat import SHORT_NAME, FULL_NAME
from addons.integromat import settings
from addons.integromat.models import NodeSettings, Attendees
from addons.integromat.tests.factories import (
    IntegromatUserSettingsFactory,
    IntegromatNodeSettingsFactory,
    IntegromatAccountFactory,
    IntegromatAttendeesFactory
)
from framework.auth import Auth
from osf_tests.factories import ProjectFactory, DraftRegistrationFactory
from tests.base import get_default_metaschema
from django.core import serializers
pytestmark = pytest.mark.django_db


class TestUserSettings(OAuthAddonUserSettingTestSuiteMixin, unittest.TestCase):

    short_name = SHORT_NAME
    full_name = FULL_NAME
    ExternalAccountFactory = IntegromatAccountFactory


class TestNodeSettings(OAuthAddonNodeSettingsTestSuiteMixin, unittest.TestCase):

    short_name = SHORT_NAME
    full_name = FULL_NAME
    ExternalAccountFactory = IntegromatAccountFactory
    NodeSettingsFactory = IntegromatNodeSettingsFactory
    NodeSettingsClass = NodeSettings
    UserSettingsFactory = IntegromatUserSettingsFactory

    def test_registration_settings(self):
        registration = ProjectFactory()
        clone, message = self.node_settings.after_register(
            self.node, registration, self.user,
        )
        assert_is_none(clone)

    def test_before_register_no_settings(self):
        self.node_settings.user_settings = None
        message = self.node_settings.before_register(self.node, self.user)
        assert_false(message)

    def test_before_register_no_auth(self):
        self.node_settings.external_account = None
        message = self.node_settings.before_register(self.node, self.user)
        assert_false(message)

    def test_before_register_settings_and_auth(self):
        message = self.node_settings.before_register(self.node, self.user)
        assert_true(message)

    ## Overrides ##

    def test_set_folder(self):
        pass

    def test_serialize_credentials(self):
        pass

    def test_serialize_credentials_not_authorized(self):
        pass

    def test_serialize_settings(self):
        pass

    def test_serialize_settings_not_configured(self):
        pass

    def test_create_log(self):
        pass



@pytest.mark.django_db
def test_default_guest_user_guid():
    inst = IntegromatAttendeesFactory(fullname='TEST USER', is_guest=True)
    result = Attendees.objects.filter(fullname='TEST USER')
    rJson = serializers.serialize('json', result, ensure_ascii=False)
    rDict = json.loads(rJson)
    expected_user_guid = None
    expected_microsoft_teams_mail = None
    expected_webex_meetings_mail = None
    assert_equal(rDict[0]['fields']['user_guid'], expected_user_guid)
    assert_equal(rDict[0]['fields']['microsoft_teams_user_name'], expected_webex_meetings_mail)
    assert_equal(rDict[0]['fields']['webex_meetings_mail'], expected_webex_meetings_mail)
