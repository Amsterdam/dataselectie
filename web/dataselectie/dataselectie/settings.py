"""
Django settings for dataselectie project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

import authorization_levels

from dataselectie._settings_common import *  # noqa F403
from dataselectie._settings_databases import *  # noqa F403

from dataselectie.utils import get_variable
from dataselectie.utils import get_db_settings
from pathlib import Path


DATAPUNT_API_URL = os.getenv(
    'DATAPUNT_API_URL', 'https://api.data.amsterdam.nl/')

# Application definition

INSTALLED_APPS.extend([
    'dataselectie',
    'batch',
    'api',

    # Datasets
    'datasets.hr',
    'datasets.bag',
    'datasets.brk',
])

ROOT_URLCONF = 'dataselectie.urls'

WSGI_APPLICATION = 'dataselectie.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DS_DATASELECTIE = get_db_settings(
    db='dataselectie',
    docker_host='database',
    localport='5435')

DATABASE_OPTIONS = {
    LocationKey.docker: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'dataselectie'),
        'USER': os.getenv('DATABASE_USER', 'dataselectie'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': 'database',
        'PORT': '5432'
    },
    LocationKey.local: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'dataselectie'),
        'USER': os.getenv('DATABASE_USER', 'dataselectie'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': get_docker_host(),
        'PORT': '5435'
    },
    LocationKey.override: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'dataselectie'),
        'USER': os.getenv('DATABASE_USER', 'dataselectie'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv(OVERRIDE_HOST_ENV_VAR),
        'PORT': os.getenv(OVERRIDE_PORT_ENV_VAR, '5432')
    },
}

DATABASES = {
    'default': DATABASE_OPTIONS[get_database_key()]
}

if os.getenv("AZURE", False):
    DATABASES["default"]["PASSWORD"] = Path(os.environ["DATABASE_PW_LOCATION"]).open().read()

ELASTIC_SEARCH_HOSTS = ["{}:{}".format(
    get_variable('ELASTIC_HOST_OVERRIDE', 'elasticsearch', 'localhost'),
    get_variable('ELASTIC_PORT_OVERRIDE', '9200'))]

ELASTIC_INDICES = {
    'DS_BAG_INDEX': 'ds_bag_index',
    'DS_HR_INDEX': 'ds_hr_index',
    'DS_BRK_INDEX': 'ds_brk_index'
}

# MAX_SEARCH_ITEMS is limited by the ElasticSearch index.max_result_window index setting which defaults to 10_000
MAX_SEARCH_ITEMS = 10000
MIN_BAG_NR = 1000
MIN_HR_NR = 1000

# Setting test prefix on index names in test
if TESTING:
    MIN_BAG_NR = 0
    MIN_HR_NR = 0
    for k, v in ELASTIC_INDICES.items():
        ELASTIC_INDICES[k] = 'test_{}'.format(v)

# The size of the preview to fetch from elastic
SEARCH_PREVIEW_SIZE = 100
AGGS_VALUE_SIZE = 1400
DOWNLOAD_BATCH = 900

# Batch processing
BATCH_SETTINGS = {
    'batch_size': 400,
}

PARTIAL_IMPORT = {
    'numerator': 0,
    'denominator': 1,
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

# Security
# The following JWKS data was obtained in the authz project :  jwkgen -create -alg ES256
# This is a test public/private key def and added for testing.
JWKS_TEST_KEY = """
    {
        "keys": [
            {
                "kty": "EC",
                "key_ops": [
                    "verify",
                    "sign"
                ],
                "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                "crv": "P-256",
                "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
            }
        ]
    }
"""

# Security
DATAPUNT_AUTHZ = {
    'JWKS': os.getenv('PUB_JWKS', JWKS_TEST_KEY),
    'JWKS_URL': os.getenv('KEYCLOAK_JWKS_URL'),
    'MIN_SCOPE': authorization_levels.SCOPE_HR_R,
    'FORCED_ANONYMOUS_ROUTES': (
        '/status/',
        '/dataselectie/bag/',
        '/dataselectie/api-docs'
    ),
    'ALWAYS_OK': False
}


SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'

# Generate https links
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True

SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment="dataselectie",
        integrations=[DjangoIntegration()]
    )
