import logging
# Python
from urllib.parse import urlencode

# Packages
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase
from elasticsearch import Elasticsearch

# Project
from datasets.generic.tests.authorization import AuthorizationSetup
from datasets.brk.tests.factories import create_brk_data
from datasets.brk.tests.fixture_utils import create_eigendom
from datasets.bag.tests import fixture_utils as bag

BRK_BASE_QUERY = '/dataselectie/brk/?{}'
BRK_GEO_QUERY = '/dataselectie/brk/geolocation/?{}'

log = logging.getLogger(__name__)


class ESTestCase(TestCase):
    """
    TestCase for using with elastic search to reset the elastic index
    """

    @classmethod
    def rebuild_elastic_index(cls):
        """
        Rebuild the elastic search index for tests
        """
        es = Elasticsearch(hosts=settings.ELASTIC_SEARCH_HOSTS)

        call_command('elastic_indices', '--recreate', 'brk', verbosity=0)
        call_command('elastic_indices', '--build', 'brk', verbosity=0)

        es.cluster.health(
            wait_for_status='yellow',
            wait_for_active_shards=0,
            timeout="320s")


class DataselectieApiTest(ESTestCase, AuthorizationSetup):

    @classmethod
    def setUpTestData(cls):
        super(ESTestCase, cls).setUpTestData()

        bag.create_gemeente_fixture()
        bag.create_buurt_combinaties()
        bag.create_buurt_fixtures()
        bag.create_gebiedsgericht_werken_fixtures()
        bag.create_stadsdeel_fixtures()

        create_brk_data()
        create_eigendom()

        cls.rebuild_elastic_index()

    def setUp(self):
        # self.client = Client()
        # self.setup_authorization()
        pass

    def test_get_dataselectie_brk(self):
        # response = self.client.get(BRK_GEO_QUERY, **self.header_auth_scope_hr_r)
        #
        # # assert that response status is 200
        # self.assertEqual(response.status_code, 200)
        pass

    def tearDown(self):
        pass
