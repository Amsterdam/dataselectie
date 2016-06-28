# Packages
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import ListView
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

# Project
from datasets.bag import models
from datasets.bag.queries import meta_Q


class JSONResponseMixin(object):
    """
    Render response to json
    """
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Return a serialzieable object
        This function should probably be overwritten
        """
        return context


class TableSearchView(JSONResponseMixin, ListView):
    """
    A base class to generate tables from search results
    """

    #attributes:
    #---------------------
    model = None  # The model class to use
    index = ''  # The name of the index to search in
    db = None  # The DB to use for the query This allws usage of different dbs
    keywords = []  # A set of optional keywords to filter the results further

    # ListView inherintance functions
    def get_queryset(self):
        """
        This function is called by list view to generate the query set
        It is overwritten to first use elastic to retrieve the ids then
        return a queryset based on the ids
        """
        # Loading data from elastic. See function for details
        self.load_from_elastic()
        # Creating a queryset
        qs = self.create_queryset()
        return qs

    def render_to_response(self, context, **response_kwargs):
        print(context)
        context = {}
        return self.render_to_json_response(context, **response_kwargs)

    def query_elastic(self, query):
        """
        Perform the query to elastic
        """

    # Functions to implement by subclass
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
        self.elastic = {
            'ids': None,
            'filters': [],
        }
        # Looking for keywords
        query = self.request.GET.get('query', None)
        term = self.request.GET.get('term', None)
        if query and term:
            print('Search: %s = %s' % (term, query))
        else:
            print('No query and term given')
            return
        # Performing the search
        q = self.elastic_query(term, query)
        elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            # sniff_on_start=True,
            retry_on_timeout=True,
            refresh=True
        )
        s = Search().using(elastic).query(q['Q'])
        # Adding filters
        filters = {}
        for filter_keyword in self.keywords:
            val = self.request.GET.get(filter_keyword, None)
            if val:
                filters[filter_keyword] = val
        # IF any filters were given, add them
        if filters:
            s = s.filters('terms', **filters)
        # Adding aggregations if given
        if 'A' in q:
            for key, aggregatie in q['A']:
                s.aggs.bucket(key, val)
        print('Query:', repr(s.to_dict()))
        response = s.execute()
        print(response)

    def create_queryset(self):
        """
        Generates a query set based on the ids retrieved from elastic
        """
        ids = self.elastic.get('ids', None)
        if ids:
            return self.model.objects.filter(id__in=ids)
        else:
            # No ids where found
            return self.model.objects.none()


class BagSearch(TableSearchView):

    model = models.Nummeraanduiding
    index = 'ZB_BAG'
    q_func = meta_Q

    def elastic_query(self, term, query):
        return meta_Q(term, query)

    def create_queryset(self):
        return self.model.objects.none()


