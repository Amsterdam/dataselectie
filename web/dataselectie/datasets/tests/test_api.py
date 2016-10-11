from django.test import Client
from json import loads

from urllib.parse import urlencode
from django.core.management import call_command
from django.test import TestCase
from datasets.bag import models
from datasets.tests import fixture_utils

class ESTestCase(TestCase):
    """
    TestCase for using with elastic search to reset the elistic index
    """
    @classmethod
    def rebuild_elastic_index(cls):
        """
        Rebuild the elastic search index for tests
        """
        call_command('elastic_indices', '--build', verbosity=0, interactive=False)


class DataselectieApiTest(ESTestCase):

    @classmethod
    def setUpClass(cls):
        super(ESTestCase, cls).setUpClass()
        fixture_utils.create_nummeraanduiding_fixtures()
        cls.rebuild_elastic_index()

    def setUp(self):
        self.client = Client()

    def test_get_dataselectie_bag(self):
        """
        Fetch all records (gets the first 100 records)
        """
        q = dict(page=1)
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))

        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], models.Nummeraanduiding.objects.count())
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bag_stadsdeel(self):
        """
        Test the elastic while querying on field `stadsdeel_naam` top-down
        """
        q = dict(page=1, stadsdeel_naam='Centrum')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 9)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bag_stadsdeel_code(self):
        """
        Test the elastic while querying on field `stadsdeel_code`
        """
        q = dict(page=1, stadsdeel_code='A')  # Centrum
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 9)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bag_ggw_naam(self):
        """
        Test the elastic while querying on field `ggw_naam`
        """
        q = dict(page=1, ggw_naam='Centrum-West')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 1)
        self.assertEqual(res['page_count'], 1)


    def test_get_dataselectie_bag_buurtcombinatie_naam(self):
        """
        Test the elastic while querying on field `buurtcombinatie_naam`
        """
        q = dict(page=1, buurtcombinatie_naam='Burgwallen-Nieuwe Zijde')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 1)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bag_buurtcombinatie_code(self):
        """
        Test the elastic while querying on field `buurtcombinatie_code`
        """
        q = dict(page=1, buurtcombinatie_code='01')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 1)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bag_buurt_naam(self):
        """
        Test the elastic while querying on field `buurt_naam`
        """
        q = dict(page=1, buurt_naam='Hemelrijk')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 2)
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bag_postcode(self):
        """
        Test the elastic while querying on field `buurt_naam`
        """
        q = dict(page=1, postcode='1012AA')
        response = self.client.get('/dataselectie/bag/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 5)
        self.assertEqual(res['page_count'], 1)

    def tearDown(self):
        pass
