<div class="addon-widget" name="${short_name}">
<script src="/addons/static/badges/awardBadge.js"></script>

%if complete:

    <h3 class="addon-widget-header">
        % if can_issue and configured and len(badges) > 0:
<!--             <button class="pull-right btn btn-success" id="awardBadge">
                <i class="icon-plus"></i>
                Award
            </button> -->
        % endif
          <a href="badges/"><span>${full_name}</span></a>
    </h3>

%if len(assertions) > 0:
  <div class="badge-list">
          %for assertion in reversed(assertions[:6]):
            <img src="${assertion['image']}" width="64px" height="64px" class="open-badge badge-popover" badge-url="/${assertion['uid']}/json/" data-content="${assertion['description']}" data-toggle="popover" data-title="${assertion['name']}">
          %endfor
          <!-- TODO add ...-->
  </div>
%endif
<script>

$(document).ready(function(){
  $('.badge-popover').popover({
    container: 'body',
    trigger: 'hover'
  });

% if can_issue and configured and len(badges) > 0:
    $('#awardBadge').editable({
      name:  'title',
      title: 'Award Badge',
      display: false,
      highlight: false,
      placement: 'bottom',
      showbuttons: 'bottom',
      type: 'AwardBadge',
      value: '${badges[0]['id']}',
      badges: [
        %for badge in badges:
          {value: '${badge['id']}', text: '${badge['name']}'},
        %endfor
      ],
      ajaxOptions: {
        'type': 'POST',
        "dataType": "json",
        "contentType": "application/json"
      },
      url: nodeApiUrl + 'badges/award/',
      params: function(params){
        // Send JSON data
        return JSON.stringify(params.value);
      },
      success: function(data){
        document.location.reload(true);
      },
      pk: 'newBadge'
    });

    $('.revoke-badge').editable({
      type: 'text',
      pk: 'revoke',
      title: 'Revoke this badge?',
      placeholder: 'Reason',
      display: false,
      validate: function(value) {
        if($.trim(value) == '') return 'A reason is required';
      },
      ajaxOptions: {
        'type': 'POST',
        "dataType": "json",
        "contentType": "application/json"
      },
      url: nodeApiUrl + 'badges/revoke/',
      params: function(params){
        // Send JSON data
        var uid = $(this).attr('badge-uid')
        return JSON.stringify({reason: params.value, id: uid});
      },
      success: function(data){
        document.location.reload(true);
      },
    });
%endif
});

</script>

%else:
        <div mod-meta='{
                "tpl": "project/addon/config_error.mako",
                "kwargs": {
                    "short_name": "${short_name}",
                    "full_name": "${full_name}"
                }
            }'></div>
%endif
</div>
