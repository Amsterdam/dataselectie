# Packages
from django.core.management import call_command
from django.test import TestCase

from datasets.bag.tests.fixture_utils import create_nummeraanduiding_fixtures
from datasets.data.models import DataSelectie
from datasets.hr.factories.build_hr_data import fill_geo_table
from datasets.hr.factories.factorieshr import create_dataselectie_set


class DataselectieHrImportTest(TestCase):

    def test_datasel_import(self):

        create_nummeraanduiding_fixtures()
        create_dataselectie_set()

        fill_geo_table()
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
        self.assertEqual(len(row.api_json['sbi_codes']), 1)
        self.assertEqual(len(row.api_json['betrokkenen']), 1)
        self.assertIsInstance(row.api_json['geometrie'], list)
        self.assertEqual(row.api_json['postadres_volledig_adres'][:9],
                         'vol_adres')
