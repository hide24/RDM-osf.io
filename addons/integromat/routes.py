# -*- coding: utf-8 -*-
"""Routes for the integromat addon.
"""

from framework.routing import Rule, json_renderer
from website.routes import notemplate

from addons.integromat import views

TEMPLATE_DIR = './addons/integromat/templates/'

# HTML endpoints
page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/<pid>/grdmapps',
                '/<pid>/node/<nid>/grdmapps',
            ],
            'get',
            views.project_grdmapps,
            notemplate
        ),

    ]
}

# JSON endpoints
api_routes = {
    'rules': [

        Rule(
            '/settings/integromat/accounts/',
            'post',
            views.integromat_add_user_account,
            json_renderer,
        ),

        Rule(
            [
                '/settings/integromat/accounts/',
            ],
            'get',
            views.integromat_account_list,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/settings/',
                '/project/<pid>/node/<nid>/integromat/settings/'
            ],
            'get',
            views.integromat_get_config,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/settings/',
                '/project/<pid>/node/<nid>/integromat/settings/'
            ],
            'put',
            views.integromat_set_config,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/user_auth/',
                '/project/<pid>/node/<nid>/integromat/user_auth/'
            ],
            'put',
            views.integromat_import_auth,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/user_auth/',
                '/project/<pid>/node/<nid>/integromat/user_auth/'
            ],
            'delete',
            views.integromat_deauthorize_node,
            json_renderer,
        ),
        #route for Integromat action
        Rule(
            '/integromat/integromat_api_call',
            'get',
            views.integromat_api_call,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/register_meeting',
                '/project/<pid>/node/<nid>/integromat/register_meeting',
            ],
            'post',
            views.integromat_register_meeting,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/update_meeting_registration',
                '/project/<pid>/node/<nid>/integromat/update_meeting_registration',
            ],
            'post',
            views.integromat_update_meeting_registration,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/delete_meeting_registration',
                '/project/<pid>/node/<nid>/integromat/delete_meeting_registration',
            ],
            'post',
            views.integromat_delete_meeting_registration,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/start_scenario',
                '/project/<pid>/node/<nid>/integromat/start_scenario',
            ],
            'post',
            views.integromat_start_scenario,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/requestNextMessages',
                '/project/<pid>/node/<nid>/integromat/requestNextMessages',
            ],
            'post',
            views.integromat_req_next_msg,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/register_alternative_webhook_url',
                '/project/<pid>/node/<nid>/integromat/register_alternative_webhook_url',
            ],
            'post',
            views.integromat_register_alternative_webhook_url,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/register_web_meeting_apps_email',
                '/project/<pid>/node/<nid>/integromat/register_web_meeting_apps_email',
            ],
            'post',
            views.integromat_register_web_meeting_apps_email,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/info_msg',
                '/project/<pid>/node/<nid>/integromat/info_msg',
            ],
            'post',
            views.integromat_info_msg,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/error_msg',
                '/project/<pid>/node/<nid>/integromat/error_msg',
            ],
            'post',
            views.integromat_error_msg,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/get_meetings',
                '/project/<pid>/node/<nid>/integromat/get_meetings',
            ],
            'get',
            views.integromat_get_meetings,
            json_renderer,
        ),

        # ember: ここから
        Rule([
            '/project/<pid>/grdmapps/config',
            '/project/<pid>/node/<nid>/grdmapps/config',
        ], 'get', views.grdmapps_get_config_ember, json_renderer),
        Rule([
            '/project/<pid>/grdmapps/config',
            '/project/<pid>/node/<nid>/grdmapps/config',
        ], 'patch', views.grdmapps_set_config_ember, json_renderer),
        # ember: ここまで

    ],
    'prefix': '/api/v1'
}
