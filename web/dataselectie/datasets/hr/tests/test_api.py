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
from .factories import create_hr_data

HR_BASE_QUERY = '/dataselectie/hr/?{}'
HR_GEO_QUERY = '/dataselectie/hr/geolocation/?{}'

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

        call_command(
            'elastic_indices', '--recreate', 'hr', verbosity=0,
            interactive=False
        )

        call_command(
            'elastic_indices', '--build', 'hr', verbosity=0,
            interactive=False)

        es.cluster.health(
            wait_for_status='yellow',
            wait_for_active_shards=0,
            timeout="320s")


class DataselectieApiTest(ESTestCase, AuthorizationSetup):

    @classmethod
    def setUpTestData(cls):
        super(ESTestCase, cls).setUpTestData()
        create_hr_data()
        cls.rebuild_elastic_index()

    def setUp(self):
        self.client = Client()
        self.setup_authorization()

    def check_in(self, objects, field, values):
        for o in objects:
            self.assertIn(o[field], values)

    def test_get_dataselectie_hr(self):
        """
        Fetch all records (gets the first 100 records)
        """
        q = {'page': 1}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = response.json()
        self.assertEqual(len(res['object_list']), 6)
        self.assertEqual(res['page_count'], 1)
        self.assertIn('aggs_list', res)
        self.assertEqual(res['object_count'], 6)
        self.assertIn('hoofdcategorie', res['aggs_list'])

        testcats = {
            'cultuur, sport, recreatie': 1,
            "productie, installatie, reparatie": 1,
            'handel, vervoer, opslag': 3,
            'bouw': 1,
            'zakelijke dienstverlening': 3,
            'informatie, telecommunicatie': 1,
            'overige niet hierboven genoemd': 2,
        }

        self.assertIn('buckets', res['aggs_list']['hoofdcategorie'])

        self.assertEqual(len(res['aggs_list']['hoofdcategorie']['buckets']), 7)

        hoofdcategorieen = [
            (k['key'], k['doc_count'])
            for k in
            res['aggs_list']['hoofdcategorie']['buckets']
        ]

        for cat, count in hoofdcategorieen:
            self.assertEqual(testcats[cat], count, cat)

        self.assertIn('subcategorie', res['aggs_list'])
        self.assertIn('buurt_naam', res['aggs_list'])
        self.assertIn('buckets', res['aggs_list']['buurt_naam'])
        self.assertIn('buurtcombinatie_naam', res['aggs_list'])
        self.assertIn('buckets', res['aggs_list']['buurtcombinatie_naam'])

        # test sorting
        names = [obj['handelsnaam'] for obj in res['object_list']]
        names2 = list(names)
        names2.sort()
        log.info(names)
        log.info(names2)
        self.assertEqual(names, names2, 'sort error')

    def test_get_dataselectie_invalidparm(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': 'notfound'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(len(res['object_list']), 0)

    def test_get_dataselectie_hr_sbi_code(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': '4'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 4)

        sbis = [o['sbi_code'] for o in res['object_list']]
        log.info(sbis)
        sbis = sum(sbis, [])
        log.info(sbis)

        self.assertIn('47544', sbis)
        self.assertIn('46471', sbis)
        self.assertIn('4110', sbis)
        self.assertIn('4120', sbis)

    def test_get_dataselectie_hr_multi_sbi_code(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': '[41,351]'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 3)

        sbis = [o['sbi_code'] for o in res['object_list']]
        log.info(sbis)
        sbis = sum(sbis, [])
        log.info(sbis)

        self.assertIn('35111', sbis)
        self.assertIn('4110', sbis)
        self.assertIn('4120', sbis)

    def test_get_dataselectie_hr_match_sbi_code(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': '35111'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 1)
        self.assertIn('35111', res['object_list'][0]['sbi_code'])
        self.assertEqual(res['page_count'], 1)

        sbi_bucket = res['aggs_list']['sbi_code']['buckets']
        sbi_bucket2 = res['aggs_list']['sbi_l2']['buckets']
        sbi_bucket3 = res['aggs_list']['sbi_l3']['buckets']
        sbi_bucket4 = res['aggs_list']['sbi_l4']['buckets']

        self.assertTrue(len(sbi_bucket2) > 0)
        self.assertTrue(len(sbi_bucket3) > 0)
        self.assertTrue(len(sbi_bucket4) > 0)

        for agg_key_count in sbi_bucket:
            key = agg_key_count['key']
            self.assertTrue('35111'.startswith(key))

    def test_get_dataselectie_hr_multiple_sbi_code(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': '[35111,9002]'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 2)
        collect_codes = list(res['object_list'][0]['sbi_code'])
        collect_codes.extend(res['object_list'][1]['sbi_code'])

        self.assertIn('35111', collect_codes)
        self.assertIn('9002', collect_codes)

        self.assertEqual(res['page_count'], 1)

        sbi_bucket = res['aggs_list']['sbi_code']['buckets']
        self.assertTrue(len(sbi_bucket) > 0)
        for agg_key_count in sbi_bucket:
            key = agg_key_count['key']
            self.assertTrue(
                '35111'.startswith(key) or
                '9002'.startswith(key)
            )

    def test_get_dataselectie_hr_sbi_code2(self):
        """

        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'sbi_code': '9002'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(
            res['object_list'][0]['sbi_code'],
            ['9002', '5030', '4120', '7320']
        )
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_bedrijfsnaam(self):
        """
        Test elastic querying on field `sbi_code` top-down
        """
        q = {'page': 1, 'handelsnaam': 'Armada Producties'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        res = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(
            res['object_list'][0]['sbi_code'],
            ['9002', '5030', '4120', '7320']
        )
        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_subcategorie(self):
        q = {'page': 1,
             'subcategorie': 'vervoer'}

        response = self.client.get(HR_BASE_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(
            res['object_list'][0]['sbi_code'],
            ['9002', '5030', '4120', '7320'])
        self.assertEqual(res['page_count'], 1)
        self.assertEqual(res['object_count'], 1)

    def test_get_dataselectie_hoofd_categorie(self):
        q = {'page': 1, 'hoofdcategorie': 'cultuur, sport, recreatie'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 1)
        # self.check_in(res['object_list'], 'vestiging_id',
        #              ('000000002216', '000000000086'))
        self.assertEqual(res['page_count'], 1)
        self.assertEqual(res['object_count'], 1)

    def test_get_dataselectie_sbi_omschrijving(self):
        q = {
            'page': 1,
            'sbi_omschrijving': 'Dienstverlening voor uitvoerende kunst'
        }

        response = self.client.get(HR_BASE_QUERY.format(urlencode(q)), **self.header_auth_scope_hr_r)
        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['page_count'], 1)
        self.assertEqual(res['object_count'], 1)

    def test_get_dataselectie_parent(self):
        """
        Test elastic querying on field in parent
        """
        q = {
            'page': 1, 'stadsdeel_naam': 'Centrum',
            'handelsnaam': 'Funky Solutions',
        }

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(len(res['object_list']), 1)

        self.assertEqual(
            res['object_list'][0]['sbi_code'],
            ['47544', '6201', '74201'],
            'sbi codes should match'
        )

        self.assertEqual(res['page_count'], 1)

    def test_get_dataselectie_parent2(self):
        q = {
            'page': 1,
            'postcode': '1075EC'  # Rietveld fixture
        }
        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)
        res = response.json()

        self.assertEqual(len(res['object_list']), 1)
        self.assertEqual(res['object_list'][0]['sbi_code'], ['46471'])
        self.assertEqual(res['page_count'], 1)
        self.assertEqual(res['object_count'], 1)

    def test_get_dataselectiehr_geolocation(self):
        """
        Test elastic for returning only geolocation
        """
        response = self.client.get('/dataselectie/hr/geolocation/',
                                   **self.header_auth_scope_hr_r)

        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = response.json()
        self.assertEqual(
            res['object_count'], 6)
        self.assertNotIn('aggs_list', res)

    def test_get_dataselectiehr_geolocation_no_auth(self):
        response = self.client.get('/dataselectie/hr/geolocation/')

        self.assertEqual(response.status_code, 401)

    def test_get_dataselectie_hr_shape_limit(self):
        """
        Test querying on geolocation
        """
        q = {
            'shape': '[[3.315526,47.9757],[3.315527,47.9757],[3.315527,47.9758],[3.315526,47.9758]]'}  # noqa

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEqual(response.status_code, 200)

        res = response.json()
        self.assertEqual(res['object_count'], 2)

    def test_get_dataselectiehr_geolocation2(self):
        """
        Test elastic for returning only geolocation
        """
        q = {
            'shape': '[[3.315526,47.9757],[3.315527,47.9757],[3.315527,47.9758],[3.315526,47.9758]]'}   # noqa

        response = self.client.get(HR_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_hr_r)

        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = response.json()
        self.assertEqual(
            res['object_count'], 2)
        self.assertNotIn('aggs_list', res)

    # Following tests also check auth by definition of the hiding rules:
    def test_hr_hides_afgeschermd(self):
        q = {'page': 1, 'handelsnaam': 'Armada Producties'}

        response = self.client.get(
            HR_BASE_QUERY.format(urlencode(q)),
            **self.header_auth_scope_hr_r)

        self.assertEquals(response.status_code, 200)
        res_json = response.json()
        self.assertEquals(res_json['object_count'], 1)
        self.assertEquals(
            res_json['object_list'][0]['postadres_afgeschermd'], True)
        self.assertEquals(
            res_json['object_list'][0]['bezoekadres_afgeschermd'], False)
        self.assertEquals(
            res_json['object_list'][0]['non_mailing'], False)

        # publiek request ziet alleen handelsnaam en sbi codes
        # res = self.client.get(HR_BASE_QUERY.format(urlencode(q)),
        #                      **self.header_auth_default)

        # self.assertEquals(res.status_code, 200)
        # res_json = res.json()
        # self.assertEquals(res_json['object_count'], 1)

        # self.assertIn('handelsnaam', res_json['object_list'][0])
        # self.assertIn('hoofdcategorie', res_json['object_list'][0])
        # self.assertIn('subcategorie', res_json['object_list'][0])

        # publiek request ziet alleen handelsnaam en sbi codes
        # res = self.client.get(HR_BASE_QUERY.format(urlencode(q)))
        # self.assertEquals(res.status_code, 200)
        # res_json = res.json()
        # self.assertEquals(res_json['object_count'], 1)

        # self.assertIn('handelsnaam', res_json['object_list'][0])
        # self.assertIn('hoofdcategorie', res_json['object_list'][0])
        # self.assertIn('subcategorie', res_json['object_list'][0])

    def test_hr_hides_nonmailing(self):
        q = {'page': 1, 'handelsnaam': 'Rietveld by Rietveld B.V.'}

        res = self.client.get(HR_BASE_QUERY.format(urlencode(q)),
                              **self.header_auth_scope_hr_r)

        self.assertEquals(res.status_code, 200)
        res_json = res.json()
        self.assertEquals(res_json['object_count'], 1)
        self.assertEquals(
            res_json['object_list'][0]['postadres_afgeschermd'], False)
        self.assertEquals(
            res_json['object_list'][0]['bezoekadres_afgeschermd'], False)
        self.assertEquals(
            res_json['object_list'][0]['non_mailing'], True)

        # res = self.client.get(
        #     HR_BASE_QUERY.format(urlencode(q)), **self.header_auth_default)

        # self.assertEquals(res.status_code, 200)
        # res_json = loads(res.content.decode('utf-8'))
        # self.assertEquals(res_json['object_count'], 1)

        # self.assertNotIn('postadres_afgeschermd', res_json['object_list'][0])
        # self.assertNotIn('postadres_straatnaam', res_json['object_list'][0])
        # self.assertNotIn('bezoekadres_volledig_adres',
        #                  res_json['object_list'][0])

        # public.
        res = self.client.get(HR_BASE_QUERY.format(urlencode(q)))
        self.assertEquals(res.status_code, 401)
        # res_json = loads(res.content.decode('utf-8'))
        # self.assertEquals(res_json['object_count'], 1)
        # self.assertNotIn('postadres_afgeschermd', res_json['object_list'][0])
        # self.assertNotIn('postadres_straatnaam', res_json['object_list'][0])
        # self.assertNotIn('bezoekadres_volledig_adres',
        #                 res_json['object_list'][0])

    def tearDown(self):
        pass
