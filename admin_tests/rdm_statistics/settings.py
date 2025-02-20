# -*- coding: utf-8 -*-
"""Consolidates settings from defaults.py and local.py.

::
    >>> from admin.base import settings
    >>> settings.ADMIN_BASE
    'admin/'
"""
import os
from urllib.parse import urlparse
from website import settings as osf_settings
from django.contrib import messages
from api.base.settings import *  # noqa

import warnings

from .defaults import *  # noqa

try:
    from .local import *  # noqa
except ImportError:
    warnings.warn('No admin/base/settings/local.py settings file found. Did you remember to '
                  'copy local-dist.py to local.py?', ImportWarning)
"""
Django settings for the admin project.
"""
# TODO ALL SETTINGS FROM API WILL BE IMPORTED AND WILL NEED TO BE OVERRRIDEN
# TODO THIS IS A STEP TOWARD INTEGRATING ADMIN & API INTO ONE PROJECT

# import local  # Build own local.py (used with postgres)

# TODO - remove duplicated items, as this is now using settings from the API

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# from the GakuNin RDM settings
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = osf_settings.SECRET_KEY


# Don't allow migrations
DATABASE_ROUTERS = ['admin.base.db.router.NoMigrationRouter']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = osf_settings.DEBUG_MODE
DEBUG_PROPAGATE_EXCEPTIONS = True


# session:
SESSION_COOKIE_NAME = 'admin'
SESSION_COOKIE_SECURE = osf_settings.SECURE_MODE
SESSION_COOKIE_HTTPONLY = osf_settings.SESSION_COOKIE_HTTPONLY

# csrf:
CSRF_COOKIE_NAME = 'admin-csrf'
CSRF_COOKIE_SECURE = osf_settings.SECURE_MODE
# set to False: prereg uses a SPA and ajax and grab the token to use it in the requests
CSRF_COOKIE_HTTPONLY = False

ALLOWED_HOSTS = [
    'localhost'
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 5,
        }
    },
]

USE_L10N = False

# Email settings. Account created for testing. Password shouldn't be hardcoded
# [DEVOPS] this should be set to 'django.core.mail.backends.smtp.EmailBackend' in the > dev local.py.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Sendgrid Email Settings - Using OSF credentials.
# Add settings references to local.py

EMAIL_HOST = osf_settings.MAIL_SERVER
EMAIL_HOST_USER = osf_settings.MAIL_USERNAME
EMAIL_HOST_PASSWORD = osf_settings.MAIL_PASSWORD
EMAIL_PORT = 25
EMAIL_USE_TLS = False

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # 3rd party
    'raven.contrib.django.raven_compat',
    'webpack_loader',
    'django_nose',
    'password_reset',

    # OSF
    'osf',

    # Addons
    'addons.osfstorage',
    'addons.wiki',
    'addons.twofactor',
    # Additional addons
    'addons.bitbucket',
    'addons.box',
    'addons.dataverse',
    'addons.dropbox',
    'addons.figshare',
    'addons.forward',
    'addons.github',
    'addons.googledrive',
    'addons.mendeley',
    'addons.owncloud',
    'addons.s3',
    'addons.zotero',
    'addons.iqbrims',

    # Internal apps
    'admin.common_auth',
    'admin.base',
    'admin.pre_reg',
    'admin.spam',
    'admin.metrics',
    'admin.nodes',
    'admin.users',
    'admin.desk',
    'admin.meetings',
    'admin.institutions',
    'admin.preprint_providers',
)

MIGRATION_MODULES = {
    'osf': None,
    'addons_osfstorage': None,
    'addons_wiki': None,
    'addons_twofactor': None,
    'addons_bitbucket': None,
    'addons_box': None,
    'addons_dataverse': None,
    'addons_dropbox': None,
    'addons_figshare': None,
    'addons_forward': None,
    'addons_github': None,
    'addons_googledrive': None,
    'addons_mendeley': None,
    'addons_owncloud': None,
    'addons_s3': None,
    'addons_zotero': None,
    'addons_iqbrims': None,
}

USE_TZ = True
TIME_ZONE = 'UTC'

# local development using https
if osf_settings.SECURE_MODE and osf_settings.DEBUG_MODE:
    INSTALLED_APPS += ('sslserver',)

# Custom user model (extends AbstractBaseUser)
AUTH_USER_MODEL = 'osf.OSFUser'

# TODO: Are there more granular ways to configure reporting specifically related to the API?
RAVEN_CONFIG = {
    'tags': {'App': 'admin'},
    'dsn': osf_settings.SENTRY_DSN,
    'release': osf_settings.VERSION,
}

# Settings related to CORS Headers addon: allow API to receive authenticated requests from OSF
# CORS plugin only matches based on "netloc" part of URL, so as workaround we add that to the list
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (urlparse(osf_settings.DOMAIN).netloc,
                         osf_settings.DOMAIN,
                         )
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE_CLASSES = (
    # TokuMX transaction support
    # Needs to go before CommonMiddleware, so that transactions are always started,
    # even in the event of a redirect. CommonMiddleware may cause other middlewares'
    # process_request to be skipped, e.g. when a trailing slash is omitted
    'api.base.middleware.DjangoGlobalMiddleware',
    'api.base.middleware.CeleryTaskMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

MESSAGE_TAGS = {
    messages.SUCCESS: 'text-success',
    messages.ERROR: 'text-danger',
    messages.WARNING: 'text-warning',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'admin.rdm_announcement.context_processor.setInstitution',
            ],
        }
    }]

ROOT_URLCONF = 'admin.base.urls'
WSGI_APPLICATION = 'admin.base.wsgi.application'
ADMIN_BASE = ''
STATIC_URL = '/static/'
LOGIN_URL = 'account/login/'
LOGIN_REDIRECT_URL = ADMIN_BASE

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static_root')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, '../website/static'),
)

LANGUAGE_CODE = 'en-us'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'public/js/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--verbosity=2']

# Keen.io settings in local.py
KEEN_PROJECT_ID = osf_settings.KEEN['private']['project_id']
KEEN_READ_KEY = osf_settings.KEEN['private']['read_key']
KEEN_WRITE_KEY = osf_settings.KEEN['private']['write_key']

KEEN_CREDENTIALS = {
    'keen_ready': False
}

if KEEN_CREDENTIALS['keen_ready']:
    KEEN_CREDENTIALS.update({
        'keen_project_id': KEEN_PROJECT_ID,
        'keen_read_key': KEEN_READ_KEY,
        'keen_write_key': KEEN_WRITE_KEY
    })


ENTRY_POINTS = {'osf4m': 'osf4m', 'prereg_challenge_campaign': 'prereg',
                'institution_campaign': 'institution'}

# Set in local.py
DESK_KEY = ''
DESK_KEY_SECRET = ''

TINYMCE_APIKEY = ''

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar', )
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda _: True
    }

FCM_SETTINGS = {
    'FCM_SERVER_KEY': ''
}

TEST_DATABASE_NAME = 'test_suzuki'
TEST = 'aaa'
NAME = 'bbb'
