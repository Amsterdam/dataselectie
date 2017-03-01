# Python
# Packages
from collections import OrderedDict
from itertools import chain

from django.db.models import QuerySet
from django.db.models.expressions import RawSQL

from datasets.bag.views import BAG_APIFIELDS
from datasets.generic.views_mixins import CSVExportView, GeoLocationSearchView, TableSearchView
from datasets.hr import models as hrmodels
from datasets.hr.queries import meta_q

HR_APIFIELDS = ['_openbare_ruimte_naam', 'huisnummer',
                'huisletter', 'huisnummer_toevoeging', 'woonplaats',
                'postcode']

HR_KEYWORDS = ['subcategorie', 'hoofdcategorie', 'bedrijfsnaam',
               'sbi_code', 'sbi_omschrijving']

class HrBase(object):
    """
    Base class mixing for data settings
    """
    index = 'DS_INDEX'

    raw_fields = ['naam', '_openbare_ruimte_naam']
    default_search = 'term'
    keywords = HR_KEYWORDS + BAG_APIFIELDS
    fieldname_mapping = {'naam': 'bedrijfsnaam'}
    el_sorts = []
    filtercategories = ('sbi_omschrijving', 'subcategorie', 'hoofdcategorie')
    extra_context_data = {}
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

    def proc_parameters(self, filter_keyword: str, val: str,
                        filters: list) -> list:

        lfilter = {
            self.default_search: self.get_term_and_value(filter_keyword, val)
        }

        if filter_keyword in HR_KEYWORDS:
            self.child_filters.append(lfilter)
        else:
            filters.append(lfilter)
        return filters


class HrGeoLocationSearch(HrBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, True)

    def bldresponse(self, response: dict) -> dict:

        resp = {
            'object_count': self.calc_total_from_aggs(response),
            'object_list': response['hits']['hits']
        }
        return self.add_missing_point(resp)

    def add_missing_point(self, resp):
        for idx in range(len(resp['object_list'])):
            point = resp['object_list'][idx]
            vestigingen = point['hits']['hits']
            for extra in range(len(vestigingen) - 1):
                resp['object_list'].append(point)
        return resp

    def calc_total_from_aggs(self, response):
        aggs = response.get('aggregations', {})
        return self.add_nummeraanduiding_sub(aggs)['total']


class HrSearch(HrBase, TableSearchView):
    mapfiltercats = {'sbi_omschrijving': 'categorieen', 'subcategorie': 'categorieen'}

    def elastic_query(self, query: dict) -> dict:
        res = meta_q(query, True, False)
        #res['aggs'].update(add_aggregations(res['aggs']))

        return res

    def filterkeys(self, filter_keyword: str, val: str):
        """
        Based on the entered filter keys a list is constructed containing
        the descriptions of the categories, subcategories and sbi_description

        :param filter_keyword:
        :param val: the value to use in the select
        :return:
        """

        if not self.sbi_sub_subcategorie_values:
            self.sbi_sub_subcategorie_values = build_sbi_filterkeys()

        if filter_keyword in self.filtercategories:
            ab = [ssbi for ssbi in self.sbi_sub_subcategorie_values
                  if val in ssbi]

            self.selection += chain.from_iterable(ab)

        self.selection = list(set(self.selection))

    # def update_context_data(self, context: dict) -> dict:
    #     """
    #     Adding the buurtcombinatie, ggw, stadsdeel info to the result,
    #     moving the jsonapi info one level down
    #     """
    #     ignore_list = ('geometrie',)

    #     for i in range(len(context['object_list'])):
    #         api_json_data = context['object_list'][i]['api_json']
    #         for json_key, values in api_json_data.items():
    #             if json_key not in ignore_list:
    #                 nwfield = self.get_mapped_fieldname(json_key)
    #                 context['object_list'][i][nwfield] = \
    #                     context['object_list'][i]['api_json'][json_key]

    #         del context['object_list'][i]['api_json']

    #         self.flatten(context['object_list'][i])

    #         # Adding the extra context
    #         bagvbid = context['object_list'][i]['bag_vbid']
    #         if bagvbid in self.extra_context_data['items']:
    #             context['object_list'][i].update(
    #                 self.extra_context_data['items'][bagvbid])
    #         else:
    #             print('bag_vbid %s not found' % bagvbid)

    #     context['aggs_list'] = self.extra_context_data['aggs_list']
    #     context['total'] = self.extra_context_data['aggs_list']['total']
    #     del context['aggs_list']['total']
    #     return context

    # def get_mapped_fieldname(self, fieldname: str) -> str:
    #     try:
    #         nwfield = self.fieldname_mapping[fieldname]
    #     except KeyError:
    #         nwfield = fieldname
    #     return nwfield

    # def flatten(self, context_data: dict):
    #     context_data.update(self.process_sbi_codes(context_data['sbi_codes']))
    #     del context_data['sbi_codes']
    #     context_data['betrokkenen'] = \
    #         self.process_betrokkenen(context_data['betrokkenen'])


