# -*- coding: utf-8 -*-
"""Serializer tests for the My MinIO addon."""
import mock
import pytest

from addons.base.tests.serializers import StorageAddonSerializerTestSuiteMixin
from addons.microsoftteams.tests.factories import MicrosofTteamsAccountFactory
from addons.microsoftteams.serializer import MicrosofTteamsSerializer

from tests.base import OsfTestCase

pytestmark = pytest.mark.django_db

class TestMicrosofTteamsSerializer(StorageAddonSerializerTestSuiteMixin, OsfTestCase):
    addon_short_name = 'microsoftteams'
    Serializer = MicrosofTteamsSerializer
    ExternalAccountFactory = MicrosofTteamsAccountFactory

    def set_provider_id(self, pid):
        self.node_settings.folder_id = pid

    def setUp(self):
        super(TestMicrosofTteamsSerializer, self).setUp()

    def tearDown(self):
        super(TestMicrosofTteamsSerializer, self).tearDown()
