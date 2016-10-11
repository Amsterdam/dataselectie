from django.test import TestCase, Client
from datasets.tests.factories import NummeraanduidingFactory, GemeenteFactory
from datasets.bag import models

class DataselectieApiTest(TestCase):

    def setUp(self):
        self.client = Client()
        # self.gemeente = GemeenteFactory()
        # for i in range(10):
        #     NummeraanduidingFactory()
        #
        # print(models.Nummeraanduiding.objects.all())


    # Get by id
    def test_get_by_woonplaats(self):
        d = models.Nummeraanduiding.objects.all()
        response = self.client.get('/dataselectie/bag/')
        # assert that response status is 200
        self.assertEqual(response.status_code, 200)

        # self.assertIn('Connectivity OK', response.data)
        # # Testing 404 on non existing id
        # response = self.client.get('/panorama/opnamelocatie/PANO_NOT_DEFINED/')
        # self.assertEqual(response.status_code, 404)

    def tearDown(self):
        pass
