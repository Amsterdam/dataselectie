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
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hr_sbi_code(self):
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

        q = {'page': 1, 'sbi_code': '9003'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(len(res['object_list'][0]['sbi_codes']), 1)
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

        q = {'page': 1, 'bedrijfsnaam': 'Mundus College'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['object_list'][0]['sbi_codes'][0]['sbi_code'], '85314')
        self.assertEqual(res['page_count'], 1)

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

        q = {'page': 1, 'sub_sub_categorie': 'scholengemeenschappen', 'bedrijfsnaam': 'van puffelen'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 0)

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

    def test_get_dataselectie_hr_stadsdeel_code(self):
        """
        Test the elastic while querying on field `stadsdeel_code`
        """
        q = dict(page=1, stadsdeel_code='A')  # Centrum
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        _ = models.Nummeraanduiding.objects.count()
        self.assertEqual(res['object_count'], 10)
        self.assertEqual(res['page_count'], int(10 / settings.SEARCH_PREVIEW_SIZE + 1))

    @skip('Needs to add geo matching for this test to work')
    def test_get_dataselectie_hr_ggw_naam(self):
        """
        Test the elastic while querying on field `ggw_naam`
        """
        self.assertEqual(models.Gebiedsgerichtwerken.objects.count(), 2)
        q = {'page': 1, 'ggw_naam': 'Centrum-West'}
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        print(res)
        self.assertEqual(res['object_count'], 1)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hr_buurtcombinatie_naam(self):
        """
        Test the elastic while querying on field `buurtcombinatie_naam`
        """
        self.assertEqual(models.Buurtcombinatie.objects.count(), 8)

        q = dict(page=1, buurtcombinatie_naam='Burgwallen-Nieuwe Zijde')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 8)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hr_buurtcombinatie_code(self):
        """
        Test the elastic while querying on field `buurtcombinatie_code`
        """
        q = dict(page=1, buurtcombinatie_code='A01')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 8)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hr_buurt_naam(self):
        """
        Test the elastic while querying on field `buurt_naam`
        """
        q = dict(page=1, buurt_naam='Hemelrijk')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 3)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hr_postcode(self):
        """
        Test the elastic while querying on field `buurt_naam`
        """

        q = dict(page=1, postcode='1012AA')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        postcode_count = models.Nummeraanduiding.objects.filter(postcode=q['postcode']).count()
        self.assertEqual(res['object_count'], postcode_count)
        self.assertEqual(res['page_count'], int(postcode_count / settings.SEARCH_PREVIEW_SIZE + 1))

    def test_setting_raw_fields(self):
        """
        Tests that the query generated adds raw where it is needed
        """
        table_view = views.BagSearch()
        filter_dict = {}
        extra_field = 'this_is_clearly_not_a_field_in_elastic_so_we_can_use_it'
        fields = table_view.raw_fields + [extra_field]
        for item in fields:
            filter_dict.update(table_view.get_term_and_value(item, 'Value'))
        # Now to check that every field in the raw has the .raw finish but not the last item
        for field in table_view.raw_fields:
            self.assertIn('{}.raw'.format(field), filter_dict.keys())
            self.assertNotIn(field, filter_dict.keys())
        # Making sure the not raw field is in without the raw
        self.assertIn(extra_field, filter_dict.keys())
        self.assertNotIn('{}.raw'.format(extra_field), filter_dict.keys())

    def tearDown(self):
        pass
