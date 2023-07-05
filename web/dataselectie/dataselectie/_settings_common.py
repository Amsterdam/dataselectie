"""
Django settings for dataselectie project.

"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DATASELECTIE_SECRET_KEY', "insecure")
DEBUG = os.getenv("DEBUG", False)

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django_filters',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
]

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'authorization_django.authorization_middleware',
]

if DEBUG:
    INSTALLED_APPS += ('corsheaders',)
    MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['{}/datasets/generic/templates'.format(BASE_DIR)],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DUMP_DIR = 'mks-dump'

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', '127.0.0.1')
LOGSTASH_PORT = int(os.getenv('LOGSTASH_GELF_UDP_PORT', 12201))

REST_FRAMEWORK = dict(
    PAGE_SIZE=100,
    MAX_PAGINATE_BY=100,
    DEFAULT_PAGINATION_CLASS='rest_framework.pagination.PageNumberPagination',

    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},

    DEFAULT_AUTHENTICATION_CLASSES=(
    ),

    DEFAULT_RENDERER_CLASSES=(
        'rest_framework.renderers.JSONRenderer',
    ),

    DEFAULT_FILTER_BACKENDS=(
        'django_filters.rest_framework.DjangoFilterBackend',

    ),
    COERCE_DECIMAL_TO_STRING=True,
)


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
            'class': 'graypy.GELFUDPHandler',
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

