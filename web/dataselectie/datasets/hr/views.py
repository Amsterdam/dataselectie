# Python
# Packages
from dateutil.parser import parse

from django.conf import settings

import authorization_levels

from datasets.generic.views_mixins import CSVExportView
from datasets.generic.views_mixins import GeoLocationSearchView
from datasets.generic.views_mixins import TableSearchView
from datasets.generic.views_mixins import stringify_item_value

from datasets.hr.queries import meta_q


class HrBase(object):
    """
    Base class mixing for data settings
    """
    index = 'DS_HR_INDEX'

    nonmail_msg = 'Non-mailing-indicatie actief'
    restricted_msg = 'Afgeschermd'

    filters = {
        #'dataset': 'ves',
    }

    keywords = [
        'subcategorie', 'hoofdcategorie', 'handelsnaam', 'sbi_code',
        'sbi_omschrijving', 'buurt_naam', 'buurtcombinatie_naam', 'ggw_naam',
        'stadsdeel_naam', 'postcode', '_openbare_ruimte_naam',
        'openbare_ruimte',
        'rechtsvorm', 'aantal_werkzame_personen',
        'dataset',
        'bijzondere_rechtstoestand',
    ]
    keyword_mapping = {
        'buurt_naam': 'bezoekadres_buurt_naam',
        'buurtcombinatie_naam': 'bezoekadres_buurtcombinatie_naam',
        'ggw_naam': 'bezoekadres_ggw_naam',
        'stadsdeel_naam': 'bezoekadres_stadsdeel_naam',
        'postcode': 'bezoekadres_postcode',
        'woonplaats': 'bezoekadres_plaats',
        '_openbare_ruimte_naam': 'bezoekadres_openbare_ruimte',
        'openbare_ruimte': 'bezoekadres_openbare_ruimte',
    }
    selection = []


class HrGeoLocationSearch(HrBase, GeoLocationSearchView):

    def elastic_query(self, query):
        return meta_q(query, True)


class HrSearch(HrBase, TableSearchView):

    def elastic_query(self, query: dict) -> dict:
        return meta_q(query, add_aggs=True, sort=True)

    def _prepare_sbi_param(self, request) -> list:
        # Retrieving the request parameters
        request_parameters = getattr(request, self.request.method)
        #
        sbi_codes = request_parameters.get('sbi_code', None)

        sbi_codes = self._convert_value_to_list(sbi_codes)

        if not sbi_codes:
            return []

        # make sure we get a list of strings
        if not isinstance(sbi_codes, list):
            sbi_codes = [sbi_codes, ]
        # make sure everything is string
        sbi_codes = list(map(str, sbi_codes))
        return sbi_codes

    def custom_aggs(self, elastic_data: dict, request) -> None:
        """
        We want to filter out sbi code's aggs not being selected.

        if user selects: ?sbi_code=['01', '02']

        then we only want to return sbi codes that macht these
        paterns.
        Since Vestigingen can have multiple sbi_code way more
        sbi codes are returend. We do not want those extra codes
        they are 'correct' but confusing for endusers who made a specific
        selection
        """
        # Determine sbicodes
        sbi_codes = self._prepare_sbi_param(request)

        if not sbi_codes:
            return

        aggs_list = elastic_data['aggs_list']

        # loop over all sbi_ aggs
        for key, value in aggs_list.items():
            # find sbi keys
            if not key.startswith('sbi_'):
                continue

            bucketlist = value['buckets']
            newbucket = []
            # check if we want this sbi bucket key
            for bkey in bucketlist:
                if not _is_selected(bkey, sbi_codes):
                    continue
                # add to new sbi selection
                newbucket.append(bkey)

            # replace bucket list with cleaned up version
            value['doc_count'] = len(newbucket)
            value['buckets'] = newbucket


def _is_selected(bkey: dict, sbi_codes: list) -> bool:
    """
    """
    # first part is number
    b_key = bkey['key'].split(': ')[0]
    # compare bucket key with input sbi_codes
    for input_code in sbi_codes:
        if b_key.startswith(input_code):
            return True
        # if input_code.startswith(b_key):
        #    return True
    return False


class HrCSV(HrBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    name_conv = {'handelsnaam': 'naam'}

    fields_and_headers = (
        ('kvk_nummer', 'KvK-nummer'),
        ('vestiging_id', 'Vestigingsnummer'),
        ('handelsnaam', 'Eerste handelsnaam'),
        ('non_mailing', 'Indicatie non-mailing'),
        ('bezoekadres_volledig_adres', 'Bezoekadres (KvK HR)'),
        ('bezoekadres_correctie', 'Indicatie bezoekadres geschat o.b.v BAG'),
        ('bezoekadres_openbare_ruimte', 'Openbare ruimte bezoekadres (BAG)'),
        ('bezoekadres_huisnummer', 'Huisnummer bezoekadres (BAG)'),
        ('bezoekadres_huisletter', 'Huisletter bezoekadres (BAG)'),
        ('bezoekadres_huisnummertoevoeging',
         'Huisnummertoevoeging bezoekadres (BAG)'),
        ('bezoekadres_postcode', 'Postcode bezoekadres (BAG)'),
        ('bezoekadres_plaats', 'Woonplaats bezoekadres (BAG)'),
        ('postadres_volledig_adres', 'Postadres (KvK HR)'),
        ('postadres_correctie', 'Indicatie postadres geschat o.b.v BAG'),
        ('postadres_openbare_ruimte', 'Openbare ruimte postadres (BAG)'),
        ('postadres_huisnummer', 'Huisnummer postadres (BAG)'),
        ('postadres_huisletter', 'Huisletter postadres (BAG)'),
        ('postadres_huisnummertoevoeging',
         'Huisnummertoevoeging postadres (BAG)'),
        ('postadres_postcode', 'Postcode postadres (BAG)'),
        ('postadres_plaats', 'Woonplaats postadres (BAG)'),
        # ('hoofdcategorie', 'Hoofdcategorie'),
        # ('subcategorie', 'Subcategorie'),
        ('sbi_omschrijving', 'SBI-omschrijving'),
        ('sbi_code', 'SBI-code'),
        ('datum_aanvang', 'Datum aanvang'),
        # ('datum_einde', 'Datum einde'),
        ('bijzondere_rechtstoestand', 'Bijzondere rechtstoestand'),
        ('eigenaar_naam', 'Naam eigenaar(en)'),
        ('rechtsvorm', 'Rechtsvorm'),
        ('aantal_werkzame_personen', 'Werkzame personen'),
        ('adresseerbaar_object_id', 'Adresseerbaar object ID'),
        # ('centroid', 'lon/lat locatie'),
        ('lon', 'longitude'),
        ('lat', 'latitude'),
    )

    field_names = [h[0] for h in fields_and_headers]
    csv_headers = [h[1] for h in fields_and_headers]

    def elastic_query(self, query):
        return meta_q(query, False, False)

    def paginate(self, _offset, q: dict) -> dict:
        if 'size' in q:
            del q['size']
        return q

    def item_data_update(self, item, request):
        # strip time from date.
        datum_aanvang = item.get('datum_aanvang')
        if datum_aanvang is not None:
            date = parse(datum_aanvang)
            item['datum_aanvang'] = date.strftime('%Y-%m-%d')

        if item.get('centroid'):
            lon, lat = item['centroid']
            item['lon'] = float(lon)
            item['lat'] = float(lat)

        return item

    def sanitize_fields(self, item, field_names):
        item.update(
            {field_name: stringify_item_value(item.get(field_name, None))
             for field_name in field_names})
