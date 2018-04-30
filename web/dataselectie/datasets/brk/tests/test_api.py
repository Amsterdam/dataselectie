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
from datasets.brk.tests import fixture_utils as brk
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
        brk.create_eigendom()

        cls.rebuild_elastic_index()

    def setUp(self):
        brk.create_geo_tables()

        self.client = Client()
        self.setup_authorization()

    def test_get_geodata_withzoom_withoutbbox(self):
        # no zoom should work, takes default
        q = {'categorie': 1}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_hr_r)
        self.assertEqual(response.status_code, 200)

        # zoom < 13 should work
        q['zoom'] = 12
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_hr_r)
        self.assertEqual(response.status_code, 200)

        # zoom > 13 requires bbox
        q['zoom'] = 13
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_hr_r)
        self.assertEqual(response.status_code, 400)

        q['bbox'] = brk.get_bbox()
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_hr_r)
        self.assertEqual(response.status_code, 200)

    def test_get_geodata_withoutbbox(self):
        # no zoom should work, takes default
        q = {'categorie': 1, 'zoom': 14}
        q['bbox'] = brk.get_bbox()
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_hr_r)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        pass
