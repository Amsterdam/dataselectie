# Python
from json import loads
from unittest import skip
from urllib.parse import urlencode
# Packages
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase
from elasticsearch import Elasticsearch
# Project
from datasets.bag import models, views
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
        call_command('elastic_indices', '--build', verbosity=0, interactive=False)
        es.cluster.health(wait_for_status='yellow',
                          wait_for_active_shards=0,
                          timeout="320s")


class DataselectieExportTest(ESTestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls):
        super(ESTestCase, cls).setUpTestData()
        fixture_utils.create_nummeraanduiding_fixtures()
        cls.rebuild_elastic_index()

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass
