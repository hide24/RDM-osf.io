'use strict';

var IntegromatNodeConfig = require('./integromatNodeConfig.js').IntegromatNodeConfig;
var url = window.contextVars.node.urls.api + 'integromat/settings/';
new IntegromatNodeConfig('Integromat', '#integromatScope', url, '#integromatGrid');
