# Packages
from urllib.parse import urlencode

from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase
from elasticsearch import Elasticsearch

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
        call_command('elastic_indices', '--recreate', verbosity=0,
                     interactive=False)
        call_command('elastic_indices', '--build', verbosity=0,
                     interactive=False)
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

    def test_complete_export_hr(self):
        response = self.client.get('/dataselectie/hr/export/')
        # assert that response st.values()[:self.preview_size]atus is 200
        self.assertEqual(response.status_code, 200)

        res = (b''.join(response.streaming_content)).decode('utf-8').strip()
        res = res.split('\r\n')
        # 6 lines: headers + 6 items
        self.assertEqual(len(res), 7)
        row2 = res[2].split(';')

        self.assertEqual(len(row2), 18)
        checkvalues = ('50326457', 'Golf 10 V.O.F.',
                       'Buitenveldertselaan 106 (3e et.) 1081AB Amsterdam',
                       'nee', 'Delflandplein', '15', 'C', '2', '1012AB',
                       'Amsterdam',
                       'Buitenveldertselaan 106 (3e et.) 1081AB Amsterdam',
                       'handel, vervoer, opslag',
                       'groothandel (verkoop aan andere ondernemingen, niet zelf vervaardigd)',
                       'Groothandel in voedings- en genotmiddelen algemeen assortiment',
                       '4639', '2010-07-01', '', 'Van Puffelen Vennoot')
        # checkvalues = ('50326457', 'Golf 10 V.O.F.',
        #                'Buitenveldertselaan 106 (3e et.) 1081AB Amsterdam',
        #                'nee', 'Delflandplein', '15', 'C', '2', '1012AB',
        #                'Amsterdam',
        #                'Buitenveldertselaan 106 (3e et.) 1081AB Amsterdam',
        #                'nee', 'Buitenveldertselaan', '106', '', '', '1081AB',
        #                'Amsterdam', 'handel, vervoer, opslag',
        #                'groothandel (verkoop aan andere ondernemingen, niet zelf vervaardigd)',
        #                'Groothandel in voedings- en genotmiddelen algemeen assortiment',
        #                '4639', '2010-07-01', '', 'Van Puffelen Vennoot')

        for idx, val in enumerate(row2):
            self.assertEqual(row2[idx], checkvalues[idx])

    def test_export_hr_subcategorie(self):
        q = {'page': 1,
             'subcategorie': 'groothandel (verkoop aan andere ondernemingen, niet zelf vervaardigd)'}
        response = self.client.get(
            '/dataselectie/hr/export/?{}'.format(urlencode(q)))
        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        res = (b''.join(response.streaming_content)).decode('utf-8').strip()

        res = res.split('\r\n')
        # 2 lines: headers + 1 items
        self.assertEqual(len(res), 2)
