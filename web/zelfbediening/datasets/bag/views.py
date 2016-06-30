# Packages
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from django.views.generic import ListView
from elasticsearch import Elasticsearch
# Project
from datasets.bag import models
from datasets.bag.queries import meta_Q


class TableSearchView(ListView):
    """
    A base class to generate tables from search results
    """
    #attributes:
    #---------------------
    model = None  # The model class to use
    index = ''  # The name of the index to search in
    db = None  # The DB to use for the query This allws usage of different dbs
    keywords = []  # A set of optional keywords to filter the results further

    def __init__(self):
        self.elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS, retry_on_timeout=True, refresh=True
        )
        self.extra_context_data = None  # Used to store data from elastic used in context

    # Listview methods overloading
    def get_queryset(self):
        """
        This function is called by list view to generate the query set
        It is overwritten to first use elastic to retrieve the ids then
        return a queryset based on the ids
        """
        # Loading data from elastic. See function for details
        elastic_data = self.load_from_elastic()
        # Creating a queryset
        qs = self.create_queryset(elastic_data)
        return qs

    def render_to_response(self, context, **response_kwargs):
        # The get_data should take care of all the serialization
        # Extra data is then added and the response is returned
        context = self.get_data(context)
        context = self.update_context_data(context)
        return HttpResponse(
            self.get_data(context),
            content_type='application/json',
            **response_kwargs
        )

    # Tableview methods
    def build_elastic_query(self, q):
        """
        Builds the dictionary query to send to elastic
        Parameters:
        q - The q dict returned from the queries file
        Returns:
        The query dict to send to elastic
        """
        query = q['Q']

        # Adding filters
        filters = {}
        for filter_keyword in self.keywords:
            val = self.request.GET.get(filter_keyword, None)
            if val:
                filters[filter_keyword] = val
        # If any filters were given, add them
        if filters:
            query['filters'] = filters
            self.elastic_data['filters'] = filters

        # Adding aggregations if given
        if 'A' in q:
            for key, aggregatie in q['A']:
                query['aggs'] = {
                    'bucket': {
                        key: val
                    }
                }
        print('Query:', repr(query))
        return query

    def load_from_elastic(self):
        """
        Loads the data from elastic.
        It extracts the query parameters from the url and creates a
        query for elastic. The query returns a list of ids relevant to
        the search term as well as a list of possible filters, based on
        aggregates search results. The results are set in the class

        query - the search string
        term - what type of term this is

        The folowing parameters are optional and can be used
        to further filter the results
        postcode - A postcode to limit the results to
        """
        # Creating empty result set. Just in case
        elastic_data = {'ids': [], 'filters': {}}
        # looking for a query
        query_string = self.request.GET.get('query', None)
        term = self.request.GET.get('term', None)
        if not (query_string and term):
            print('No query and term given')
            return elastic_data

        # Building the query
        q = self.elastic_query(term, query_string)
        query = self.build_elastic_query(q)
        # Performing the search
        response = self.elastic.search(index='zb_bag', body=query)  #, filter_path=['hits.hits._id', 'hits.hits._type'])
        print(response)
        for hit in response['hits']['hits']:
            elastic_data['ids'].append(hit['_id'])
        # Enrich result data with neede info
        self.save_context_data(response)
        return elastic_data

    def create_queryset(self, elastic_data):
        """
        Generates a query set based on the ids retrieved from elastic
        """
        ids = elastic_data.get('ids', None)
        if ids:
            return self.model.objects.filter(id__in=ids).order_by('_openbare_ruimte_naam')[:20]
        else:
            # No ids where found
            return self.model.objects.none()

    #===============================================
    # Context altering functions to be overwritten
    #===============================================
    def save_context_data(self, response):
        """
        Can be used by the subclass to save extra data to be used
        later to correct context data

        Parameter:
        response - the elastic response dict
        """
        pass

    def update_context_data(self, context):
        """
        Enables the subclasses to update/change the object list
        """
        return context

    def get_data(self, context):
        """
        Takes care of preparing the data for a json response
        by serializing and filtering
        This should probably be overwritten
        """
        return context

class BagSearch(TableSearchView):

    model = models.Nummeraanduiding
    index = 'ZB_BAG'
    q_func = meta_Q

    def elastic_query(self, term, query):
        return meta_Q(term, query)

    def save_context_data(self, response):
        """
        Save the relevant wijk, buurt, ggw and stadsdeel to be used
        later to enrich the results
        """
        self.extra_context_data = {}
        fields = ('buurt_naam', 'buurt_code', 'wijk_code', 'wijk_naam', 'ggw_naam', 'ggw_code', 'stadsdeel_naam', 'stadsdeel_code')
        for item in response['hits']['hits']:
            self.extra_context_data[item['_id']] = {}
            for field in fields:
                self.extra_context_data[item['_id']][field] = item['_source'][field]

    def update_context_data(self, context):
        # Adding the wijk, ggw, stadsdeel info to the result
        object_list = self.get_context_object_name()
        for item in context[object_list]:
            print(item)

    def get_data(self, context):
        # Returns the list of objects
        print(context)
        context = serializers.serialize('json', context[self.get_context_object_name()], fields=('id', '_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging', 'postcode', 'hoofdadres'))
        print(context)
        return context


