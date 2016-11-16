# Python
from rapidjson import loads
from unittest import skip
from urllib.parse import urlencode
# Packages
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase
from elasticsearch import Elasticsearch
# Project
from datasets.bag import models, views
from ...bag.tests.fixture_utils import create_nummeraanduiding_fixtures


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
        call_command('elastic_indices', '--delete', verbosity=0, interactive=False)
        call_command('elastic_indices', '--build', verbosity=0, interactive=False)
        es.cluster.health(wait_for_status='yellow',
                          wait_for_active_shards=0,
                          timeout="320s")


class DataselectieApiTest(ESTestCase):

    @classmethod
    def setUpTestData(cls):
        super(ESTestCase, cls).setUpTestData()
        create_nummeraanduiding_fixtures()
        cls.rebuild_elastic_index()

    def setUp(self):
        self.client = Client()

    def check_in(self, objects, field, values):
        for o in objects:
            self.assertIn(o[field], values)

    def test_get_dataselectie_hr(self):
        """
        Fetch all records (gets the first 100 records)
        """
        q = {'page': 1}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))

        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 3)
        self.assertEqual(len(res['object_list']), 3)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hr_sbi_code1(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': '85314'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(len(res['object_list'][0]['sbi_codes']), 1)
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hr_sbi_code2(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': '9003'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 2)
        self.check_in(res['object_list'], 'id', ('000000000086', '000000002216'))
        self.assertEqual(len(res['object_list'][0]['sbi_codes']), 2)
        self.assertEqual(res['object_list'][0]['sbi_codes'][1]['sbi_code'], '9003')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bedrijfsnaam(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'bedrijfsnaam': 'Mundus College'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_sub_sub_categorie(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sub_sub_categorie': 'Brede scholengemeenschappen'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

        q = {'page': 1, 'sub_sub_categorie': 'scholengemeenschappen'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_subcategorie(self):
        q = {'page': 1, 'subcategorie': 'groothandel'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000001198')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '4639')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hoofd_categorie(self):
        q = {'page': 1, 'hoofdcategorie': 'cultuur'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 2)
        self.check_in(res['object_list'], 'id', ('000000002216', '000000000086'))
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_not_found(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sub_sub_categorie': 'scholengemeenschappen', 'bedrijfsnaam': 'van puffelen'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 0)

    def test_get_dataselectie_combinaties(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sub_sub_categorie': 'scholengemeenschappen', 'bedrijfsnaam': 'Mundus College'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

        q = {'page': 1, 'stadsdeel_naam': 'centrum', 'bedrijfsnaam': 'Mundus College'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

        q = {'page': 1, 'subcategorie': 'groothandel', 'stadsdeel_naam': 'Centrum'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000001198')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '4639')
        self.assertEqual(res['page_count'], 1)

    def tearDown(self):
        pass
