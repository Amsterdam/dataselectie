# Python
import csv
# Packages
from django.http import StreamingHttpResponse
# Project
from datasets.bag import models
from datasets.bag.queries import meta_Q
from datasets.generic.view_mixins import CSVExportView, Echo, TableSearchView


class BagBase(object):
    """
    Base class mixing for data settings
    """
    model = models.Nummeraanduiding
    index = 'ZB_BAG'
    db = 'BAG'
    q_func = meta_Q
    keywords = ('buurt_naam', 'buurt_code', 'buurtcombinatie_code', 'buurtcombinatie_naam', 'ggw_naam', 'ggw_code', 'stadsdeel_naam', 'stadsdeel_code', 'naam', 'postcode')


class BagSearch(BagBase, TableSearchView):

    def elastic_query(self, query):
        return meta_Q(query)

    def save_context_data(self, response):
        """
        Save the relevant buurtcombinatie, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        self.extra_context_data = {'items': {}}
        fields = ('buurt_naam', 'buurt_code', 'buurtcombinatie_code', 'buurtcombinatie_naam', 'ggw_naam', 'ggw_code', 'stadsdeel_naam', 'stadsdeel_code')
        for item in response['hits']['hits']:
            self.extra_context_data['items'][item['_id']] = {}
            for field in fields:
                try:
                    self.extra_context_data['items'][item['_id']][field] = item['_source'][field]
                except:
                    pass
        self.extra_context_data['total'] =  response['hits']['total']
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
                {k: self._stringify_item_value(v) for k, v in context['object_list'][i].items() if not isinstance(v, str)}
            )
            # Adding the extra context
            context['object_list'][i].update(self.extra_context_data['items'][context['object_list'][i]['id']])
        try:
            context['aggs_list'] = self.extra_context_data['aggs_list']
            context['total'] = self.extra_context_data['total']
        except TypeError:
            # There is no extra_content_data
            pass
        return context


class BagCSV(BagBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    headers = ('id', '_openbare_ruimte_naam', 'huisnummer', 'stadsdeel_naam', 'huisnummer_toevoeging', 'ggw_code', 'document_nummer', 'buurt_code', 'huisletter', 'hoofdadres', 'vervallen', 'begin_geldigheid', 'buurt_naam', 'einde_geldigheid', 'landelijk_id', 'stadsdeel_code', 'ggw_naam', 'buurtcombinatie_naam', 'buurtcombinatie_code', 'adres_nummer', 'postcode', 'type', 'document_mutatie', 'date_modified', 'openbare_ruimte_id', 'mutatie_gebruiker', 'standplaats_id', 'landelijk_id', 'verblijfsobject_id', 'ligplaats_id', 'status_id')

    def elastic_query(self, query):
        return meta_Q(query, add_aggs=False)

    def render_to_response(self, context, **response_kwargs):
        # Returning a CSV
        pseudo_buffer = Echo()
        # Creating the writer
        writer = csv.DictWriter(pseudo_buffer, self.headers)
        # Streaming!
        gen = self.result_generator(self.headers, context['object_list'])
        response = StreamingHttpResponse((writer.writerow(row) for row in gen), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        return response

    def paginate(self, offset, q):
        return q
