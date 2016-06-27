import logging

from rest_framework.test import APITestCase

import datasets.meetbouten.batch
import datasets.nap.batch

from datapunt_generic.batch import batch

from unittest import skip

from datasets.meetbouten.tests import factories as mb_factories

# from datasets.nap.tests import factories as nap_factories

log = logging.getLogger('search')


class SearchMeetbout(APITestCase):
    """
    Testing meetbouten search
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        mb_factories.MeetboutFactory(
            id=123456,
            bouwbloknummer='AB10'
        )

        mb_factories.MeetboutFactory(
            id=123451,
            bouwbloknummer='AB10'
        )

        mb_factories.MeetboutFactory(
            id=12346,
            bouwbloknummer='AB11'
        )

        batch.execute(
            datasets.meetbouten.batch.IndexMeetboutenJob())

    def test_non_matching_query(self):
        response = self.client.get(
            '/meetbouten/search/',
            dict(q="qqq"))

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        log.debug(response)
        self.assertEqual(response.data['count'], 0)

    def test_matching_query(self):
        response = self.client.get(
            '/meetbouten/search/',
            dict(q="123456"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        print(response.data)

        log.debug(response)

        self.assertEqual(response.data['count'], 1)

        first = response.data['results'][0]

        self.assertEqual(first['meetboutnummer'], "123456")
        self.assertEqual(first['bouwbloknummer'], "AB10")

    def test_query_bouwblok(self):
        response = self.client.get(
            '/meetbouten/search/', dict(q="AB10"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        log.debug(response)
        self.assertEqual(response.data['count'], 2)

        self.assertEqual(
                response.data['results'][0]['bouwbloknummer'], "AB10")
        self.assertEqual(
                response.data['results'][1]['bouwbloknummer'], "AB10")

    def test_query_boutnummer(self):
        response = self.client.get(
            "/meetbouten/search/", dict(q="1"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 3)