class HrCSV(HrBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    name_conv = {'handelsnaam': 'naam'}

    hdrs = (('kvk_nummer', True, 'KvK-nummer', True),
            ('handelsnaam', True, 'Handelsnaam', True),
            ('bezoekadres_volledig_adres', True, 'Bezoekadres (KvK HR)', True),
            ('bezoekadres_correctie', True, 'Indicatie bezoekadres geschat o.b.v BAG', True),
            ('bezoekadres_openbare_ruimte', True, 'Openbare ruimte bezoekadres (BAG)', True),
            ('bezoekadres_huisnummer', False, 'Huisnummer bezoekadres (BAG)', True),
            ('bezoekadres_huisletter', False, 'Huisletter bezoekadres (BAG)', True),
            ('bezoekadres_toevoeging', False, 'Huisnummertoevoeging bezoekadres (BAG)',
             True),
            ('bezoekadres_postcode', False, 'Postcode bezoekadres (BAG)', True),
            ('bezoekadres_plaats', False, 'Woonplaats bezoekadres (BAG)', True),
            ('postadres_volledig_adres', True, 'Postadres (Kvk HR)', True),
            ('postadres_correctie', True, 'Indicatie postadres geschat o.b.v BAG', True),
            # ('postadres_straatnaam', True, 'Openbare ruimte postadres (BAG)', True),
            # ('postadres_huisnummer', True, 'Huisnummer postadres (BAG)', True),
            # ('postadres_huisletter', True, 'Huisletter postadres (BAG)', True),
            # ('postadres_huisnummertoevoeging', True, 'Huisnummertoevoeging postadres (BAG)', True),
            # ('postadres_postcode', True, 'Postcode postadres (BAG)', True),
            # ('woonplaats_postadres', True, 'Woonplaats postadres (BAG)', True),
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
        return meta_q(query, add_aggs=False)

    def _convert_to_dicts(self, qs: QuerySet) -> list:
        """
        Overwriting the default conversion so that 1 to n data is
        flattened according to specs
        """
        result = []
        for nr, row in enumerate(qs):
            r_dict = self._process_flatfields(row.api_json)
            r_dict['id'] = row.id
            r_dict.update(self.process_sbi_codes(row.api_json['sbi_codes']))
            r_dict['betrokkenen'] = self.process_betrokkenen(
                row.api_json['betrokkenen'])
            result.append(r_dict)

        return result

    def _process_flatfields(self, json: dict) -> dict:

        result = {}
        for hdr in self.headers_hr:
            hdr_from = hdr
            if hdr in self.name_conv:
                hdr_from = self.name_conv[hdr]
            else:
                try:
                    result[hdr] = json[hdr_from]
                except KeyError:
                    pass
        return result

    def paginate(self, offset, q: dict) -> dict:
        if 'size' in q:
            del (q['size'])
        return q

    # def _fill_item(self, items: dict, item: dict) -> dict:
    #     """
    #     Function can be overwritten in the using class to allow for
    #     specific output (hr has multi outputs

    #     :param items:   Resulting dictionary containing the
    #     :param item:    Item from elastic
    #     :return: items
    #     """
    #     for ihit in item['hits']['hits']:
    #         items[ihit['_id'][2:]] = item

    #     return items

