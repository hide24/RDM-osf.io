# -*- coding: utf-8 -*-
"""Factories for the Integromat addon."""
import factory
from datetime import date, datetime, timedelta
from factory.django import DjangoModelFactory
from osf.models.user import OSFUser

from addons.integromat import SHORT_NAME
from addons.integromat.models import (
    UserSettings,
    NodeSettings,
    WorkflowExecutionMessages,
    Attendees,
    AllMeetingInformation,
    AllMeetingInformationAttendeesRelation,
    NodeWorkflows
)

from osf_tests.factories import UserFactory, ProjectFactory, ExternalAccountFactory

class IntegromatAccountFactory(ExternalAccountFactory):
    provider = SHORT_NAME
    provider_id = factory.Sequence(lambda n: 'id-{0}'.format(n))
    oauth_key = factory.Sequence(lambda n: 'key-{0}'.format(n))
    webhook_url = factory.Sequence(lambda n: 'webhook-{0}'.format(n))
    display_name = 'Integromat Fake User'


class IntegromatUserSettingsFactory(DjangoModelFactory):
    class Meta:
        model = UserSettings

    owner = factory.SubFactory(UserFactory)


class IntegromatNodeSettingsFactory(DjangoModelFactory):
    class Meta:
        model = NodeSettings

    _id = 'qwe'
    owner = factory.SubFactory(ProjectFactory)
    user_settings = factory.SubFactory(IntegromatUserSettingsFactory)


class IntegromatWorkflowExecutionMessagesFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowExecutionMessages

    notified = False
    integromat_msg = 'integromat.info.message'
    timestamp = '1234567890123'
    node_settings = factory.SubFactory(IntegromatNodeSettingsFactory)

class IntegromatAttendeesFactory(DjangoModelFactory):
    class Meta:
        model = Attendees

    _id = '1234567890qwertyuiop'
    user_guid = 'testuser'
    fullname = 'TEST USER'
    microsoft_teams_mail = 'testUser1@test.onmicrosoft.com'
    microsoft_teams_user_name = 'Teams User'
    webex_meetings_mail = 'testUser2@test.co.jp'
    webex_meetings_display_name = 'Webex User'
    is_guest = False
    node_settings = factory.SubFactory(IntegromatNodeSettingsFactory)

class IntegromatAllMeetingInformationFactory(DjangoModelFactory):
    class Meta:
        model = AllMeetingInformation


    subject = 'TEST MEETING'
    organizer = 'testUser1@test.onmicrosoft.com'
    organizer_fullname = 'TEST USER'
    start_datetime = datetime.now().isoformat()
    end_datetime = (datetime.now() + timedelta(hours=1)).isoformat()
    location = 'LOCATION'
    content = 'MEETING CONTENT'
    join_url = 'teams/microsoft.com/321'
    meetingid = 'qwertyuiopasdfghjklzxcvbnm'
    meeting_password = ''
    app = 1639
    node_settings = factory.SubFactory(IntegromatNodeSettingsFactory)
#    attendees = attendees(True, ['testUser1@test.onmicrosoft.com'])


    @factory.post_generation
    def attendees(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for attendee in extracted:
                self.attendees.add(attendee)


class IntegromatAllMeetingInformationAttendeesRelationFactory(DjangoModelFactory):
    class Meta:
        model = AllMeetingInformationAttendeesRelation

    all_meeting_information = factory.SubFactory(IntegromatAllMeetingInformationFactory)
    attendees = factory.SubFactory(IntegromatAttendeesFactory)
    webex_meetings_invitee_id = 'mnbvcxzlkjhgfdsapoiuytrewq'

class IntegromatNodeWorkflowsFactory(DjangoModelFactory):
    class Meta:
        model = NodeWorkflows

    workflow = factory.SubFactory(IntegromatRdmWorkflowsFactory)
    # An alternative webhook url to the external service
    alternative_webhook_url = 'hook/integromat/com'
    node_settings = factory.SubFactory(IntegromatNodeSettingsFactory)