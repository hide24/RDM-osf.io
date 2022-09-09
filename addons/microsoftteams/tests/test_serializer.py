# -*- coding: utf-8 -*-
"""Serializer tests for the My MinIO addon."""
import mock
import pytest

from addons.base.tests.serializers import StorageAddonSerializerTestSuiteMixin
from addons.microsoftteams.tests.factories import MicrosoftTteamsAccountFactory
from addons.microsoftteams.serializer import MicrosoftTteamsSerializer

from tests.base import OsfTestCase

pytestmark = pytest.mark.django_db

class TestMicrosoftTteamsSerializer(StorageAddonSerializerTestSuiteMixin, OsfTestCase):
    addon_short_name = 'microsoftteams'
    Serializer = MicrosoftTteamsSerializer
    ExternalAccountFactory = MicrosoftTteamsAccountFactory

    def set_provider_id(self, pid):
        self.node_settings.folder_id = pid

    def setUp(self):
        super(TestMicrosoftTteamsSerializer, self).setUp()

    def tearDown(self):
        super(TestMicrosoftTteamsSerializer, self).tearDown()
