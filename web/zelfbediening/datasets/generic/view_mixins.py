# Python
from datetime import date, datetime
import json
# Packages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

#=============================================================
# Views
#=============================================================

class TableSearchView(ListView):
    """
    A base class to generate tables from search results
    """
    #attributes:
    #---------------------
    model = None  # The model class to use
    index = ''  # The name of the index to search in
    keywords = []  # A set of optional keywords to filter the results further
    preview_size = settings.SEARCH_PREVIEW_SIZE
    max_page_size = settings.SEARCH_MAX_PAGE_COUNT

    def __init__(self):
        super(ListView, self).__init__()
        self.elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS, retry_on_timeout=True, refresh=True
        )
        self.extra_context_data = None  # Used to store data from elastic used in context

    def _stringify_item_value(self, value):
        """
        Makes sure that the dict contains only strings for easy jsoning of the dict
        Following actions are taken:
        - None is replace by empty string
        - Boolean is converted to strinf
        - Numbers are converted to string
        - Datetime and Dates are converted to EU norm dates

        Important!
        If no conversion van be found the same value is returned
        This may, or may not break the jsoning of the object list

        @Parameter:
        value - a value to convert to string

        @Returns:
        The string representation of the value
        """
        if (isinstance(value, date) or isinstance(value, datetime)):
            value = value.strftime('%d-%m-%Y')
        elif value is None:
            value = ''
        else:
            # Trying repr, otherwise trying
            try:
                value = repr(value)
            except:
                try:
                    value = str(value)
                except:
                    pass
        return value


    # Listview methods overloading
    def get_queryset(self):
        """
        This function is called by list view to generate the query set
        It is overwritten to first use elastic to retrieve the ids then
        return a queryset based on the ids
        """
        elastic_data = self.load_from_elastic()  # See method for details
        qs = self.create_queryset(elastic_data)
        return qs

    def render_to_response(self, context, **response_kwargs):
        # Checking if pretty and debug
        resp = {}
        if self.request.GET.get('pretty', False) and settings.DEBUG:
            # @TODO Add a row to the object list at the start with all the keys
            return render(self.request, "pretty_elastic.html", context=context) 
        resp['object_list'] = list(context.get('object_list', []))
        # Cleaning all but the objects and aggregations
        try:
            resp['aggs_list'] = context['aggs_list']
        except KeyError:
            pass
        # If there is a total count, adding it as well
        try:
            resp['object_count'] = context.get('total', 0)
            resp['page_count'] = int(int(context['total']) / self.preview_size)
            if int(context['total']) % self.preview_size:
                resp['page_count'] += 1
            # Caping the number at max_page_size
            if resp['page_count'] > self.max_page_size:
                resp['page_count'] = self.max_page_size;
        except KeyError:
            pass

        return HttpResponse(
            json.dumps(resp),
            content_type='application/json',
            **response_kwargs
        )

    # Tableview methods
    def build_elastic_query(self, query):
        """
        Builds the dictionary query to send to elastic
        Parameters:
        query - The q dict returned from the queries file
        Returns:
        The query dict to send to elastic
        """
        # Adding filters
        filters = []
        for filter_keyword in self.keywords:
            val = self.request.GET.get(filter_keyword, None)
            if val:
                filters.append({'match_phrase_prefix': {filter_keyword: val}})
        # If any filters were given, add them, creating a bool query
        if filters:
            query['query'] = {
                'bool': {
                    'must': [query['query']],
                    'filter': filters,
                }
            }
        # Adding sizing if not given
        if 'size' not in query and self.preview_size:
            query['size'] = self.preview_size
        # Adding offset in case of paging
        offset = self.request.GET.get('page', 0)
        if offset:
            try:
                offset = (int(offset) - 1) * self.preview_size
                if offset > 1:
                    query['from'] = offset
            except ValueError:
                # offset is not an int
                pass
        # Sanity check to make sure we do not pass 10000
        if query['size'] + offset > settings.MAX_SEARCH_ITEMS:
            query['size'] = settings.MAX_SEARCH_ITEMS - offset  # really ??
        return query

    def load_from_elastic(self):
        """
        Loads the data from elastic.
        It extracts the query parameters from the url and creates a
        query for elastic. The query returns a list of ids relevant to
        the search term as well as a list of possible filters, based on
        aggregates search results. The results are set in the class

        query - the search string

        The folowing parameters are optional and can be used
        to further filter the results
        postcode - A postcode to limit the results to
        """
        # Creating empty result set. Just in case
        elastic_data = {'ids': [], 'filters': {}}
        # looking for a query
        query_string = self.request.GET.get('query', None)

        # Building the query
        q = self.elastic_query(query_string)
        query = self.build_elastic_query(q)
        # Performing the search
        # -----------------------
        # Checking if normal search can be done or the scroll API
        # must be used
        response = self.elastic.search(index='zb_bag', body=query)
        for hit in response['hits']['hits']:
            elastic_data['ids'].append(hit['_id'])
        # Enrich result data with needed info
        self.save_context_data(response)
        return elastic_data

    def create_queryset(self, elastic_data):
        """
        Generates a query set based on the ids retrieved from elastic
        """
        ids = elastic_data.get('ids', [])
        if ids:
            return self.model.objects.filter(id__in=ids).order_by('_openbare_ruimte_naam').values()[:self.preview_size]
        else:
            # No ids where found
            return self.model.objects.none().values()

    def get_context_data(self, **kwargs):
        """
        Overwrite the context retrital
        """
        context = super(TableSearchView, self).get_context_data(**kwargs)
        context = self.update_context_data(context)
        return context
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

class CSVExportView(TableSearchView):
    """
    A base class to generate csv exports
    """

    preview_size = None  # This is not relevant for csv export
    headers = []  # The headers of the csv

    def get_context_data(self, **kwargs):
        """
        Overwrite the context retrival
        """
        context = super(TableSearchView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        """
        Instead of an actual queryset, it returns an elastic scroll api generator
        """
        query_string = self.request.GET.get('query', None)
        # Building the query
        q = self.elastic_query(query_string)
        query = self.build_elastic_query(q)
        # Making sure there is no pagination
        if 'from' in query:
            del(query['from'])
        # Returning the elastic generator
        return scan(self.elastic, query=query)

    def result_generator(self, headers, es_generator, batch_size=100):
        """
        Generate the result set for the CSV eport
        """
        # Als eerst geef de headers terug
        header_dict = {}
        for h in headers:
            header_dict[h] = h
        yield header_dict
        more = True
        counter = 0
        # Yielding results in batches
        while more:
            counter += 1
            items = {}
            ids = []
            for item in es_generator:
                # Collecting items for batch
                items[item['_id']] = item
                # Breaking on batch size
                if len(items) == batch_size:
                    break
            # Stop the run
            if len(items) < batch_size:
                more = False
            # Retriving the database data
            qs = self.model.objects.filter(id__in=list(items.keys())).values()
            # Pairing the data
            data = self._combine_data(qs, items)
            for item in data:
                # Only returning fields from the headers
                resp = {}
                for key in headers:
                    resp[key] = item.get(key, '')
                yield resp

    def _combine_data(self, qs, es):
        data = list(qs)
        for item in data:
            # Making sure all the data is in string form
            item.update(
                {k: self._stringify_item_value(v) for k, v in item.items() if not isinstance(v, str)}
            )
            # Adding the elastic context
            item.update(es[item['id']]['_source'])
        return data

class Echo(object):
        """
        An object that implements just the write method of the file-like
        interface, for csv file streaming
        """
        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value
