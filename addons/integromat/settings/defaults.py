H_SDK_VERSION = '2.0.0'
INTEGROMAT_API_WHOAMI = 'https://api.integromat.com/v1/whoami'
TIME_LIMIT_START_SCENARIO = 15

#APPS
MICROSOFT_TEAMS = 'MicrosoftTeams'
WEBEX_MEETINGS = 'WebexMeetings'

#WORKFLOWS
#Make sure the values match the ember-osf-web translation key.
WEB_MEETING_DESC = 'integromat.workflows.web_meeting.description'
WEB_MEETING_APPS = 'integromat.workflows.web_meeting.apps'

### The id is registered in databaselike a foreign key###
### DO NOT MODIFY APP ID ################################
RDM_WEB_MEETING_APPS = [
    {
        'id': '1639',
        'app_name': MICROSOFT_TEAMS
    },
    {
        'id': '3152',
        'app_name': WEBEX_MEETINGS
    }
]

RDM_WORKFLOW = [
    {
        'id': '7895',
        'workflow_description': WEB_MEETING_DESC,
        'workflow_apps': WEB_MEETING_APPS
    }
]
#######################################################
