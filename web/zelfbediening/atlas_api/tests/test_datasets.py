from rest_framework.test import APITestCase

from datasets.nap.tests import factories as factories_nap
from datasets.meetbouten.tests import factories as factories_meetbouten


class BrowseDatasetsTestCase(APITestCase):
    """
    Verifies that browsing the API works correctly.
    """

    datasets = [
        'nap/peilmerk',
        'meetbouten/meetbout',
        'meetbouten/referentiepunt',
        'meetbouten/rollaag',
        'meetbouten/meting',
    ]

    def setUp(self):
        factories_nap.PeilmerkFactory.create()
        factories_meetbouten.MeetboutFactory.create()
        factories_meetbouten.ReferentiepuntFactory.create()
        factories_meetbouten.RollaagFactory.create()
        factories_meetbouten.MetingFactory.create()

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            self.assertEqual(response.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(response['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))

            self.assertIn('count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(response.data['count'], 0, 'Wrong result count for {}'.format(url))

    def test_details(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.assertEqual(detail.status_code, 200, 'Wrong response code for {}'.format(url))
            self.assertEqual(detail['Content-Type'], 'application/json', 'Wrong Content-Type for {}'.format(url))
            self.assertIn('_display', detail.data)
