'use strict';

var IntegromatUserConfig = require('./integromatUserConfig.js').IntegromatUserConfig;
var url = '/api/v1/settings/integromat/accounts/';
new IntegromatUserConfig('#integromatScope', url);
