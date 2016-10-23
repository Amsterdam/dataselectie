# Python
import csv
from datetime import datetime

from django.http import StreamingHttpResponse
from pytz import timezone

from datasets.bag import models
from datasets.bag.queries import meta_q
from datasets.generic.view_mixins import CSVExportView, Echo, TableSearchView


class BagBase(object):
    """
    Base class mixing for data settings
    """
    model = models.Nummeraanduiding
    index = 'DS_BAG'
    db = 'bag'
    q_func = meta_q
    keywords = (
        'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
        'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code', 'naam', 'postcode')
    raw_fields = ['naam', '_openbare_ruimte_naam']


class BagSearch(BagBase, TableSearchView):
    def elastic_query(self, query):
        res = meta_q(query)
        return res

    def save_context_data(self, response):
        """
        Save the relevant buurtcombinatie, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        self.extra_context_data = {'items': {}}
        fields = ('buurt_naam', 'buurt_code', 'buurtcombinatie_code',
                  'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
                  'stadsdeel_naam', 'stadsdeel_code')
        for item in response['hits']['hits']:
            self.extra_context_data['items'][item['_id']] = {}
            for field in fields:
                try:
                    self.extra_context_data['items'][item['_id']][field] = \
                        item['_source'][field]
                except:
                    pass
        self.extra_context_data['total'] = response['hits']['total']
        # Merging count with regular aggregation
        aggs = response.get('aggregations', {})
        count_keys = [key for key in aggs.keys() if key.endswith('_count')]
        for key in count_keys:
            aggs[key[0:-6]]['doc_count'] = aggs[key]['value']
            # Removing the individual count aggregation
            del aggs[key]
        self.extra_context_data['aggs_list'] = aggs

    def update_context_data(self, context):
        # Adding the buurtcombinatie, ggw, stadsdeel info to the result
        for i in range(len(context['object_list'])):
            # Making sure all the data is in string form
            context['object_list'][i].update(
                {k: self._stringify_item_value(v) for k, v in
                 context['object_list'][i].items() if not isinstance(v, str)}
            )
            # Adding the extra context
            context['object_list'][i].update(self.extra_context_data['items'][
                                                 context['object_list'][i][
                                                     'id']])
        context['aggs_list'] = self.extra_context_data['aggs_list']
        context['total'] = self.extra_context_data['total']
        return context


class BagCSV(BagBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    headers = ('_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging',
               'postcode', 'gemeente', 'stadsdeel_naam', 'stadsdeel_code', 'ggw_naam', 'ggw_code',
               'buurtcombinatie_naam', 'buurtcombinatie_code', 'buurt_naam',
               'buurt_code', 'bouwblok', 'geometrie_rd_x', 'geometrie_rd_y',
               'geometrie_wgs_lat', 'geometrie_wgs_lon', 'hoofdadres',
               'gebruiksdoel_omschrijving', 'gebruik', 'oppervlakte', 'type_desc', 'status', 'openbare_ruimte', 
               'panden', 'verblijfsobject', 'ligplaats', 'standplaats', 'landelijk_id')
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

    def verblijfsobject_updates(self, item):
        """
        Creates a dict with verblijfsobject specific data
        A dict is always returned, even if no data is found, in which case
        an empty dict is returned
        """
        verblijfsobject = {}
        verblijfsobject_data = ['gebruiksdoel_omschrijving', 'oppervlakte']
        for meta in verblijfsobject_data:
            verblijfsobject[meta] = getattr(Opp, meta, '')
        try:
            verblijfsobject['bouwblok'] = item.verblijfsobject.bouwblok.code
        except AttributeError:
            pass
        try:
            verblijfsobject['gebruik'] = item.verblijfsobject.gebruik.omschrijving
        except AttributeError:
            pass
        try:
            verblijfsobject['panden'] = '/'.join([i.landelijk_id for i in item.verblijfsobject.panden.all()])
        except AttributeError:
            pass
        return verblijfsobject

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
            #------------------------
            # Adding geometry
            dict_item.update(self.create_geometry_dict(item))
            # Updating status to description
            # try:
            #     dict_item['status'] = item.adresseerbaar_object.status.omschrijving
            # except AttributeError:
            #     pass
            # # Converting type
            #type_code = int(dict_item['type']) - 1
            #dict_item['type'] = self.model.OBJECT_TYPE_CHOICES[type_code][1]
            # Changing true/flase to yes/no
            #dict_item['hoofdadres'] = 'Ja' if dict_item['hoofdadres'] else 'Nee'
            # Updating to landelijk id
            # landelijk_ids = ['openbare_ruimte', 'adresseerbaar_object']
            # for sub_item_name in landelijk_ids:
            #     try:
            #         ref_item = getattr(item, sub_item_name, None)
            #         dict_item[sub_item_name] = ref_item.landelijk_id
            #     except:
            #         pass
            # Adding Verblijfobject specifiek data
            #if item.verblijfsobject:
            #    dict_item.update(self.verblijfsobject_updates(item))
                    
            # Saving the dict
            data.append(dict_item)
        return data

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
