from unittest.mock import Mock
from django.http import HttpResponse
from corsheaders.middleware import CorsMiddleware
from rest_framework.test import APITestCase

# from datasets.bag.tests import factories

class DataselectieApiTest(APITestCase):

    # Get by id
    def test_get_by_woonplaats(self):

        response = self.client.get('/zelfbediening/bag/')
        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        # self.assertIn('Connectivity OK', response.data)
        # # Testing 404 on non existing id
        # response = self.client.get('/panorama/opnamelocatie/PANO_NOT_DEFINED/')
        # self.assertEqual(response.status_code, 404)
