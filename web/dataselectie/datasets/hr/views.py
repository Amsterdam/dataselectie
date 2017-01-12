# Python
# Packages
from django.db.models import QuerySet
# Project
from datasets.hr import models
from datasets.bag.views import BAG_APIFIELDS
from datasets.hr.queries import meta_q
from datasets.generic.queries import add_aggregations
from datasets.generic.view_mixins import CSVExportView, TableSearchView


HR_APIFIELDS = ['_openbare_ruimte_naam', 'huisnummer',
                'huisletter', 'toevoeging', 'woonplaats',
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

    raw_fields = []
    fixed_filters = []
    keywords = HR_KEYWORDS + BAG_APIFIELDS
    fieldname_mapping = {'naam': 'bedrijfsnaam'}

    def process_sbi_codes(self, sbi_json: list) -> dict:
        """
        Sbi codes worden platgeslagen, waardoor die in de rij
        geexporteerd kunnne worden. Het scheidingsteken is
        \
        """
        result = {}

        result['sbicodes'] = ' \\ '.join([str(sbi['sbi_code']) for sbi in sbi_json])

        result['hoofdcategorieen'] = ' \\ '.join(set([hc['hoofdcategorie'] for hc in sbi_json]))

        result['subcategorieen'] = ' \\ '.join(set([sc['subcategorie'] for sc in sbi_json]))

        result['sbi_omschrijving'] = ' \\ '.join(set([sc['sub_sub_categorie'] for sc in sbi_json]))

        return result

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


class HrSearch(HrBase, TableSearchView):
    def elastic_query(self, query: dict) -> dict:
        res = meta_q(query, True, False)
        res['aggs'].update(add_aggregations(res['aggs']))
        res['aggs']['vestiging']['aggs'].update(add_aggregations(res['aggs']['vestiging']['aggs']))
        return res

    def define_id(self, item: dict, elastic_data: dict) -> str:
        return item['inner_hits']['vestiging']['hits']['hits'][0]['_id']

    def define_total(self, response: dict):
        aggs = response.get('aggregations', {})
        if 'vestiging' in aggs:
            self.extra_context_data['aggs_list'].update(super().process_aggs(aggs['vestiging']))

    def save_context_data(self, response: dict, apifields: list, elastic_data: dict=None):
        """
        Save the relevant buurtcombinatie, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        super().save_context_data(response, apifields=BAG_APIFIELDS + HR_APIFIELDS,
                                  elastic_data=elastic_data)

    def update_context_data(self, context: dict) -> dict:
        # Adding the buurtcombinatie, ggw, stadsdeel info to the result,
        # moving the jsonapi info one level down
        ignore_list = ('geometrie', )
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
            vestigingsid = 'HR' + context['object_list'][i]['id']
            if vestigingsid in self.extra_context_data['items']:
                context['object_list'][i].update(self.extra_context_data['items'][vestigingsid])

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
        print(meta_q(query, add_aggs=False))
        return meta_q(query, add_aggs=False)

    def _convert_to_dicts(self, qs: QuerySet) -> list:
        """
        Overwriting the default conversion so that 1 to n data is
        flattened according to specs
        """
        print('Converting to dicts')
        result = []
        for row in qs:
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
