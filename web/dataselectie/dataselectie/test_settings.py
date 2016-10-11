# Tests

from dataselectie.settings import *

def _get_docker_host():
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return '127.0.0.1'

ELASTIC_SEARCH_HOSTS = ["{}:{}".format(
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_ADDR', _get_docker_host()),
    os.getenv('ELASTICSEARCH_PORT_9200_TCP_PORT', 9210))]

ELASTIC_INDICES = {
    'ZB_BAG': 'zb_bag',
}

DEBUG = True

DATABASE_ROUTERS = []

TEST_RUNNER = 'dataselectie.utils.ManagedModelTestRunner'
IN_TEST_MODE = True
