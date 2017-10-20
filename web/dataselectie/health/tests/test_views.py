# from unittest.mock import Mock
# from django.http import HttpResponse
from datasets.bag.tests.test_api import ESTestCase
from datasets.bag.tests import fixture_utils

from datasets.hr.tests.factories import create_hr_data
from django.core.management import call_command

from django.test import Client
import time


class StatusViewsTest(ESTestCase):

    @classmethod
    def setUpTestData(cls):
        super(ESTestCase, cls).setUpTestData()

    def setUp(self):
        self.client = Client()

    def test_status_health(self):
        """check health url"""
        # fill data in elastic.
        fixture_utils.create_nummeraanduiding_fixtures()
        create_hr_data()

        # load all BAG and HR in elastic.
        self.rebuild_elastic_index()
        # give elastic time to proces new data
        time.sleep(2)

        response = self.client.get('/status/health')
        # Making sure its a 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'Data OK')

    def test_status_health_not_ok(self):

        # empty the indexes.
        call_command(
            'elastic_indices', '--recreate', verbosity=0,
            interactive=False)

        response = self.client.get('/status/health')
        # Making sure its a 500
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'Elastic data missing.')
