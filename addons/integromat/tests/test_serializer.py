# -*- coding: utf-8 -*-
"""Serializer tests for the My MinIO addon."""
import mock
import pytest

from addons.base.tests.serializers import StorageAddonSerializerTestSuiteMixin
from addons.integromat.tests.factories import IntegromatAccountFactory
from addons.integromat.serializer import IntegromatSerializer

from tests.base import OsfTestCase

pytestmark = pytest.mark.django_db

class TestIntegromatSerializer(StorageAddonSerializerTestSuiteMixin, OsfTestCase):
    addon_short_name = 'integromat'
    Serializer = IntegromatSerializer
    ExternalAccountFactory = IntegromatAccountFactory

    def set_provider_id(self, pid):
        self.node_settings.folder_id = pid

    def setUp(self):
        self.mock_credentials = mock.patch('addons.integromat.serializer.IntegromatSerializer.credentials_are_valid')
        self.mock_credentials.return_value = True
        self.mock_credentials.start()
        super(TestIntegromatSerializer, self).setUp()

    def tearDown(self):
        self.mock_credentials.stop()
        super(TestIntegromatSerializer, self).tearDown()