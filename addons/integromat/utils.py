# -*- coding: utf-8 -*-

# widget: ここから
def serialize_integromat_widget(node):
    integromat = node.get_addon('integromat')
    ret = {
        # if True, show widget body, otherwise show addon configuration page link.
        'complete': True
    }
    ret.update(integromat.config.to_json())
    return ret
# widget: ここまで