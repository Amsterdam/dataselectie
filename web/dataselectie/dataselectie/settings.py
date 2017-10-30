"""
Django settings for dataselectie project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import datetime
import sys

import os

from dataselectie.utils import get_variable
from dataselectie.utils import get_db_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
insecure_key = 'insecure'
SECRET_KEY = os.getenv('DATASELECTIE_SECRET_KEY', insecure_key)

DEBUG = SECRET_KEY == insecure_key

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',

    # 'django_extensions',

    'dataselectie',
    'batch',
    'api',

    # Datasets

    'datasets.hr',
    'datasets.bag'
]


# set to True for local development.
LOCAL = False
CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'authorization_django.authorization_middleware',
]

if LOCAL:
    INSTALLED_APPS += ('corsheaders',)
    MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')


ROOT_URLCONF = 'dataselectie.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['{}/datasets/generic/templates'.format(BASE_DIR)],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dataselectie.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DS_DATASELECTIE = get_db_settings(
    db='dataselectie',
    docker_host='database',
    localport='5435')

DS_BAG = get_db_settings(
    db='dataselectie',
    user='handelsregister',
    docker_host='127.0.0.1',
    localport='5406')

# These are the handelsregister docker db settings
DS_HR = get_db_settings(
    db='handelsregister',
    docker_host='127.0.0.1',
    localport='5406')


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': DS_DATASELECTIE['db'],
        'USER': DS_DATASELECTIE['username'],
        'PASSWORD': DS_DATASELECTIE['password'],
        'HOST': DS_DATASELECTIE['host'],
        'PORT': DS_DATASELECTIE['port'],
        'CONN_MAX_AGE': 60,
    },

    #'bag': {
    #    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #    'NAME': DS_BAG['db'],
    #    'USER': DS_BAG['username'],
    #    'PASSWORD': DS_BAG['password'],
    #    'HOST': DS_BAG['host'],
    #    'PORT': DS_BAG['port'],
    #    'CONN_MAX_AGE': 60,
    #},

    #'hr': {
    #    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #    'NAME': DS_HR['db'],
    #    'USER': DS_HR['username'],
    #    'PASSWORD': DS_HR['password'],
    #    'HOST': DS_HR['host'],
    #    'PORT': DS_HR['port'],
    #    'CONN_MAX_AGE': 60,
    #},
}

USE_I18N = True
# to use docker hr database directly
# handy for development
HR_DATABASE = 'default'
# HR_DATABASE = 'hr'

LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', '127.0.0.1')
LOGSTASH_PORT = int(os.getenv('LOGSTASH_GELF_UDP_PORT', 12201))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'slack': {
            'format': '%(message)s',
        },
        'console': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },

    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },

        'graypy': {
            'level': 'ERROR',
            'class': 'graypy.GELFHandler',
            'host': LOGSTASH_HOST,
            'port': LOGSTASH_PORT,
        },
    },

    'root': {
        'level': 'INFO',
        'handlers': ['console', 'graypy'],
    },

    'loggers': {
        # Debug all batch jobs
        'batch': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },

        'search': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'elasticsearch': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

        'urllib3.connectionpool': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'urllib3.util': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },

    },
}

IN_TEST_MODE = 'test' in sys.argv


ELASTIC_SEARCH_HOSTS = ["{}:{}".format(
    get_variable('ELASTIC_HOST_OVERRIDE', 'elasticsearch', 'localhost'),
    get_variable('ELASTIC_PORT_OVERRIDE', '9200'))]

ELASTIC_INDICES = {
    'DS_BAG_INDEX': 'ds_bag_index',
    'DS_HR_INDEX': 'ds_hr_index'
}

MAX_SEARCH_ITEMS = 10000
MIN_BAG_NR = 1000
MIN_HR_NR = 1000

# The size of the preview to fetch from elastic
SEARCH_PREVIEW_SIZE = 100
AGGS_VALUE_SIZE = 100
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
DATAPUNT_AUTHZ = {
    'JWT_SECRET_KEY': os.getenv('JWT_SHARED_SECRET_KEY'),
    'JWT_ALGORITHM': 'HS256'
}

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

JWT_AUTH = {
    'JWT_ENCODE_HANDLER': 'rest_framework_jwt.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER': 'rest_framework_jwt.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USER_ID_HANDLER': 'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',  # noqa
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_response_payload_handler',             # noqa
    'JWT_SECRET_KEY': os.getenv('JWT_SHARED_SECRET_KEY', 'some_shared_secret'),
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/


STATIC_URL = '/static/'

# Generate https links
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True

# Db routing goes haywire without this
