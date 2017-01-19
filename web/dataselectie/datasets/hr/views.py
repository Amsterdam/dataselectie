# Python
# Packages
from django.db.models import QuerySet
from collections import OrderedDict as od
from itertools import chain
import copy
# Project
from datasets.hr import models
from datasets.bag.views import BAG_APIFIELDS
from datasets.hr.queries import meta_q
from datasets.generic.queries import add_aggregations
from datasets.generic.view_mixins import CSVExportView, TableSearchView

HR_APIFIELDS = ['_openbare_ruimte_naam', 'huisnummer',
                'huisletter', 'huisnummer_toevoeging', 'woonplaats',
                'postcode']

HR_KEYWORDS = ['subcategorie', 'hoofdcategorie', 'bedrijfsnaam',
               'sbi_code', 'sbi_omschrijving']


class HrBase(object):
    """
    Base class mixing for data settings
    """
    model = models.DataSelectie
    index = 'DS_INDEX'
    db = 'hr'
    q_func = meta_q

    raw_fields = ['naam', '_openbare_ruimte_naam']
    fixed_filters = []
    keywords = HR_KEYWORDS + BAG_APIFIELDS
    apifields = BAG_APIFIELDS + HR_APIFIELDS
    fieldname_mapping = {'naam': 'bedrijfsnaam'}
    sbi_top_down_values = {}
    sbi_subcategorie_values = {}
    sbi_sub_subcategorie_values = {}

    def process_sbi_codes(self, sbi_json: list) -> dict:
        """
        Sbi codes worden platgeslagen, waardoor die in de rij
        geexporteerd kunnen worden. Het scheidingsteken is \
        Eerst wordt de json gesorteerd, zodat die op volgorde van
        sbi_code wordt getoond.
        """
        new_json = sorted(sbi_json, key=self.sort_on_sbicode)

        result = {}

        result['sbicodes'] = ' \\ '.join([str(sbi['sbi_code']) for sbi in new_json])
        result['hoofdcategorieen'] = ' \\ '.join(self.unique_value(new_json, 'hoofdcategorie'))
        result['subcategorieen'] = ' \\ '.join(self.unique_value(new_json, 'subcategorie'))
        result['sbi_omschrijving'] = ' \\ '.join(self.unique_value(new_json, 'sub_sub_categorie'))

        return result

    def sort_on_sbicode(self, json):
        return int(json['sbi_code'])

    def unique_value(self, sbi_json, fieldname):
        """
        Make sure the original order is retained!

        :param sbi_json:
        :param fieldname:
        :return:
        """
        hcunique = od()
        for hc in sbi_json:
            hcunique[hc[fieldname]] = True
        return hcunique.keys()

    def process_betrokkenen(self, betrokken_json: list) -> str:
        """
        Betrokkenen zijn binnen handelsregister zowel verantwoordelijk
        voor als ondergeschikt aan.
        """
        result = "Onbekend"
        text_result = []
        for betrokken in betrokken_json:
            if betrokken:
                text = (betrokken['bevoegde_naam'] or '') + (betrokken['naam'] or '')
                if text:
                    text += ' ' + (betrokken['functietitel'] or '')
                    text_result.append(text)

        if len(text_result):
            result = ' \\ '.join(text_result)

        return result

    def build_el_query(self, filters: list, mapped_filters: list, query: dict) -> dict:
        """
        Adds innerhits to the query and other selection criteria

        :param filters:
        :param mapped_filters: Filters that are mapped to the child
        :param query: The query to be executed
        :return:
        """

        if not mapped_filters:
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

    def process_huisnummer_toevoeging(self, source):
        """
        Sloop huisnummer van toevoeging
        :param source:
        :return: toevoeging zonder huisnummer
        """
        if source['toevoeging']:
            hnummer_len = 0
            if source['huisnummer'] :
                hnummer_len = len(str(source['huisnummer']))
                if str(source['huisnummer']) != source['toevoeging'][0:hnummer_len]:
                    hnummer_len = 0
            return source['toevoeging'][hnummer_len:].strip()


