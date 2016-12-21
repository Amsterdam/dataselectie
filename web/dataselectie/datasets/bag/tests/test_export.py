# Packages
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase
from elasticsearch import Elasticsearch
# Project
from datasets.bag.tests import fixture_utils


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
        call_command('elastic_indices', '--rebuild', verbosity=0, interactive=False)
        call_command('elastic_indices', '--build', verbosity=0, interactive=False)
        es.cluster.health(wait_for_status='yellow',
                          wait_for_active_shards=0,
                          timeout="320s")


class DataselectieExportTest(ESTestCase):

    @classmethod
    def setUpTestData(cls):
        super(ESTestCase, cls).setUpTestData()
        fixture_utils.create_nummeraanduiding_fixtures()
        cls.rebuild_elastic_index()

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_response_is_streaming(self):
        """Verify that the response is streaming"""
        response = self.client.get('/dataselectie/bag/export/')
        self.assertTrue(response.streaming)

    def test_complete_export_bag(self):
        response = self.client.get('/dataselectie/bag/export/')
        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = (b''.join(response.streaming_content)).decode('utf-8').strip()
        res = res.split('\r\n')
        # 11 lines: headers + 10 items
        self.assertEqual(len(res), 11)

