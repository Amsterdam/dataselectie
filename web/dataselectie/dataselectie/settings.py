"""
Django settings for dataselectie project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import re
import sys

from typing import List

TESTING = 'test' in sys.argv


def _get_docker_host() -> str:
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return '127.0.0.1'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
insecure_key = 'insecure'
SECRET_KEY = os.getenv('DATASELECTIE_SECRET_KEY', insecure_key)

DEBUG = SECRET_KEY == insecure_key

ALLOWED_HOSTS = ['*']     # type: List[str]

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # dataselectie
    'batch',
    'api',
    # Datasets
    'datasets.hr',
    'datasets.bag'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_DATASELECTIE_ENV_POSTGRES_DB', 'dataselectie'),
        'USER': os.getenv('DATABASE_DATASELECTIE_ENV_POSTGRES_USER', 'dataselectie'),
        'PASSWORD': os.getenv('DATABASE_DATASELECTIE_ENV_POSTGRES_PASSWORD', insecure_key),
        'HOST': os.getenv('DATABASE_DATASELECTIE_PORT_5432_TCP_ADDR', _get_docker_host()),
        'PORT': os.getenv('DATABASE_DATASELECTIE_PORT_5432_TCP_PORT', '5435'),
        'CONN_MAX_AGE': 60,
    },

    'bag': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_BAG_ENV_POSTGRES_DB', 'atlas'),
        'USER': os.getenv('DATABASE_BAG_ENV_POSTGRES_USER', 'atlas'),
        'PASSWORD': os.getenv('DATABASE_BAG_ENV_POSTGRES_PASSWORD', insecure_key),
        'HOST': os.getenv('DATABASE_BAG_PORT_5432_TCP_ADDR', _get_docker_host()),
        'PORT': os.getenv('DATABASE_BAG_PORT_5432_TCP_PORT', '5436'),
        'CONN_MAX_AGE': 60,
    },

    'hr': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_HR_ENV_POSTGRES_DB', 'handelsregister'),
        'USER': os.getenv('DATABASE_HR_ENV_POSTGRES_USER', 'handelsregister'),
        'PASSWORD': os.getenv('DATABASE_HR_ENV_POSTGRES_PASSWORD', 'insecure'),
        'HOST': os.getenv('DATABASE_HR_PORT_5432_TCP_ADDR', _get_docker_host()),
        'PORT': os.getenv('DATABASE_HR_PORT_5432_TCP_PORT', '5406'),
        'CONN_MAX_AGE': 60,
    }
}


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
    },

    'root': {
        'level': 'INFO',
        'handlers': ['console'],
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

        # Log all unhandled exceptions
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# DB routing
DATABASE_ROUTERS = ['datasets.generic.dbroute.DatasetsRouter', ]

ELASTIC_SEARCH_HOSTS = ["{}:{}".format(
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_ADDR', _get_docker_host()),
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_PORT', '9200'))]

ELASTIC_INDICES = {
    'DS_INDEX': 'ds_index'
}

MAX_SEARCH_ITEMS = 10000
MIN_BAG_NR = 1000
MIN_HR_NR = 1000


# The size of the preview to fetch from elastic
SEARCH_PREVIEW_SIZE = 100
AGGS_VALUE_SIZE = 100

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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

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

# Checking if running inside some test mode


# settings below are just for unit test purposes and need to be put in a test_settings.py module
TEST_RUNNER = 'dataselectie.utils.ManagedModelTestRunner'

IN_TEST_MODE = TESTING
# Setting test prefix on index names in test
if TESTING:
    MIN_BAG_NR = 0
    MIN_HR_NR = 0
    for k, v in ELASTIC_INDICES.items():
        ELASTIC_INDICES[k] = 'test_{}'.format(v)

DATAPUNT_API_URL = 'https://api.datapunt.amsterdam.nl/'