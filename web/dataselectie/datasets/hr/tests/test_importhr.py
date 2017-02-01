# Packages
from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.test import TestCase

from datasets.bag.tests.fixture_utils import create_nummeraanduiding_fixtures
from datasets.data.models import DataSelectie
from datasets.hr.tests.factorieshr import create_dataselectie_set
from django.db import connections
from django.conf import settings

class DataselectieHrImportTest(TestCase):

    def test_datasel_import(self):

        create_nummeraanduiding_fixtures()
        create_dataselectie_set()
        with connections['hr'].cursor() as cursor:
            cursor.execute(
                "Insert into django_site (domain, name) Values ('{}', 'API Domain');".format(
                    settings.DATAPUNT_API_URL))

        call_command('run_import', verbosity=0, interactive=False)

        # this one is always there

        rows = DataSelectie.objects.all()
        self.assertGreater(len(rows), 0)

        fields_in_row = (
            'geometrie', 'hoofdvestiging', 'kvk_nummer', 'locatie_type',
            'naam', 'postadres_afgeschermd', 'postadres_correctie',
            'postadres_huisletter', 'postadres_huisnummer',
            'postadres_huisnummertoevoeging', 'postadres_postbus_nummer',
            'postadres_postcode', 'postadres_straat_huisnummer',
            'postadres_straatnaam', 'postadres_toevoegingadres',
            'postadres_volledig_adres', 'sbi_codes', 'vestigingsnummer',
            'datum_einde', 'datum_aanvang', 'bezoekadres_volledig_adres',
            'bezoekadres_correctie', 'bezoekadres_afgeschermd',
            'betrokkenen')


        for row in rows:
            for f in fields_in_row:
                self.assertIn(f, row.api_json)

        row = rows[0]

        self.assertGreaterEqual(len(row.api_json), 1)
        self.assertIsInstance(row.api_json['sbi_codes'], list)
        self.assertGreater(len(row.api_json['sbi_codes']), 0)
        self.assertGreater(len(row.api_json['betrokkenen']), 0)
        self.assertEqual(row.api_json['postadres_volledig_adres'][:9],
                         'vol_adres')