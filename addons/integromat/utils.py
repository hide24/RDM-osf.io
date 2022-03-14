# -*- coding: utf-8 -*-
import json
from django.core import serializers

# widget: ここから
def serialize_integromat_widget(node):
    integromat = node.get_addon('integromat')
    ret = {
        # if True, show widget body, otherwise show addon configuration page link.
        'complete': integromat.complete,
        'include': False,
        'can_expand': True,
    }
    ret.update(integromat.config.to_json())
    return ret
# widget: ここまで

def get_guid(node):

    qsGuid = node._prefetched_objects_cache['guids'].only()
    guidSerializer = serializers.serialize('json', qsGuid, ensure_ascii=False)
    guidJson = json.loads(guidSerializer)
    guid = guidJson[0]['fields']['_id']
    return guid
