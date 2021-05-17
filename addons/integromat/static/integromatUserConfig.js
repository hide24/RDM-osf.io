/**
* Module that controls the Integromat user settings. Includes Knockout view-model
* for syncing data.
*/

var ko = require('knockout');
var $ = require('jquery');
var Raven = require('raven-js');
var bootbox = require('bootbox');
require('js/osfToggleHeight');

var language = require('js/osfLanguage').Addons.integromat;
var osfHelpers = require('js/osfHelpers');
var addonSettings = require('js/addonSettings');
var ChangeMessageMixin = require('js/changeMessage');
var ExternalAccount = addonSettings.ExternalAccount;

var $modal = $('#integromatCredentialsModal');

function ViewModel(url) {
    var self = this;

    self.properName = 'Integromat';
    self.accessKey = ko.observable();
    self.secretKey = ko.observable();
    self.account_url = '/api/v1/settings/integromat/accounts/';
    self.accounts = ko.observableArray();

    self.integromatApiToken = ko.observable();
    self.integromatWebhookUrl = ko.observable();

    self.userGuid = ko.observable();
    self.microsoftTeamsUserName = ko.observable();
    self.microsoftTeamsMail = ko.observable();
    self.webexMeetingsDisplayName = ko.observable();
    self.webexMeetingsMail = ko.observable();
    self.userGuidToDelete = ko.observable();

    ChangeMessageMixin.call(self);

    /** Reset all fields from Integromat credentials input modal */
    self.clearModal = function() {
        self.message('');
        self.messageClass('text-info');
        self.integromatApiToken(null);
        self.integromatWebhookUrl(null);
    };
    /** Send POST request to authorize Integromat */
    self.connectAccount = function() {
        // Selection should not be empty
        if (!self.integromatApiToken() ){
            self.changeMessage('Please enter an API token.', 'text-danger');
            return;
        }
        if (!self.integromatWebhookUrl() ){
            self.changeMessage('Please enter an Webhook URL.', 'text-danger');
            return;
        }

        return osfHelpers.postJSON(
            self.account_url,
            ko.toJS({
                integromat_api_token: self.integromatApiToken(),
                integromat_webhook_url: self.integromatWebhookUrl()
            })
        ).done(function() {
            self.clearModal();
            $modal.modal('hide');
            self.updateAccounts();

        }).fail(function(xhr, textStatus, error) {
            var errorMessage = (xhr.status === 400 && xhr.responseJSON.message !== undefined) ? xhr.responseJSON.message : 'auth error';
            self.changeMessage(errorMessage, 'text-danger');
            Raven.captureMessage('Could not authenticate with Integromat', {
                extra: {
                    url: self.account_url,
                    textStatus: textStatus,
                    error: error
                }
            });
        });
    };

    self.updateAccounts = function() {
        return $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).done(function (data) {
            self.accounts($.map(data.accounts, function(account) {
                var externalAccount =  new ExternalAccount(account);
                externalAccount.integromatApiToken = account.integromat_api_token;
                externalAccount.integromatWebhookUrl = account.integromat_webhook_url;
                return externalAccount;
            }));
            $('#integromat-header').osfToggleHeight({height: 160});
        }).fail(function(xhr, status, error) {
            self.changeMessage('user setting error', 'text-danger');
            Raven.captureMessage('Error while updating addon account', {
                extra: {
                    url: url,
                    status: status,
                    error: error
                }
            });
        });
    };

    self.askDisconnect = function(account) {
        var self = this;
        bootbox.confirm({
            title: 'Disconnect Integromat Account?',
            message: '<p class="overflow">' +
                'Are you sure you want to disconnect the Integromat account <strong>' +
                osfHelpers.htmlEscape(account.name) + '</strong>? This will revoke access to Integromat for all projects associated with this account.' +
                '</p>',
            callback: function (confirm) {
                if (confirm) {
                    self.disconnectAccount(account);
                }
            },
            buttons:{
                confirm:{
                    label:'Disconnect',
                    className:'btn-danger'
                }
            }
        });
    };

    self.disconnectAccount = function(account) {
        var self = this;
        var url = '/api/v1/oauth/accounts/' + account.id + '/';
        var request = $.ajax({
            url: url,
            type: 'DELETE'
        });
        request.done(function(data) {
            self.updateAccounts();
        });
        request.fail(function(xhr, status, error) {
            Raven.captureMessage('Error while removing addon authorization for ' + account.id, {
                extra: {
                    url: url,
                    status: status,
                    error: error
                }
            });
        });
        return request;
    };

    self.selectionChanged = function() {
        self.changeMessage('','');
    };

    self.updateAccounts();

    self.addWebMeetingAppsUser = function() {
        ;
    };
    self.deleteMicrosoftTeamsUser = function() {
        ;
    };
}

$.extend(ViewModel.prototype, ChangeMessageMixin.prototype);

function IntegromatUserConfig(selector, url) {
    // Initialization code
    var self = this;
    self.selector = selector;
    self.url = url;
    // On success, instantiate and bind the ViewModel
    self.viewModel = new ViewModel(url);
    osfHelpers.applyBindings(self.viewModel, self.selector);
}

module.exports = {
    IntegromatViewModel: ViewModel,
    IntegromatUserConfig: IntegromatUserConfig
};