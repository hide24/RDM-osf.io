# -*- coding: utf-8 -*-
from addons.base.tests.base import OAuthAddonTestCaseMixin, AddonTestCase
from addons.integromat.provider import IntegromatProvider
from addons.integromat.serializer import IntegromatSerializer
from addons.integromat.tests.factories import (
    IntegromatAccountFactory,
    IntegromatAttendeesFactory,
    IntegromatWorkflowExecutionMessagesFactory,
    IntegromatAllMeetingInformationFactory,
    IntegromatAllMeetingInformationAttendeesRelationFactory,
    IntegromatNodeWorkflowsFactory
)


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

    WorkflowExecutionMessage = IntegromatWorkflowExecutionMessagesFactory
    AttendeesFactory = IntegromatAttendeesFactory
    AllMeetingInformationFactory = IntegromatAllMeetingInformationFactory
    AllMeetingInformationAttendeesRelationFactory = IntegromatAllMeetingInformationAttendeesRelationFactory
    NodeWorkflowsFactory = IntegromatNodeWorkflowsFactory
