import pytest
from addons.base.utils import get_mfr_url
import mock
from nose.tools import assert_equal
from addons.osfstorage.tests.utils import StorageTestCase
from tests.base import OsfTestCase
from osf_tests.factories import ProjectFactory, UserFactory, RegionFactory, CommentFactory
from website.settings import MFR_SERVER_URL
from addons.base.utils import get_root_institutional_storage
from osf.models import BaseFileNode
class MockFolder(dict, object):

    def __init__(self):
        self.name = 'Fake Folder'
        self.json = {'id': 'Fake Key', 'parent_id': 'cba321', 'name': 'Fake Folder'}
        self['data'] = {'name': 'Fake Folder', 'key': 'Fake Key', 'parentCollection': False}
        self['library'] = {'type': 'personal', 'id': '34241'}
        self['name'] = 'Fake Folder'
        self['id'] = 'Fake Key'


class MockLibrary(dict, object):

    def __init__(self):
        self.name = 'Fake Library'
        self.json = {'id': 'Fake Library Key', 'parent_id': 'cba321'}
        self['data'] = {'name': 'Fake Library', 'key': 'Fake Key', 'id': '12345' }
        self['name'] = 'Fake Library'
        self['id'] = 'Fake Library Key'


@pytest.mark.django_db
class TestAddonsUtils(OsfTestCase):
    def test_mfr_url(self):
        user = UserFactory()
        project = ProjectFactory(creator=user)
        comment = CommentFactory()
        assert get_mfr_url(project, 'github') == MFR_SERVER_URL
        assert get_mfr_url(project, 'osfstorage') == project.osfstorage_region.mfr_url
        assert get_mfr_url(comment, 'osfstorage') == MFR_SERVER_URL

    @mock.patch('osf.models.BaseFileNode.objects.get')
    def test_get_root_institutional_storage(self, mock_base_file_node_objects_get):
        file_id = '12345'
        is_root_none = BaseFileNode(is_root=None, parent_id=1)
        is_root_true = BaseFileNode(is_root=True, parent_id=1)
        mock_base_file_node_objects_get.side_effect = [is_root_none, is_root_true]
        result = get_root_institutional_storage(file_id)
        assert isinstance(result, BaseFileNode)
    @mock.patch('osf.models.files.BaseFileNode.objects.get')
    def test_get_root_institutional_storage_exception(self, mock_base_file_node_objects_get):
        file_id = '12345'
        mock_base_file_node_objects_get.side_effect = BaseFileNode.DoesNotExist('error')
        result = get_root_institutional_storage(file_id)
        assert_equal(result, None)
