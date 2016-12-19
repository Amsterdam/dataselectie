# Python
import csv
from datetime import datetime

from django.http import StreamingHttpResponse
from pytz import timezone
from django.conf import settings

from datasets.hr import models
from datasets.bag import views as bagviews
from datasets.bag import queries
from datasets.hr.queries import meta_q
from datasets.generic.view_mixins import CSVExportView, TableSearchView

AGGKEYS = ('hoofdcategorie', 'subcategorie')


import logging
log = logging.getLogger(__name__)


class HrBase(object):
    """
    Base class mixing for data settings
    """
    model = models.DataSelectie
    db = 'hr'
    q_func = meta_q

    extra_context_keywords = [
        'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
        'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code', 'naam']

    bezoekadres_context_keywords = ['_openbare_ruimte_naam', 'huisnummer',
                                    'huisletter', 'toevoeging', 'woonplaats',
                                    'postcode']

    keywords = ['subcategorie', 'hoofdcategorie', 'bedrijfsnaam', 'sbi_code'] \
               + extra_context_keywords

    raw_fields = []

    def bld_parent_path(lfilter):
        return {"has_parent": {"type": "bag_locatie", "query": lfilter}}
    
    keyword_mapping = ('buurt_naam', 'buurt_code', 'buurtcombinatie_code',
                       'buurtcombinatie_naam', 'ggw_code', 'stadsdeel_naam',
                       'stadsdeel_code', 'naam', 'ggw_naam', 'woonplaats')

    fieldname_mapping = {'naam': 'bedrijfsnaam'}

    def process_sbi_codes(self, sbi_json: list) -> dict:
        """
        Sbi codes worden platgeslagen, waardoor die in de rij
        geexporteerd kunnne worden. Het scheidingsteken is
        \
        """
        result = {}

        result['sbicodes'] = ' \\ '.join(
                [str(sbi['sbi_code']) for sbi in sbi_json])

        result['hoofdcategorieen'] = ' \\ '.join(set([
            hc['hoofdcategorie'] for hc in sbi_json]))

        result['subcategorieen'] = ' \\ '.join(set(
            [sc['subcategorie'] for sc in sbi_json]))
        return result

    def process_betrokkenen(self, betrokken_json: list) -> str:
        """
        Betrokkenen zijn binnen handelsregister zowel verantwoordelijk
        voor als ondergeschikt aan.
        """
        result = "Onbekend"
        text_result = []
        for betrokken in betrokken_json:
            text = (betrokken['bevoegde_naam'] or '') + (betrokken['naam'] or '')
            if text:
                text += ' ' + betrokken['functietitel']
                text_result.append(text)

        if len(text_result):
            result = ' \\ '.join(text_result)

        return result


