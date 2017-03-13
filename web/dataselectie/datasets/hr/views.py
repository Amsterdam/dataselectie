# Python
# Packages
from collections import OrderedDict
from itertools import chain

from django.db.models import QuerySet
from django.db.models.expressions import RawSQL

from datasets.generic.views_mixins import CSVExportView, GeoLocationSearchView, TableSearchView
from datasets.hr import models as hrmodels
from datasets.hr.queries import meta_q


class HrBase(object):
    """
    Base class mixing for data settings
    """
    index = 'DS_INDEX'

    raw_fields = []
    default_search = 'term'
    keywords = [
        'subcategorie', 'hoofdcategorie', 'handelsnaam', 'sbi_code', 'sbi_omschrijving',
        'buurt_naam', 'buurtcombinatie_naam', 'ggw_naam', 'stadsdeel_naam', 'postcode',
        '_openbare_ruimte_naam'
    ]
    keyword_mapping = {
        'buurt_naam': 'bezoekadres_buurt_naam',
        'buurtcombinatie_naam': 'bezoekadres_buurtcombinatie_naam',
        'ggw_naam': 'bezoekadres_ggw_naam',
        'stadsdeel_naam': 'bezoekadres_stadsdeel_naam',
        'postcode': 'bezoekadres_postcode',
        'woonplaats': 'bezoekadres_plaats',
        '_openbare_ruimte_naam': 'bezoekadres_openbare_ruimte',
        'naam': 'bezoekadres_openbare_ruimte',
    }
    selection = []

    def process_huisnummer_toevoeging(self, source):
        """
        Sloop huisnummer en huisletter uit de toevoeging
        :param source:
        :return: toevoeging zonder huisnummer
        """
        if source.get('bezoekadres_huisnummertoevoeging', False):
            hnm = [h for h in source['bezoekadres_huisnummertoevoeging'].split()
                   if h not in (
                       str(source['bezoekadres_huisnummer']), source['bezoekadres_huisletter'])]
            return ''.join(hnm)


class HrGeoLocationSearch(HrBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, True)


class HrSearch(HrBase, TableSearchView):
    def elastic_query(self, query: dict) -> dict:
        return meta_q(query, True)


class HrCSV(HrBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    name_conv = {'handelsnaam': 'naam'}

    hdrs = (('kvk_nummer', True, 'KvK-nummer', True),
            ('handelsnaam', True, 'Eerste handelsnaam', True),
            ('non_mail', True, 'Indicatie non-mailing', True),
            ('bezoekadres_volledig_adres', True, 'Bezoekadres (KvK HR)', True),
            ('bezoekadres_correctie', True, 'Indicatie bezoekadres geschat o.b.v BAG', True),
            ('bezoekadres_openbare_ruimte', True, 'Openbare ruimte bezoekadres (BAG)', True),
            ('bezoekadres_huisnummer', False, 'Huisnummer bezoekadres (BAG)', True),
            ('bezoekadres_huisletter', False, 'Huisletter bezoekadres (BAG)', True),
            ('bezoekadres_toevoeging', False, 'Huisnummertoevoeging bezoekadres (BAG)',
             True),
            ('bezoekadres_postcode', False, 'Postcode bezoekadres (BAG)', True),
            ('bezoekadres_plaats', False, 'Woonplaats bezoekadres (BAG)', True),
            ('postadres_volledig_adres', True, 'Postadres (KvK HR)', True),
            ('postadres_correctie', True, 'Indicatie postadres geschat o.b.v BAG', True),
            ('postadres_openbare_ruimte', True, 'Openbare ruimte postadres (BAG)', True),
            ('postadres_huisnummer', True, 'Huisnummer postadres (BAG)', True),
            ('postadres_huisletter', True, 'Huisletter postadres (BAG)', True),
            ('postadres_huisnummertoevoeging', True, 'Huisnummertoevoeging postadres (BAG)', True),
            ('postadres_postcode', True, 'Postcode postadres (BAG)', True),
            ('postadres_plaats', True, 'Woonplaats postadres (BAG)', True),
            ('hoofdcategorie', True, 'Hoofdcategorie', True),
            ('subcategorie', True, 'Subcategorie', True),
            ('sbi_omschrijving', True, 'SBI-omschrijving', True),
            ('sbi_code', True, 'SBI-code', True),
            ('datum_aanvang', True, 'Datum aanvang', True),
            ('datum_einde', True, 'Datum einde', True),
            ('eigenaar_naam', True, 'Naam eigenaar(en)', True))

    headers = [h[0] for h in hdrs if h[3]]
    pretty_headers = [h[2] for h in hdrs if h[3]]
    headers_hr = [h[0] for h in hdrs if h[3] and h[1]]

    def elastic_query(self, query):
        return meta_q(query, False, False)

    def paginate(self, offset, q: dict) -> dict:
        if 'size' in q:
            del (q['size'])
        return q
