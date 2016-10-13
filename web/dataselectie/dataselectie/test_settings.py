# Tests

from dataselectie.settings import *

def _get_docker_host():
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return '127.0.0.1'

ELASTIC_SEARCH_HOSTS = [
    "{}:{}".format(os.getenv('TEST_ELASTICSEARCH_PORT_9200_TCP_ADDR', _get_docker_host()), os.getenv('TEST_ELASTICSEARCH_PORT_9200_TCP_PORT', 9210))
]

ELASTIC_INDICES = {
    'DS_BAG': 'ds_bag',
}

DEBUG = True

DATABASE_ROUTERS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_DATASELECTIE_ENV_POSTGRES_DB', 'dataselectie'),
        'USER': os.getenv('DATABASE_DATASELECTIE_ENV_POSTGRES_USER', 'dataselectie'),
        'PASSWORD': os.getenv('DATABASE_DATASELECTIE_ENV_POSTGRES_PASSWORD', 'insecure'),
        'HOST': os.getenv('DATABASE_DATASELECTIE_PORT_5432_TCP_ADDR', _get_docker_host()),
        'PORT': os.getenv('DATABASE_DATASELECTIE_PORT_5432_TCP_PORT', 5435),
        'CONN_MAX_AGE': 60,
    }
}


TEST_RUNNER = 'dataselectie.utils.ManagedModelTestRunner'
JENKINS_TEST_RUNNER = 'dataselectie.utils.JenkinsManagedModelTestRunner'
IN_TEST_MODE = True