class HrSearch(HrBase, TableSearchView):
    def elastic_query(self, query):
        res = meta_q(query, True, False)
        return res

    # def process_aggs(self, response):
    #     """
    #     Agregates of elastic not used to avoid "analysed" problem in aggregates
    #     and to allow for removal of "hoofdcategorieen" and "subcategorieen:  if
    #     selected
    #     :param response:
    #     :return:
    #     """
    #
    #     aggs = self.fill_elastic_aggregates(response)
    #
    #     akeys = {'hoofdcategorie': self.process_hoofdcategorie,
    #                'subcategorie': self.process_subcategorie}
    #     selected = []
    #     subcats = []
    #
    #     for k,v in self.input_filter.items():
    #         if k in akeys:
    #             selected, subcats = akeys[k](k, v)              # process hoofd or subcategorie
    #
    #     if not selected and not subcats:
    #         selected, subcats = self.process_hoofdcategorie()
    #
    #     aggs.update(self.fill_aggregates(selected, subcats))
            
    def process_subcategorie(self, value):
        return [], models.CBS_sbi_subcat.filter(hoofdcategorie=value).all()
        
    def fill_aggregates(self, selected, subcats):
        return {}

    def fill_elastic_aggregates(self, response):
        aggs = response.get('aggregations', {})
        for key in aggs.keys():
            if key.endswith('_count'):
                aggs[key[0:-6]]['doc_count'] = aggs[key]['value']
                # Removing the individual count aggregation
                del aggs[key]
        return aggs

    def build_el_query(self, filters:list, mapped_filters:list, query:dict) -> dict:
        """
        Adds innerhits to the query and other selection criteria

        :param filters:
        :return:
        """

        if not mapped_filters:
            mapped_filters = {"match_all": {}}

        filterquery = { "bool":
                            {
                            "should": [
                                {"term": {"_type": "vestigingen"}},
                                {"has_parent":
                                    {"type": "bag_locatie",
                                    "query": mapped_filters,
                                    "inner_hits": {}
                                    }
                                }]
                            }
                        }
        if len(filters):
            filterquery["bool"]["must"] = filters

        query['query'] = filterquery

        return query

    def fill_ids(self, response: dict, elastic_data: dict) -> dict:
        # Can be overridden in the view to allow for other primary keys
        for hit in response['hits']['hits']:
            elastic_data['ids'].append(hit['_id'][2:])
        return elastic_data

    def save_context_data(self, response, elastic_data=None):
        """
        Save the relevant buurtcombinatie, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        api_fields = (
            'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
            'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
            'stadsdeel_naam', 'stadsdeel_code', 'woonplaats')

        if len(response['hits']['hits']) and 'inner_hits' in response['hits']['hits'][0]:
            super().save_context_data(response['hits']['hits'][0]['inner_hits']['bag_locatie'],
                                  apifields=api_fields)

        self.aggregates_parent(response, api_fields)

    def aggregates_parent(self, response, api_fields):
        """
        Routine is necessary because elastic does not support aggregates over a parent
        from a child
        :param response:
        :param api_fields:
        :return:
        """
        request_parameters = getattr(self.request, self.request.method)
        mapped_filters = []
        filters = []
        for filter_keyword in self.keyword_mapping:
            val = request_parameters.get(filter_keyword, None)
            if val is not None:     # parameter is entered
                filters, mapped_filters = self.proc_parameters(filter_keyword, val, mapped_filters, filters)

        query = queries.bld_agg()
        query = super().build_el_query(filters, mapped_filters, query)
        response = self.elastic.search(
            index=settings.ELASTIC_INDICES[self.index],
            body=query,
            _source_include=['centroid']
        )

    def sbi_retrieve(self, item, orig_vestigingsnr):
        """
        Processing of SBI codes, update self.extra_context_data

        :param item: response item
        :param orig_vestigingsnr: Original vestigingsnr
        :return:
        """
        first = True
        for sbi_info in item['_source']['sbi_codes']:
            vestigingsnr = sbi_info['vestigingsnummer']
            if first:
                first = False
                self.first_sbi(item, vestigingsnr)
                orig_vestigingsnr = vestigingsnr
            else:
                self.extra_context_data['items'][vestigingsnr] = \
                    self.extra_context_data['items'][orig_vestigingsnr]

    def first_sbi(self, item, vestigingsnr):
        """
        Process first sbi code, add to self.extra_context_data

        :param item: response item
        :param vestigingsnr: current vestigingsnr to be processed
        :return:
        """
        self.extra_context_data['items'][vestigingsnr] = {}
        for field in self.extra_context_keywords:
            if field in item['_source']:
                self.extra_context_data['items'][vestigingsnr][field] = \
                    item['_source'][field]

    def update_context_data(self, context):
        # Adding the buurtcombinatie, ggw, stadsdeel info to the result,
        # moving the jsonapi info one level down
        for i in range(len(context['object_list'])):
            for json_key, values in context['object_list'][i]['api_json'].items():
                try:
                    nwfield = self.fieldname_mapping[json_key]
                except KeyError:
                    nwfield = json_key
                context['object_list'][i][nwfield] = context['object_list'][i]['api_json'][json_key]

            del context['object_list'][i]['api_json']

            self.flatten(context['object_list'][i])

            # Adding the extra context
            bag_numid = context['object_list'][i]['bag_numid']
            if bag_numid in self.extra_context_data['items']:
                context['object_list'][i].update(self.extra_context_data['items'][bag_numid])

        context['total'] = self.extra_context_data['total']
        context['aggs_list'] = self.extra_context_data['aggs_list']
        return context

    def flatten(self, context_data):
        context_data.update(self.process_sbi_codes(context_data['sbi_codes']))
        context_data['betrokkenen'] = self.process_betrokkenen(context_data['betrokkenen'])
        del context_data['sbi_codes']


class HrCSV(HrBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    headers = [
        '_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging',
        'postcode', 'gemeente', 'stadsdeel_naam', 'stadsdeel_code', 'ggw_naam', 'ggw_code',
        'buurtcombinatie_naam', 'buurtcombinatie_code', 'buurt_naam',
        'buurt_code', 'gebruiksdoel_omschrijving', 'gebruik', 'oppervlakte', 'type_desc', 'status',
        'openabre_ruimte_landelijk_id', 'panden', 'verblijfsobject', 'ligplaats', 'standplaats',
        'landelijk_id']

    headers_hr = ['kvk_nummer', 'naam', 'vestigingsnummer', 'sbicodes', 'hoofdcategorieen', 'subsubcategorieen',
                  'subcategorieen', 'betrokkenen', 'rechtsvorm', ]

    headers += headers_hr

    pretty_headers = (
        'Naam openbare ruimte', 'Huisnummer', 'Huisletter', 'Huisnummertoevoeging',
        'Postcode', 'Woonplaats', 'Naam stadsdeel', 'Code stadsdeel', 'Naam gebiedsgerichtwerkengebied',
        'Code gebiedsgerichtwerkengebied', 'Naam buurtcombinatie', 'Code buurtcombinatie', 'Naam buurt',
        'Code buurt', 'Gebruiksdoel', 'Feitelijk gebruik', 'Oppervlakte (m2)', 'Objecttype',
        'Verblijfsobjectstatus', 'Openbareruimte-identificatie', 'Pandidentificatie',
        'Verblijfsobjectidentificatie', 'Ligplaatsidentificatie', 'Standplaatsidentificatie',
        'Nummeraanduidingidentificatie', 'KvK-nummer', 'Handelsnaam', 'Vestigingsnummer', 'SBI-code',
        'Hoofdcategorie', 'SBI-omschrijving', 'Subcategorie', 'Naam eigenaar(en)', 'Rechtsvorm')

    def elastic_query(self, query):
        return meta_q(query, add_aggs=False)

    def create_geometry_dict(self, db_item):
        """
        Creates a geometry dict that can be used to add
        geometry information to the result set

        Returns a dict with geometry information if one
        can be created. If not, an empty dict is returned
        """
        res = {}
        try:
            geom = db_item.adresseerbaar_object.geometrie.centroid
        except AttributeError:
            geom = None
        if geom:
            # Convert to wgs
            geom_wgs = geom.transform('wgs84', clone=True).coords
            geom = geom.coords
            res = {
                'geometrie_rd_x': int(geom[0]),
                'geometrie_rd_y': int(geom[1]),
                'geometrie_wgs_lat': ('{:.7f}'.format(geom_wgs[1])).replace('.', ','),
                'geometrie_wgs_lon': ('{:.7f}'.format(geom_wgs[0])).replace('.', ',')
            }
        return res

    def _convert_to_dicts(self, qs):
        """
        Overwriting the default conversion so that 1 to n data is
        flattened according to specs
        """
        result = []
        for row in qs:
            r_dict = self._process_flatfields(row.api_json)
            r_dict.update(self._process_flatfields(row.api_json['postadres']))
            if len(row.api_json['betrokkenen']):
                r_dict['rechtsvorm'] = row.api_json['betrokkenen'][0]['rechtsvorm']
            r_dict['id'] = row.id
            r_dict.update(self.process_sbi_codes(row.api_json['sbi_codes']))
            r_dict['betrokkenen'] = self.process_betrokkenen(row.api_json['betrokkenen'])

            result.append(r_dict)

        return result

    def _process_flatfields(self, json: dict) -> dict:
        result = {}
        for hdr in self.headers_hr:
            try:
                result[hdr] = json[hdr]
            except KeyError:
                pass
        return result

    def fill_items(self, items, item):
        """
        
        :param items:
        :param item:
        :return:
        """
        items[item['_id']] = item

        return items

    def paginate(self, offset, q):
        if 'size' in q:
            del(q['size'])
        return q
