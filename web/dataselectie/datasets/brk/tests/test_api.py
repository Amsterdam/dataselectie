import json
import logging
# Python
from urllib.parse import urlencode

# Packages
from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.management import call_command
from django.test import Client, TestCase
from elasticsearch import Elasticsearch

from datasets.bag.tests import fixture_utils as bag
from datasets.brk.tests import fixture_utils as brk
from datasets.brk.tests.factories import create_brk_data
from datasets.brk.views import _prepare_queryparams_for_shape
# Project
from datasets.generic.tests.authorization import AuthorizationSetup

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
        brk.create_geo_data()

        self.client = Client()
        self.setup_authorization()

    def test_get_geodata_withzoom_withoutbbox(self):
        # no zoom should work, takes default
        q = {'categorie': 1}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertEqual(response.status_code, 200)

        # zoom < 13 should work
        q['zoom'] = 12
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertEqual(response.status_code, 200)

        # zoom >= 13 requires bbox
        q['zoom'] = 13
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertEqual(response.status_code, 400)

    def test_get_geodata_with_bbox(self):
        q = {'categorie': 1, 'zoom': 14}
        q['bbox'] = brk.get_bbox_leaflet()
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertEqual(response.status_code, 200)

    def test_get_geodata_appartementen(self):
        q = {'categorie': 3, 'zoom': 12, 'bbox': brk.get_bbox_leaflet()}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['appartementen']), 0)
        q['zoom'] = 13
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['appartementen']), 1)

    def test_get_geodata_eigenpercelen(self):
        q = {'categorie': 3, 'bbox': brk.get_bbox_leaflet()}

        for zoom in range(8, 14):
            q['zoom'] = zoom
            response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                       **self.header_auth_scope_brk_plus)
            self.assertEqual(response.status_code, 200)
            self.assertGeoJSON(response.json()['eigenpercelen'])

    def test_get_geodata_nieteigenpercelen(self):
        q = {'categorie': 3, 'bbox': brk.get_bbox_leaflet()}

        for zoom in range(8, 14):
            q['zoom'] = zoom
            response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                       **self.header_auth_scope_brk_plus)
            self.assertEqual(response.status_code, 200)
            self.assertGeoJSON(response.json()['niet_eigenpercelen'])

    def test_get_geodata_gebied_buurt(self):
        q = {'categorie': 3, 'zoom': 14, 'bbox': brk.get_bbox_leaflet(), 'buurt': '1'}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

        q['buurt'] = '20'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response, zoomed_in=True)

        q['zoom'] = 11
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response)

        q['buurt'] = '1'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

    def test_get_geodata_with_shape(self):
        q = {'categorie': 3, 'zoom': 14, 'bbox': brk.get_bbox_leaflet(),
             'buurt': '1', 'shape': brk.get_selection_shape()}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

        q['buurt'] = '20'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response, zoomed_in=True)

        q['zoom'] = 11
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response)

        q['buurt'] = '1'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

    def test_get_geodata_gebied_wijk(self):
        q = {'categorie': 3, 'zoom': 14, 'bbox': brk.get_bbox_leaflet(), 'wijk': '3630012052028'}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

        q['wijk'] = '3630012052036'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response, zoomed_in=True)

        q['zoom'] = 11
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response)

        q['wijk'] = '3630012052028'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

    def test_get_geodata_gebied_ggw(self):
        q = {'categorie': 3, 'zoom': 14, 'bbox': brk.get_bbox_leaflet(), 'ggw': 'DX02'}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

        q['ggw'] = 'DX01'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response, zoomed_in=True)

        q['zoom'] = 11
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response)

        q['ggw'] = 'DX02'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

    def test_get_geodata_gebied_stadsdeel(self):
        q = {'categorie': 3, 'zoom': 14, 'bbox': brk.get_bbox_leaflet(), 'stadsdeel': '03630000000019'}
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

        q['stadsdeel'] = '03630000000018'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response, zoomed_in=True)

        q['zoom'] = 11
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidMatching(response)

        q['stadsdeel'] = '03630000000019'
        response = self.client.get(BRK_GEO_QUERY.format(urlencode(q)),
                                   **self.header_auth_scope_brk_plus)
        self.assertValidEmpty(response)

    def assertValidMatching(self, response, zoomed_in=False):
        self.assertEqual(response.status_code, 200)
        if zoomed_in:
            self.assertEqual(len(response.json()['appartementen']), 1)
        else:
            self.assertEqual(len(response.json()['appartementen']), 0)
        self.assertGeoJSON(response.json()['eigenpercelen'])
        self.assertGeoJSON(response.json()['niet_eigenpercelen'])

    def assertValidEmpty(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['appartementen']), 0)
        self.assertIsNone(response.json()['eigenpercelen'])
        self.assertIsNone(response.json()['niet_eigenpercelen'])

    def assertGeoJSON(self, geojson):
        self.assertIsInstance(geojson, dict)
        self.assertIn('type', geojson)
        self.assertIn('geometries', geojson)

    def test_shape_parameter(self):
        fixture = {
            'shape': "[[4.890712,52.373579],[4.8920548,52.3736018],[4.8932629,52.3732028],"
                     "[4.8929459,52.3727335],[4.8906613,52.3727228]]"}
        _prepare_queryparams_for_shape(fixture)

        self.assertIsInstance(fixture['shape'], Polygon)
        dict_of_polygon = json.loads(fixture['shape'].geojson)
        expected_dict = json.loads(
            '{"type":"Polygon","coordinates":[[[4.890712,52.373579],[4.8920548,52.3736018],'
            '[4.8932629,52.3732028],[4.8929459,52.3727335],[4.8906613,52.3727228],'
            '[4.890712,52.373579]]]}')
        self.assertDictEqual(dict_of_polygon, expected_dict)

        fixture = {'shape': "[]"}
        _prepare_queryparams_for_shape(fixture)

        self.assertNotIn('shape', fixture)