import os
from addons.base.apps import BaseAddonAppConfig


HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(
    HERE,
    'templates'
)

class IntegromatAddonConfig(BaseAddonAppConfig):

    name = 'addons.integromat'
    label = 'addons_integromat'
    short_name = 'integromat'
    full_name = 'Integromat'
    views = ['widget', 'page']
    categories = ['web apps']
    owners = ['user', 'node']
    configs = ['accounts', 'node']
    has_page_icon = False
    tab_name = 'Web Apps'
    tab_path = 'grdmapps'

    node_settings_template = os.path.join(TEMPLATE_PATH, 'integromat_node_settings.mako')
    user_settings_template = os.path.join(TEMPLATE_PATH, 'integromat_user_settings.mako')

    # default value for RdmAddonOption.is_allowed for GRDM Admin
    is_allowed_default = False

    @property
    def routes(self):
        from . import routes
        return [routes.page_routes, routes.api_routes]

    @property
    def user_settings(self):
        return self.get_model('UserSettings')

    @property
    def node_settings(self):
        return self.get_model('NodeSettings')