class HrSearch(HrBase, TableSearchView):
    selection = []
    sbi_sub_subcategorie_values = []
    filtercategories = ('hoofdcategorie', 'subcategorie', 'sbi_omschrijving')
    mapfiltercats = {'sbi_omschrijving': 'sub_sub_categorie'}

    def elastic_query(self, query: dict) -> dict:
        res = meta_q(query, True, False)
        res['aggs'].update(add_aggregations(res['aggs']))
        res['aggs']['vestiging']['aggs'].update(add_aggregations(res['aggs']['vestiging']['aggs']))
        return res

    def define_id(self, item: dict, elastic_data: dict) -> str:
        return item['inner_hits']['vestiging']['hits']['hits'][0]['_source']['bag_vbid']

    def define_total(self, response: dict):
        aggs = response.get('aggregations', {})
        if 'vestiging' in aggs:
            aggs = super().process_aggs(aggs['vestiging'])
            aggs = self.includeagg(aggs)
            if 'doc_count' in aggs:
                del aggs['doc_count']
            self.extra_context_data['aggs_list'].update(aggs)
            del self.extra_context_data['aggs_list']['vestiging']

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
            ab = [[s['hoofdcategorie'], s['subcategorie'], s['sub_sub_categorie']]
                 for s in self.sbi_sub_subcategorie_values if s[fk] == val]
            self.selection += chain.from_iterable(ab)

        self.selection = list(set(self.selection))

        return

    def includeagg(self, aggs: dict) -> dict:
        """
        Correct results returned from elastic.

        :param aggs:
        :return: aggs
        """

        if len(self.selection):
            for fieldkey in self.filtercategories:
                delete_row = [idx for idx, b in enumerate(aggs[fieldkey]['buckets']) if not b['key'] in self.selection]
                delete_row.reverse()
                for idx in delete_row:
                    del aggs[fieldkey]['buckets'][idx]

        return aggs

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
        # Adding the buurtcombinatie, ggw, stadsdeel info to the result,
        # moving the jsonapi info one level down
        ignore_list = ('geometrie',)
        for i in range(len(context['object_list'])):
            for json_key, values in context['object_list'][i]['api_json'].items():
                if json_key not in ignore_list:
                    try:
                        nwfield = self.fieldname_mapping[json_key]
                    except KeyError:
                        nwfield = json_key
                    context['object_list'][i][nwfield] = context['object_list'][i]['api_json'][json_key]

            del context['object_list'][i]['api_json']

            self.flatten(context['object_list'][i])

            # Adding the extra context
            bagvbid = context['object_list'][i]['bag_vbid']
            if bagvbid in self.extra_context_data['items']:
                context['object_list'][i].update(self.extra_context_data['items'][bagvbid])
            else:
                print('bag_vbid %s not found' % bagvbid)

        context['total'] = self.extra_context_data['total']
        context['aggs_list'] = self.extra_context_data['aggs_list']
        return context

    def flatten(self, context_data: dict):
        context_data.update(self.process_sbi_codes(context_data['sbi_codes']))
        del context_data['sbi_codes']
        context_data['betrokkenen'] = self.process_betrokkenen(context_data['betrokkenen'])

    def fill_ids(self, response: dict, elastic_data: dict) -> dict:
        # Primary key from inner_Hits
        for hit in response['hits']['hits']:
            elastic_data = self.fill_item_ids(elastic_data, hit)
        return elastic_data

    def fill_item_ids(self, elastic_data: dict, hit: dict) -> dict:
        in_hits = hit['inner_hits']['vestiging']['hits']['hits']
        for ihit in in_hits:
            elastic_data['ids'].append(ihit['_id'][2:])
        elastic_data['extra_data'] = in_hits[0]['_parent']
        return elastic_data

    def proc_parameters(self, filter_keyword: str, val: str, child_filters: list, filters: list) -> (list, list):
        lfilter = {self.default_search: self.get_term_and_value(filter_keyword, val)}
        if filter_keyword in HR_KEYWORDS:
            child_filters.append(lfilter)
        else:
            filters.append(lfilter)
        return filters, child_filters


class HrCSV(HrBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    headers = [
        '_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging',
        'postcode', 'woonplaats', 'stadsdeel_naam', 'stadsdeel_code', 'ggw_naam', 'ggw_code',
        'buurtcombinatie_naam', 'buurtcombinatie_code', 'buurt_naam', 'naam',
        'buurt_code', 'gebruiksdoel_omschrijving', 'gebruik',
        'openabre_ruimte_landelijk_id', 'panden', 'verblijfsobject', 'ligplaats', 'standplaats',
        'landelijk_id']

    headers_hr = ['kvk_nummer', 'handelsnaam', 'vestigingsnummer', 'sbicodes', 'hoofdcategorieen', 'subsubcategorieen',
                  'subcategorieen', 'betrokkenen', 'rechtsvorm']

    headers += headers_hr

    name_conv = {'handelsnaam': 'naam'}

    pretty_headers = (
        'Naam openbare ruimte', 'Huisnummer', 'Huisletter', 'Huisnummertoevoeging',
        'Postcode', 'Woonplaats', 'Naam stadsdeel', 'Code stadsdeel', 'Naam gebiedsgerichtwerkengebied',
        'Code gebiedsgerichtwerkengebied', 'Naam buurtcombinatie', 'Code buurtcombinatie', 'Naam buurt',
        'Bewoner', 'Code buurt', 'Gebruiksdoel', 'Feitelijk gebruik',
        'Openbareruimte-identificatie', 'Pandidentificatie',
        'Verblijfsobjectidentificatie', 'Ligplaatsidentificatie', 'Standplaatsidentificatie',
        'Nummeraanduidingidentificatie', 'KvK-nummer', 'Handelsnaam', 'Vestigingsnummer', 'SBI-code',
        'Hoofdcategorie', 'SBI-omschrijving', 'Subcategorie', 'Naam eigenaar(en)', 'Rechtsvorm')

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
            r_dict['betrokkenen'] = self.process_betrokkenen(row.api_json['betrokkenen'])
            result.append(r_dict)

        return result

    def _process_flatfields(self, json: dict) -> dict:

        result = {}
        for hdr in self.headers_hr:
            hdr_from = hdr
            if hdr in self.name_conv:
                hdr_from = self.name_conv[hdr]
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
