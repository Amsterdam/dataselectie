from .fixture_utils import JSON
from .factories import HandelsRegisterFactory
# Packages
from django.conf import settings
from django.test import Client, TestCase
from elasticsearch import Elasticsearch
from django.core.management import call_command
# Project
from ..documents import meta_from_handelsregister


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
        call_command('elastic_indices', '--build', verbosity=0, interactive=False)
        es.cluster.health(wait_for_status='yellow',
                          wait_for_active_shards=0,
                          timeout="320s")


class DataselectieApiTest(ESTestCase):
    # multi_db = True

    @classmethod
    def setUpTestData(cls):
        super(ESTestCase, cls).setUpTestData()
        cls.rebuild_elastic_index()

    def setUp(self):
        self.client = Client()


class DocumentTest(TestCase):
    def test_create_from_json(self):
        hrs = []
        for x in range(20):
            hrs.append(HandelsRegisterFactory.create())

        for h in hrs:
            r = meta_from_handelsregister(h)

            self.assertIsInstance(r['betrokkenen'], list)
            self.assertIsInstance(r['betrokkenen_0'], dict)
            self.assertIsInstance(r['betrokkenen_0_rol'], str)
