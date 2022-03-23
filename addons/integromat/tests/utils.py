# -*- coding: utf-8 -*-
from addons.base.tests.base import OAuthAddonTestCaseMixin, AddonTestCase
from addons.integromat.tests.factories import IntegromatAccountFactory
from addons.integromat.provider import IntegromatProvider
from addons.integromat.serializer import IntegromatSerializer

class IntegromatAddonTestCase(OAuthAddonTestCaseMixin, AddonTestCase):

    ADDON_SHORT_NAME = 'integromat'
    ExternalAccountFactory = IntegromatAccountFactory
    Provider = IntegromatProvider
    Serializer = IntegromatSerializer
    client = None
    folder = {
        'path': 'bucket',
        'name': 'bucket',
        'id': 'bucket'
    }

class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def json(self):
        return json.loads(self.content)
