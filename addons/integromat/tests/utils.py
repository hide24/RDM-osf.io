# -*- coding: utf-8 -*-
from nose.tools import (assert_equals, assert_true, assert_false)

from addons.base.tests.base import OAuthAddonTestCaseMixin, AddonTestCase
from addons.integromat.tests.factories import IntegromatAccountFactory
from addons.integromat.provider import IntegromatProvider
from addons.integromat.serializer import IntegromatSerializer
from addons.integromat import utils

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