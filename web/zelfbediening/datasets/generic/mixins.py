# Python
import json
# Packages
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
from django.core import serializers
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from elasticsearch import Elasticsearch


class ImportStatusMixin(models.Model):
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DocumentStatusMixin(models.Model):
    document_mutatie = models.DateField(null=True)
    document_nummer = models.CharField(max_length=20, null=True)

    class Meta:
        abstract = True


class GeldigheidMixin(models.Model):
    begin_geldigheid = models.DateField(null=True)
    einde_geldigheid = models.DateField(null=True)

    class Meta:
        abstract = True


class MutatieGebruikerMixin(models.Model):
    mutatie_gebruiker = models.CharField(max_length=30, null=True)

    class Meta:
        abstract = True


class CodeOmschrijvingMixin(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


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
    db = None  # The DB to use for the query This allws usage of different dbs
    keywords = []  # A set of optional keywords to filter the results further
    preview_size = settings.SEARCH_PREVIEW_SIZE

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
        # this can probably be replaced by the json response mixing I had earlier
        # Serializing the object list
        # Checking if pretty and debug
        resp = {}
        if self.request.GET.get('pretty', False) and settings.DEBUG:
            return render(self.request, "pretty_elastic.html", context=context) 
        resp['object_list'] = list(context['object_list'])
        # Cleaning all but the objects and aggregations
        resp['aggs_list'] = context['aggs_list']

        return HttpResponse(
            json.dumps(resp),
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
        query = q

        # Adding filters
        filters = []
        for filter_keyword in self.keywords:
            val = self.request.GET.get(filter_keyword, None)
            if val:
                filters.append({'term': {filter_keyword: val}})
        # If any filters were given, add them, creating a bool query
        if filters:
            query['query'] = {'bool': {'must': [query['query']]}}
            query['query']['bool']['filter'] = filters

        # Adding sizing if not given
        if 'size' not in query:
            query['size'] = self.preview_size
        # Adding offset in case of paging
        offset = self.request.GET.get('page', None)
        if offset:
            try:
                offset = (int(offset) - 1) * 20
                if offset > 1:
                    query['from'] = offset
            except ValueError:
                # offset is not an int
                pass
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
        response = self.elastic.search(index='zb_bag', body=query)  #, filter_path=['hits.hits._id', 'hits.hits._type'])
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


class Echo(object):
        """
        An object that implements just the write method of the file-like
        interface, for csv file streaming
        """
        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value
