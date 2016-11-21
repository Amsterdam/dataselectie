# Python
import csv
import rapidjson
from datetime import datetime

from django.http import StreamingHttpResponse
from pytz import timezone

from datasets.hr import models
from datasets.hr.queries import meta_q
from datasets.generic.view_mixins import CSVExportView, Echo, TableSearchView


class HrBase(object):
    """
    Base class mixing for data settings
    """
    model = models.DataSelectie
    index = 'DS_BAG'
    db = 'hr'
    q_func = meta_q
    extra_context_keywords = [
        'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
        'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code', 'naam', 'postcode']
    keywords = ['sbi_code', 'bedrijfsnaam', 'sub_sub_categorie',
                'subcategorie', 'hoofdcategorie' ] + extra_context_keywords
    raw_fields = []

    keyword_mapping = {'sbi_code': 'sbi_codes.sbi_code',
                       'bedrijfsnaam': 'sbi_codes.bedrijfsnaam',
                       'sub_sub_categorie': 'sbi_codes.sub_sub_categorie',
                       'subcategorie': 'sbi_codes.subcategorie',
                       'hoofdcategorie': 'sbi_codes.hoofdcategorie'}

    fieldname_mapping = {'naam': 'bedrijfsnaam'}


    fixed_filters = [{'is_hr_address': True}]

#    sorts = ['vestigingsnummer']                    # For now this is enough.
                                                    # Probably complex sorting on content of json!


class HrSearch(HrBase, TableSearchView):
    def elastic_query(self, query):
        res = meta_q(query)
        return res

    def save_context_data(self, response):
        """
        Save the relevant buurtcombinatie, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        self.extra_context_data = {'items': {}}
        for item in response['hits']['hits']:
            first = True
            for sbi_info in item['_source']['sbi_codes']:
                vestigingsnr = sbi_info['vestigingsnummer']
                if first:
                    self.extra_context_data['items'][vestigingsnr] = {}
                    for field in self.extra_context_keywords:
                        try:
                            self.extra_context_data['items'][vestigingsnr][field] = \
                                item['_source'][field]
                        except:
                            pass
                    first = False
                    orig_vestigingsnr = vestigingsnr
                else:
                    self.extra_context_data['items'][vestigingsnr] = \
                        self.extra_context_data['items'][orig_vestigingsnr]

        self.extra_context_data['total'] = response['hits']['total']
        # Merging count with regular aggregation
        aggs = response.get('aggregations', {})
        count_keys = [key for key in aggs.keys() if key.endswith('_count')]
        for key in count_keys:
            aggs[key[0:-6]]['doc_count'] = aggs[key]['value']
            # Removing the individual count aggregation
            del aggs[key]
        self.extra_context_data['aggs_list'] = aggs
        self.update_keys = self.extra_context_data['items'].values()

    def update_context_data(self, context):
        # Adding the buurtcombinatie, ggw, stadsdeel info to the result, moving the jsonapi info one level down
        for i in range(len(context['object_list'])):
            for json_key, values in context['object_list'][i]['api_json'].items():
                try:
                    nwfield = self.fieldname_mapping[json_key]
                except KeyError:
                    nwfield = json_key
                context['object_list'][i][nwfield] = context['object_list'][i]['api_json'][json_key]
            del context['object_list'][i]['api_json']

            # Adding the extra context
            context['object_list'][i].update(self.extra_context_data['items'][
                                         context['object_list'][i][
                                             'id']])
        context['aggs_list'] = self.extra_context_data['aggs_list']
        context['total'] = self.extra_context_data['total']
        return context

    def fill_ids(self, response, elastic_data):
        for hit in response['hits']['hits']:
            for sbi_info in hit['_source']['sbi_codes']:
                if self._vest_nr_can_be_added(sbi_info):
                    elastic_data['ids'].append(sbi_info['vestigingsnummer'])
                    break
        return elastic_data

    def _vest_nr_can_be_added(self, sbi_info):
        add_value = len(self.saved_search_args) == 0
        for field, value in self.saved_search_args.items():
            if isinstance(value, str):
                value = value.lower()
            if field in sbi_info and (
                        (isinstance(sbi_info[field], str) and value in sbi_info[field].lower())
                        or sbi_info[field] == value):
                add_value = True
                break
        return add_value

class HrCSV(HrBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    # headers = ('_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging',
    #            'postcode', 'gemeente', 'stadsdeel_naam', 'stadsdeel_code', 'ggw_naam', 'ggw_code',
    #            'buurtcombinatie_naam', 'buurtcombinatie_code', 'buurt_naam',
    #            'buurt_code', 'bouwblok', 'geometrie_rd_x', 'geometrie_rd_y',
    #            'geometrie_wgs_lat', 'geometrie_wgs_lon', 'hoofdadres',
    #            'gebruiksdoel_omschrijving', 'gebruik', 'oppervlakte', 'type_desc', 'status',
    #            'openabre_ruimte_landelijk_id', 'panden', 'verblijfsobject', 'ligplaats', 'standplaats',
    #            'landelijk_id')
    pretty_headers = ('Naam openbare ruimte', 'Huisnummer', 'Huisletter', 'Huisnummertoevoeging',
                      'Postcode', 'Woonplaats', 'Naam stadsdeel', 'Code stadsdeel', 'Naam gebiedsgerichtwerkengebied',
                      'Code gebiedsgerichtwerkengebied', 'Naam buurtcombinatie', 'Code buurtcombinatie', 'Naam buurt',
                      'Code buurt', 'Code bouwblok', 'X-coordinaat (RD)', 'Y-coordinaat (RD)',
                      'Latitude (WGS84)', 'Longitude (WGS84)', 'Indicatie hoofdadres', 'Gebruiksdoel',
                      'Feitelijk gebruik', 'Oppervlakte (m2)', 'Objecttype',
                      'Verblijfsobjectstatus', 'Openbareruimte-identificatie', 'Pandidentificatie',
                      'Verblijfsobjectidentificatie', 'Ligplaatsidentificatie', 'Standplaatsidentificatie',
                      'Nummeraanduidingidentificatie')

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
        Overwriting the default conversion so that location data
        can be retrieved through the adresseerbaar_object
        and convert to wgs84
        """
        data = []
        for item in qs:
            dict_item = self._model_to_dict(item)
            # BAG Specific updates.
            # ------------------------
            # Adding geometry
            dict_item.update(self.create_geometry_dict(item))
            try:
                dict_item['hoofdadres'] = 'Ja' if dict_item['hoofdadres'] else 'Nee'
            except:
                pass
            # Saving the dict
            data.append(dict_item)
        return data

    def fill_items(self, items, item):
        items[item['_id']] = item

        return items

    def render_to_response(self, context, **response_kwargs):
        # Returning a CSV
        pseudo_buffer = Echo()

        # Creating the writer
        writer = csv.DictWriter(pseudo_buffer, self.headers, delimiter=';')

        # Streaming!
        gen = self.result_generator(context['object_list'])
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in gen), content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; ' \
            'filename="export_{0:%Y%m%d_%H%M%S}.csv"'.format(datetime.now(
                tz=timezone('Europe/Amsterdam')))
        return response

    def paginate(self, offset, q):
        if 'size' in q:
            del(q['size'])
        return q
