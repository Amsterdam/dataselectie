# Python
from rapidjson import loads
from urllib.parse import urlencode
# Packages
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase
from elasticsearch import Elasticsearch
# Project
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
        call_command('elastic_indices', '--recreate', verbosity=0, interactive=False)
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
        self.assertEqual(len(res['object_list']), 5)
        self.assertEqual(res['page_count'], 1)
        self.assertIn('aggs_list', res)
        self.assertIn('hoofdcategorie', res['aggs_list'])
        testcats = {'cultuur, sport, recreatie': 2,
                    'financiële dienstverlening,verhuur van roerend en onroerend goed': 2,
                    'handel, vervoer, opslag': 1,
                    'overheid, onderwijs, zorg': 1,
                    'zakelijke dienstverlening': 2}
        self.assertIn('buckets', res['aggs_list']['hoofdcategorie'])
        self.assertEqual(len(res['aggs_list']['hoofdcategorie']['buckets']), 5)
        hoofdcategorieen = [(k['key'], k['doc_count']) for k in res['aggs_list']['hoofdcategorie']['buckets']]
        for cat, count in hoofdcategorieen:
            self.assertEqual(testcats[cat], count)
        self.assertIn('subcategorie', res['aggs_list'])
        self.assertIn('buurt_naam', res['aggs_list'])
        self.assertIn('buckets', res['aggs_list']['buurt_naam'])
        self.assertIn('buurtcombinatie_code', res['aggs_list'])
        self.assertIn('buckets', res['aggs_list']['buurtcombinatie_code'])
        self.assertIn('buckets', res['aggs_list']['sbi_omschrijving'])

    def test_get_dataselectie_invalidparm(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'invalid_parm': '8539914'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 400)

        q = {'page': 1, 'sbi_code': 'notfound'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 0)

    def test_get_dataselectie_hr_sbi_code1(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        velden_in_api = ('bag_numid', 'bag_vbid', 'bedrijfsnaam', 'betrokkenen',
                         'bezoekadres_afgeschermd', 'bezoekadres_correctie',
                         'bezoekadres_volledig_adres', 'datum_aanvang',
                         'datum_einde', 'hoofdcategorieen',
                         'hoofdvestiging', 'id', 'kvk_nummer', 'locatie_type',
                         'postadres_afgeschermd', 'postadres_correctie',
                         'postadres_huisletter', 'postadres_huisnummer',
                         'postadres_huisnummertoevoeging', 'postadres_postbus_nummer',
                         'postadres_postcode', 'postadres_straat_huisnummer',
                         'postadres_straatnaam', 'postadres_toevoegingadres',
                         'postadres_volledig_adres', 'sbicodes', 'subcategorieen',
                         'vestigingsnummer', 'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
                         'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
                         'stadsdeel_naam', 'stadsdeel_code', 'woonplaats',
                         '_openbare_ruimte_naam', 'huisnummer',
                         'huisletter', 'huisnummer_toevoeging', 'postcode', 'sbi_omschrijving')
        q = {'page': 1, 'sbi_code': '85314'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))

        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertIn(res['object_list'][0]['sbicodes'], '85314')
        for fieldnm in velden_in_api:
            self.assertIn(fieldnm, res['object_list'][0])
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
        self.assertEqual(res['object_list'][0]['sbicodes'], '6420 \\ 9003')
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
        self.assertEqual(res['object_list'][0]['sbicodes'], '85314')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_subcategorie(self):
        q = {'page': 1, 'subcategorie': 'groothandel (verkoop aan andere ondernemingen, niet zelf vervaardigd)'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000000809')
        self.assertEqual(res['object_list'][0]['sbicodes'], '4639')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_hoofd_categorie(self):
        q = {'page': 1, 'hoofdcategorie': 'cultuur, sport, recreatie'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 2)
        self.check_in(res['object_list'], 'id', ('000000002216', '000000000086'))
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_sbi_omschrijving(self):
        q = {'page': 1, 'sbi_omschrijving': 'Brede scholengemeenschappen voor voortgezet onderwijs'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_parent(self):
        """
        Test elastic querying on field in parent
        """
        q = {'page': 1, 'stadsdeel_naam': 'Centrum', 'bedrijfsnaam': 'Mundus College'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000004383')
        self.assertEqual(res['object_list'][0]['sbicodes'], '85314')
        self.assertEqual(res['page_count'], 1)

        q = {'page': 1, 'subcategorie': 'groothandel (verkoop aan andere ondernemingen, '
                                        'niet zelf vervaardigd)', 'postcode': '1012AB'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)
        res = loads(response.content.decode('utf-8'))
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['id'], '000000000809')
        self.assertEqual(res['object_list'][0]['sbicodes'], '4639')
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectiehr_geolocation(self):
        """
        Test elastic for returning only geolocation
        """
        response = self.client.get('/dataselectie/hr/geolocation/')

        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(
            res['object_count'], 4)
        self.assertNotIn('aggs_list', res)

    def test_get_dataselectie_hr_shape_limit(self):
        """
        Test querying on geolocation
        """
        q = {'shape': '[[3.315526,47.9757],[3.315527,47.9757],[3.315527,47.9758],[3.315526,47.9758]]'}
        response = self.client.get('/dataselectie/hr/?{}'.format(urlencode(q)))
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(res['object_count'], 1)

    def test_get_dataselectiehr_geolocation2(self):
        """
        Test elastic for returning only geolocation
        """
        q = {'shape': '[[3.315526,47.9757],[3.315527,47.9757],[3.315527,47.9758],[3.315526,47.9758]]'}
        response = self.client.get('/dataselectie/hr/geolocation/?{}'.format(urlencode(q)))

        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = loads(response.content.decode('utf-8'))
        self.assertEqual(
            res['object_count'], 1)
        self.assertNotIn('aggs_list', res)

    def tearDown(self):
        pass
