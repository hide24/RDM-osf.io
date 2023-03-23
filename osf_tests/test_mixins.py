# -*- coding: utf-8 -*-
import pytest

from addons.osfstorage.tests import factories
from osf_tests.factories import ProjectFactory, RegionFactory, NodeFactory
from tests.base import OsfTestCase
from unittest import mock


@pytest.mark.django_db
class TestAddonModelMixin(OsfTestCase):

    def setUp(self):
        super(TestAddonModelMixin, self).setUp()
        self.config = {
            'storage': {
                'provider': 'osfstorage',
                'container': 'osf_storage',
                'use_public': True,
            }
        }
        self.user = factories.AuthUserFactory()
        self.project = ProjectFactory(creator=self.user)
        self.region = RegionFactory(waterbutler_settings=self.config)
        self.new_component = NodeFactory(parent=self.project)

    def test_get_addon_region(self):
        root_id = 1
        res = self.new_component.get_addon('osfstorage', False, self.region.id, root_id)
        assert res is None

    def test_get_addon_region_not_exist(self):
        res = self.new_component.get_addon('osfstorage', False, self.region.id)
        assert res is None

    def test_get_addon_not_region_id(self):
        res = self.new_component.get_addon('osfstorage', False, None)
        assert res is not None

    def test_get_addon_exception(self):
        res = self.new_component.get_addon(None)
        assert res is None

    def test_get_addon_return_none(self):
        with mock.patch('osf.models.mixins.AddonModelMixin._settings_model', return_value=None):
            res = self.new_component.get_addon('osfstorage')
            assert res is None
