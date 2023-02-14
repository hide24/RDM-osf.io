import pytest

from api.base.settings.defaults import API_BASE
from osf_tests.factories import (
    AuthUserFactory,
    RegionFactory
)
from unittest import mock
from addons.osfstorage.models import Region

@pytest.mark.django_db
class TestRegionDetail:

    @pytest.fixture()
    def region(self):
        return RegionFactory(name='Frankfort', _id='eu-central-1')

    @pytest.fixture()
    def bad_url(self):
        return '/{}regions/blah/'.format(API_BASE)

    @pytest.fixture()
    def region_url(self, region):
        return '/{}regions/{}/'.format(
            API_BASE, region._id)

    @pytest.fixture()
    def user(self):
        return AuthUserFactory()

    def test_region_detail(self, app, region_url, user):
        # test not auth
        reg = RegionFactory()
        with mock.patch('addons.osfstorage.models.Region.objects.get', return_value=reg):
            detail_res = app.get(region_url)
            assert detail_res.status_code == 200
            assert detail_res.json['data']['attributes']['name'] == reg.name
            assert detail_res.json['data']['id'] == reg._id

            # test auth
            detail_res = app.get(region_url, auth=user.auth)
            assert detail_res.status_code == 200

    def test_region_not_found(self, app, bad_url):
        with mock.patch('addons.osfstorage.models.Region.objects.get', side_effect=Region.DoesNotExist('mock error')):
            detail_res = app.get(bad_url, expect_errors=True)
            assert detail_res.status_code == 404
