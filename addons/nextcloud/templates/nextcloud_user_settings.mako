<!-- Authorization -->
<div id='nextcloudAddonScope' class='addon-settings addon-generic scripted'
     data-addon-short-name="${ addon_short_name }"
     data-addon-name="${ addon_full_name }">

    <%include file="nextcloud_credentials_modal.mako"/>

    <h4 class="addon-title">
        <img class="addon-icon" src=${addon_icon_url}>
        <span data-bind="text: properName"></span>
        <small>
            <a href="#NextcloudCredentialsModal" data-toggle="modal" class="pull-right text-primary">${_("Connect or Reauthorize Account")}</a>
        </small>
    </h4>

    <div class="addon-auth-table" id="${addon_short_name}-header">
        <!-- ko foreach: accounts -->
        <a data-bind="click: $root.askDisconnect.bind($root)" class="text-danger pull-right default-authorized-by">${_("Disconnect Account")}</a>
        <div class="m-h-lg addon-auth-table" id="${addon_short_name}-header">
            <table class="table table-hover">
                <thead>
                    <tr class="user-settings-addon-auth">
                        <th class="text-muted default-authorized-by">${_('Authorized by <em><span %(data_bind1)s></span></em> on <a %(data_bind2)s><em %(data_bind3)s></em></a>') % dict(data_bind1='data-bind="text: name"', data_bind2='data-bind="attr: {href: profileUrl}"',data_bind3='data-bind="text: profileUrl"') | n}</th><th></th>
                    </tr>
                </thead>
                <!-- ko if: connectedNodes().length > 0 -->
                <tbody data-bind="foreach: connectedNodes()">
                    <tr>
                        <td class="authorized-nodes">
                            <!-- ko if: title --><a data-bind="attr: {href: urls.view}, text: title"></a><!-- /ko -->
                            <!-- ko if: !title --><em>${_("Private project")}</em><!-- /ko -->
                        </td>
                        <td>
                            <a data-bind="click: $parent.deauthorizeNode.bind($parent)">
                                <i class="fa fa-times text-danger pull-right" title="Deauthorize Project"></i>
                            </a>
                        </td>
                    </tr>
                </tbody>
                <!-- /ko -->
            </table>
        </div>
        <!-- /ko -->
    </div>
</div>