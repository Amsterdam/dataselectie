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
    db = 'BAG'
    q_func = meta_q
    keywords = (
        'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
        'buurtcombinatie_naam',
        'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code', 'naam', 'postcode')

    @staticmethod
    def keywords_is_raw():
        return {
            'buurt_naam': True,
            'buurt_code': False,
            'buurtcombinatie_code': False,
            'buurtcombinatie_naam': True,
            'ggw_naam': True,
            'ggw_code': False,
            'stadsdeel_naam': True,
            'stadsdeel_code': False,
            'naam': True,
            'postcode': False
        }


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
    headers = ('id', '_openbare_ruimte_naam', 'huisnummer', 'stadsdeel_naam',
               'huisnummer_toevoeging', 'ggw_code', 'document_nummer',
               'buurt_code', 'huisletter', 'hoofdadres', 'vervallen',
               'begin_geldigheid', 'buurt_naam', 'einde_geldigheid',
               'landelijk_id', 'stadsdeel_code', 'ggw_naam',
               'buurtcombinatie_naam', 'buurtcombinatie_code', 'adres_nummer',
               'postcode', 'type', 'document_mutatie', 'date_modified',
               'openbare_ruimte_id', 'mutatie_gebruiker', 'standplaats_id',
               'landelijk_id', 'verblijfsobject_id', 'ligplaats_id',
               'status_id', 'geometrie_rd', 'geometrie_wgs')

    def elastic_query(self, query):
        return meta_q(query, add_aggs=False)

    def _convert_to_dicts(self, qs):
        """
        Overwriting the default conversion so that location data
        can be retrieved through the adresseerbaar_object
        and convert to wgs84 
        """
        data = []
        for item in qs:
            geom_wgs = None
            try:
                geom = item.adresseerbaar_object.geometrie.centroid
            except AttributeError:
                geom = None
            if geom:
                # Convert to wgs
                geom_wgs = geom.transform('wgs84', clone=True).coords
                geom = geom.coords
            dict_item = self._model_to_dict(item)
            dict_item.update({'geometrie_rd': geom, 'geometrie_wgs': geom_wgs})
            data.append(dict_item)
        return data

    def render_to_response(self, context, **response_kwargs):
        # Returning a CSV
        pseudo_buffer = Echo()

        # Creating the writer
        writer = csv.DictWriter(pseudo_buffer, self.headers, delimiter=';')

        # Streaming!
        gen = self.result_generator(self.headers, context['object_list'])
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in gen), content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; ' \
            'filename="export_{0:%Y%m%d_%H%M%S}.csv"'.format(datetime.now(
                tz=timezone('Europe/Amsterdam')))
        return response

    def paginate(self, offset, q):
        return q
