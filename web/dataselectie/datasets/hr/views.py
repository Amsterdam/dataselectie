# Python
# Packages
from django.db.models import QuerySet
from django.db.models.expressions import RawSQL
from collections import OrderedDict
from itertools import chain
# Project
from datasets.hr import models
from datasets.bag.views import BAG_APIFIELDS
from datasets.hr.queries import meta_q
from datasets.generic.queries import add_aggregations
from datasets.generic.tablesearchview import TableSearchView, process_aggs
from datasets.generic.csvexportview import CSVExportView
from datasets.generic.geolocationsearchview import GeoLocationSearchView

HR_APIFIELDS = ['_openbare_ruimte_naam', 'huisnummer',
                'huisletter', 'huisnummer_toevoeging', 'woonplaats',
                'postcode']

HR_KEYWORDS = ['subcategorie', 'hoofdcategorie', 'bedrijfsnaam',
               'sbi_code', 'sbi_omschrijving']


def getwoonplaats(json):
    ad_parts = json['postadres_volledig_adres'].split()
    return ad_parts[-1]


def postadres_gecorrigeerd(json):
    return adres_gecorrigeerd(json['postadres_correctie'])


def bezoekadres_gecorrigeerd(json):
    return adres_gecorrigeerd(json['bezoekadres_correctie'])


def adres_gecorrigeerd(correctie):
    if correctie == 'BAG':
        return 'ja'
    else:
        return 'nee'


class HrBase(object):
    """
    Base class mixing for data settings
    """
    model = models.DataSelectie
    index = 'DS_INDEX'
    db = 'hr'

    raw_fields = ['naam', '_openbare_ruimte_naam']
    fixed_filters = []
    default_search = 'term'
    keywords = HR_KEYWORDS + BAG_APIFIELDS
    apifields = BAG_APIFIELDS + HR_APIFIELDS
    fieldname_mapping = {'naam': 'bedrijfsnaam'}
    sbi_top_down_values = {}
    sbi_subcategorie_values = {}
    sbi_sub_subcategorie_values = {}
    sorts = RawSQL("api_json->>%s", ['naam'])
    child_filters = []
    filtercategories = ('sbi_omschrijving', 'subcategorie', 'hoofdcategorie')
    extra_context_data = {}
    selection = []

    def process_sbi_codes(self, sbi_json: list) -> dict:
        """
        Sbi codes worden platgeslagen, waardoor die in de rij
        geexporteerd kunnen worden. Het scheidingsteken is \
        Eerst wordt de json gesorteerd, zodat die op volgorde van
        sbi_code wordt getoond.
        """
        new_json = sorted(sbi_json, key=lambda x: int(x['sbi_code']))

        result = dict()

        result['sbicodes'] = ' \\ '.join(
            [str(sbi['sbi_code']) for sbi in new_json])
        result['hoofdcategorieen'] = ' \\ '.join(
            self.unique_value(new_json, 'hoofdcategorie'))
        result['subcategorieen'] = ' \\ '.join(
            self.unique_value(new_json, 'subcategorie'))
        result['sbi_omschrijving'] = ' \\ '.join(
            self.unique_value(new_json, 'sub_sub_categorie'))

        return result

    @staticmethod
    def unique_value(sbi_json, fieldname):
        """
        Make sure the original order is retained!

        :param sbi_json:
        :param fieldname:
        :return:
        """
        hcunique = OrderedDict()
        for hc in sbi_json:
            hcunique[hc[fieldname]] = True
        return hcunique.keys()

    @staticmethod
    def process_betrokkenen(betrokken_json: list) -> str:
        """
        Betrokkenen zijn binnen handelsregister zowel verantwoordelijk
        voor als ondergeschikt aan.
        """
        result = "Onbekend"
        text_result = []
        for betrokken in betrokken_json:
            if betrokken:
                bevoegde = betrokken['bevoegde_naam'] or ''
                betrokkene = betrokken['naam'] or ''
                text = (bevoegde + betrokkene)
                if text:
                    text += ' ' + (betrokken['functietitel'] or '')
                    text_result.append(text)

        if len(text_result):
            result = ' \\ '.join(text_result)

        return result

    def build_el_query(self,
            filters: list, query: dict) -> dict:
        """
        Adds innerhits to the query and other selection criteria

        :param filters:
        :param mapped_filters: Filters that are mapped to the child
        :param query: The query to be executed
        :return:
        """

        if self.child_filters:
            mapped_filters = self.child_filters
        else:
            mapped_filters = {"match_all": {}}

        filterquery = {
            "bool": {
                "must": [
                    {
                        "term": {
                            "_type": "bag_locatie"
                        }
                    },
                    {
                        "has_child": {
                            "type": "vestiging",
                            "query": mapped_filters,
                            "inner_hits": {}
                        }
                    }]
            }
        }

        if len(filters):
            filterquery["bool"]["must"] += filters

        query['query'] = filterquery

        return query

    @staticmethod
    def process_huisnummer_toevoeging(source):
        """
        Sloop huisnummer en huisletter uit de toevoeging
        :param source:
        :return: toevoeging zonder huisnummer
        """
        if source['toevoeging']:
            hnm = [h for h in source['toevoeging'].split()
                   if h not in (
                       str(source['huisnummer']), source['huisletter'])]
            return ''.join(hnm)

    def proc_parameters(self, filter_keyword: str, val: str,
                        filters: list) -> (list, list):

        lfilter = {
            self.default_search: self.get_term_and_value(filter_keyword, val)
        }

        if filter_keyword in HR_KEYWORDS:
            self.child_filters.append(lfilter)
        else:
            filters.append(lfilter)
        return filters

    def calc_total_count(self, aggs: dict) -> int:
        result = aggs['doc_count']
        if len(self.child_filters):
            selection_field = None
            for fc in self.filtercategories:
                h = [cf['term'][fc] for idx, cf in enumerate(self.child_filters) if fc in cf['term']]
                if len(h):
                    selection_field = fc
                    selection_field_val = h[0]
                    break
            if selection_field:
                f = [b for b in aggs[selection_field]['buckets'] if b['key'] == selection_field_val][0]
                result = f['doc_count']
        return result

    def add_hraggs(self, response: dict):
        aggs = response.get('aggregations', {})
        self.extra_context_data['aggs_list'] = process_aggs(aggs)
        self.extra_context_data['aggs_list']['total'] = response['hits']['total']

    def add_aggregates(self, response: dict):
        self.add_hraggs(response)
        aggs = response.get('aggregations', {})
        if 'nummeraanduiding_sub' in aggs and len(aggs['nummeraanduiding_sub']['buckets']):
            self.extra_context_data['aggs_list'].update(self.add_nummeraanduiding_sub(aggs))
        del self.extra_context_data['aggs_list']['nummeraanduiding_sub']

    def add_nummeraanduiding_sub(self, aggs):
        aggs = process_aggs(aggs['nummeraanduiding_sub']['buckets'][0]['vestiging'])
        aggs = self.includeagg(aggs)
        if 'doc_count' in aggs:
            aggs['total'] = self.calc_total_count(aggs)
            del aggs['doc_count']
            return aggs

    def includeagg(self, aggs: dict) -> dict:
        """
        Correct results returned from elastic.

        :param aggs:
        :return: aggs
        """

        if len(self.selection):
            for fieldkey in self.filtercategories:
                delete_row = [
                    idx for idx, b in enumerate(aggs[fieldkey]['buckets'])
                    if not b['key'] in self.selection]

                delete_row.reverse()
                for idx in delete_row:
                    del aggs[fieldkey]['buckets'][idx]

        return aggs


class HrGeoLocationSearch(HrBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, True)

    def bldresponse(self, response: dict) -> dict:

        resp = {
            'object_count': self.calc_total_from_aggs(response),
            'object_list': response['hits']['hits']
        }
        resp = self.add_missing_point(resp)

        return resp

    def add_missing_point(self, resp):
        for idx in range(len(resp['object_list'])):
            point = resp['object_list'][idx]
            vestigingen = point['inner_hits']['vestiging']['hits']['hits']
            for extra in range(len(vestigingen)-1):
                resp['object_list'].append(point)
            del point['inner_hits']
        return resp

    def calc_total_from_aggs(self, response):
        aggs = response.get('aggregations', {})
        return self.add_nummeraanduiding_sub(aggs)['total']


class HrSearch(HrBase, TableSearchView):
    sbi_sub_subcategorie_values = []
    mapfiltercats = {'sbi_omschrijving': 'sub_sub_categorie'}

    def elastic_query(self, query: dict) -> dict:
        res = meta_q(query, True, False)
        res['aggs'].update(add_aggregations(res['aggs']))
        vestigingaggs = res['aggs']['nummeraanduiding_sub']['aggs']['vestiging']['aggs']
        vestigingaggs.update(add_aggregations(vestigingaggs))
        return res

    def define_id(self, item: dict, elastic_data: dict) -> str:
        """
        Get the fist bag_vbid of a vestiging
        """
        inner_ves_hits = item['inner_hits']['vestiging']['hits']['hits']
        vb_id_first = inner_ves_hits[0]['_source']['bag_vbid']
        return vb_id_first

    def filterkeys(self, filter_keyword: str, val: str):
        """
        Based on the entered filter keys a list is constructed containing
        the descriptions of the categories, subcategories and sbi_description

        :param filter_keyword:
        :param val: the value to use in the select
        :return:
        """

        if not self.sbi_sub_subcategorie_values:
            self.build_sbi_filterkeys()

        if filter_keyword in self.filtercategories:
            try:
                fk = self.mapfiltercats[filter_keyword]
            except KeyError:
                fk = filter_keyword
            ab = [[ssbi['hoofdcategorie'],
                   ssbi['subcategorie'],
                   ssbi['sub_sub_categorie']]
                  for ssbi in self.sbi_sub_subcategorie_values
                  if ssbi[fk] == val]

            self.selection += chain.from_iterable(ab)

        self.selection = list(set(self.selection))

    def build_sbi_filterkeys(self):
        """
        One time build of sbi codes to enable rapid check against
        parameters (aggs)
        :return:
        """
        self.sbi_sub_subcategorie_values = []
        for hoofdcat in models.CBS_sbi_hoofdcat.objects.select_related():
            for subcat in hoofdcat.cbs_sbi_subcat_set.all():
                for sbi in subcat.cbs_sbicodes_set.all():
                    self.sbi_sub_subcategorie_values.append(
                        {
                            'sbi_code': sbi.sbi_code,
                            'hoofdcategorie': hoofdcat.hoofdcategorie,
                            'sub_sub_categorie': sbi.sub_sub_categorie,
                            'subcategorie': subcat.subcategorie,
                            'hcat': hoofdcat.hcat,
                            'scat': subcat.scat
                        })

    def save_context_data(self, response: dict, elastic_data: dict = None):
        """
        Save the relevant buurtcombinatie, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        super().save_context_data(response, elastic_data=elastic_data)

    def update_context_data(self, context: dict) -> dict:
        """
        Adding the buurtcombinatie, ggw, stadsdeel info to the result,
        moving the jsonapi info one level down
        """
        ignore_list = ('geometrie',)

        for i in range(len(context['object_list'])):
            api_json_data = context['object_list'][i]['api_json']
            for json_key, values in api_json_data.items():
                if json_key not in ignore_list:
                    try:
                        nwfield = self.fieldname_mapping[json_key]
                    except KeyError:
                        nwfield = json_key
                    context['object_list'][i][nwfield] = \
                        context['object_list'][i]['api_json'][json_key]

            del context['object_list'][i]['api_json']

            self.flatten(context['object_list'][i])

            # Adding the extra context
            bagvbid = context['object_list'][i]['bag_vbid']
            if bagvbid in self.extra_context_data['items']:
                context['object_list'][i].update(
                    self.extra_context_data['items'][bagvbid])
            else:
                print('bag_vbid %s not found' % bagvbid)

        context['aggs_list'] = self.extra_context_data['aggs_list']
        context['total'] = self.extra_context_data['aggs_list']['total']
        return context

    def flatten(self, context_data: dict):
        context_data.update(self.process_sbi_codes(context_data['sbi_codes']))
        del context_data['sbi_codes']
        context_data['betrokkenen'] = \
            self.process_betrokkenen(context_data['betrokkenen'])

    def fill_ids(self, response: dict, elastic_data: dict) -> dict:
        # Primary key from inner_Hits
        for hit in response['hits']['hits']:
            elastic_data = self.fill_item_ids(elastic_data, hit)
        return elastic_data

    @staticmethod
    def fill_item_ids(elastic_data: dict, hit: dict) -> dict:
        in_hits = hit['inner_hits']['vestiging']['hits']['hits']
        for ihit in in_hits:
            elastic_data['ids'].append(ihit['_id'][2:])
        elastic_data['extra_data'] = in_hits[0]['_parent']
        return elastic_data


class HrCSV(HrBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    convertvalues = {'woonplaats_postadres': getwoonplaats,
                     'postadres_correctie': postadres_gecorrigeerd,
                     'bezoekadres_correctie': bezoekadres_gecorrigeerd
                     }

    name_conv = {'handelsnaam': 'naam'}

    headers = [
        'kvk_nummer', 'handelsnaam', 'bezoekadres_volledig_adres',
        'bezoekadres_correctie', '_openbare_ruimte_naam', 'huisnummer',
        'huisletter', 'huisnummer_toevoeging', 'postcode', 'woonplaats',
        'postadres_volledig_adres', 'postadres_correctie',
        'postadres_straatnaam', 'postadres_huisnummer',
        'postadres_huisletter', 'postadres_huisnummertoevoeging',
        'postadres_postcode', 'woonplaats_postadres', 'hoofdcategorieen',
        'subcategorieen', 'sbi_omschrijving', 'sbicodes', 'datum_aanvang',
        'datum_einde', 'betrokkenen']

    headers_hr = [
        'kvk_nummer', 'handelsnaam', 'postadres_straatnaam',
        'postadres_huisnummer', 'postadres_huisletter',
        'postadres_huisnummertoevoeging', 'postadres_postcode',
        'woonplaats_postadres', 'hoofdcategorieen',
        'subsubcategorieen', 'subcategorieen', 'sbicodes',
        'betrokkenen', 'rechtsvorm', 'datum_aanvang', 'datum_einde',
        'bezoekadres_volledig_adres', 'postadres_volledig_adres',
        'bezoekadres_correctie', 'postadres_correctie']

    pretty_headers = (
        'KvK-nummer', 'Handelsnaam', 'Bezoekadres (KvK HR)',
        'Indicatie afwijkend bezoekadres BAG',
        'Openbare ruimte bezoekadres (BAG)', 'Huisnummer bezoekadres (BAG)',
        'Huisletter bezoekadres (BAG)', 'Huisnummertoevoeging bezoekadres (BAG)',
        'Postcode bezoekadres (BAG)', 'Woonplaats bezoekadres (BAG)',
        'Postadres (Kvk HR)', 'Indicatie afwijkend postadres BAG',
        'Openbare ruimte postadres (BAG)', 'Huisnummer postadres (BAG)',
        'Huisletter postadres (BAG)', 'Huisnummertoevoeging postadres (BAG)',
        'Postcode postadres (BAG)', 'Woonplaats postadres (BAG)',
        'Hoofdcategorie', 'Subcategorie', 'SBI-omschrijving', 'SBI-code',
        'Datum aanvang', 'Datum einde', 'Naam eigenaar(en)')

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
            if hdr in self.convertvalues:
                result[hdr] = self.convertvalues[hdr](json)
            else:
                try:
                    result[hdr] = json[hdr_from]
                except KeyError:
                    pass
        return result

    def paginate(self, offset, q: dict) -> dict:
        if 'size' in q:
            del(q['size'])
        return q

    def _fill_item(self, items: dict, item: dict) -> dict:
        """
        Function can be overwritten in the using class to allow for
        specific output (hr has multi outputs

        :param items:   Resulting dictionary containing the
        :param item:    Item from elastic
        :return: items
        """
        for ihit in item['inner_hits']['vestiging']['hits']['hits']:
            items[ihit['_id'][2:]] = item

        return items
