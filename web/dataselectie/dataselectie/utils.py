# Packages
import re

import os
import redis
from typing import Dict

from django.test.runner import DiscoverRunner

from dataselectie import settings


class ManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run, so that one doesn't need
    to execute the SQL manually to create them.
    """

    def __init__(self, *args, **kwargs):
        super(ManagedModelTestRunner, self).__init__(*args, **kwargs)
        self.verbosity = 2
        self.unmanaged_models = []

    # def setup_test_environment(self, *args, **kwargs):
    #    datasets = ['bag', 'hr']  # update when new datasets are introdiced
    #    # datasets = []  # update when new datasets are introdiced
    #    for dataset in datasets:
    #        self.unmanaged_models.extend(
    #            [model for _, model in apps.all_models[dataset].items() if
    #             not model._meta.managed]
    #        )
    #    for m in self.unmanaged_models:
    #        m._meta.managed = True
    #    super(ManagedModelTestRunner, self).setup_test_environment(**kwargs)

    # def teardown_test_environment(self, *args, **kwargs):
    #    super(ManagedModelTestRunner, self).teardown_test_environment(**kwargs)
    #    # reset unmanaged models
    #    for m in self.unmanaged_models:
    #        m._meta.managed = False


def get_docker_host():
    """
    Looks for the DOCKER_HOST environment variable to find the VM
    running docker-machine.

    If the environment variable is not found, it is assumed that
    you're running docker on localhost.
    """
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', d_host):
            return d_host

        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return 'localhost'


def in_docker() -> bool:
    """
    Checks pid 1 cgroup settings to check with reasonable certainty we're in a
    docker env.
    :rtype: bool
    :return: true when running in a docker container, false otherwise
    """
    # noinspection PyBroadException
    try:
        cgroup = open('/proc/1/cgroup', 'r').read()
        return ':/docker/' in cgroup or ':/docker-ce/' in cgroup
    except:
        return False


def get_db_variable(db: str, varname: str, docker_default: str,
                    sa_default: str = None) -> str:
    """
    Retrieve variables taking into account env overrides and wetter we are
    running in Docker or standalone (development)

    :rtype: str
    :param db: The database for which we are retrieving settings
    :param varname: The variable to retrieve
    :param docker_default: The default value (Running in docker)
    :param sa_default: The default value (Running standalone)
    :return: The applicable value of the requested variable
    """
    return get_variable(
        f"{db}_DB_{varname}_OVERRIDE".upper(),
        docker_default, sa_default)


def get_variable(varname, docker_default: str, sa_default: str = None):
    """
    Retrieve an arbitrary env. variable and choose defaults based on the env.
    :rtype: str
    :param varname: The variable to retrieve
    :param docker_default: The default value (Running in docker)
    :param sa_default: The default value (Running standalone)
    :return: The applicable value of the requested variable
    """
    sa_default = docker_default if sa_default is None else sa_default
    return os.getenv(varname, docker_default if in_docker() else sa_default)


def get_db_settings(
        db: str, docker_host: str,
        localport: str, user: str = '') -> Dict[str, str]:
    """
    Get the complete settings for a given database. Taking all possible
    environments into account.

    :rtype: Dict[str, str]
    :param db:
    :param docker_host:
    :param localport:
    :param user
    :return: A dict containing all settings:
             'username', 'password', 'host', 'port' and 'db'
    """

    if not user:
        user = db

    return {
        'username': get_db_variable(
            db=db, varname='user', docker_default=user),
        'password': get_db_variable(
            db=db, varname='password',
            docker_default='insecure'),
        'host': get_db_variable(
            db=db, varname='host',
            docker_default=docker_host,
            sa_default='localhost'),
        'port': get_db_variable(
            db=db, varname='port', docker_default='5432',
            sa_default=localport),
        'db': get_db_variable(
            db=db, varname='database', docker_default=db)
    }


def get_redis():
    try:
        redis_db = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT)
        redis_time = redis_db.time()
    except redis.exceptions.ConnectionError:
        redis_db = None
    return redis_db
