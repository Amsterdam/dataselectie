# Python
from datetime import date, datetime
import json
from typing import List
# Packages
from django.conf import settings
from django.db import models
from django.db.models.fields.related import ManyToManyField
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan


# =============================================================
# Views
# =============================================================


class TableSearchView(ListView):
    """
    A base class to generate tables from search results
    """
    # attributes:
    # ---------------------
    # The model class to use
    model = None  # type: models.Model
    # The name of the index to search in
    index = ''  # type: str
    # A set of optional keywords to filter the results further
    keywords = None  # type: Tuple[str]
    # Fields in elastic that should be used in raw version
    raw_fields = []  # type: List[str]
    preview_size = settings.SEARCH_PREVIEW_SIZE

    def __init__(self):
        super(ListView, self).__init__()
        self.elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS, retry_on_timeout=True,
            refresh=True
        )
        self.extra_context_data = None  # Used to store data from elastic used in context

    def _stringify_item_value(self, value):
        """
        Makes sure that the dict contains only strings for easy jsoning of the dict
        Following actions are taken:
        - None is replace by empty string
        - Boolean is converted to string
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
            return value.strftime('%d-%m-%Y')
        elif value is None:
            return ''
        else:
            # Trying repr, otherwise trying
            try:
                return repr(value)
            except:
                try:
                    return str(value)
                except:
                    pass
            return ''

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
        resp['object_list'] = list(context['object_list'])
        # Cleaning all but the objects and aggregations
        try:
            resp['aggs_list'] = context['aggs_list']
        except KeyError:
            pass
        # If there is a total count, adding it as well
        try:
            resp['object_count'] = context['total']
            resp['page_count'] = int(int(context['total']) / self.preview_size)
            if int(context['total']) % self.preview_size:
                resp['page_count'] += 1
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
            if val is not None:
                filters.append({'term': self.get_term_and_value(filter_keyword, val)})
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
        offset = self.request.GET.get('page', None)
        if offset:
            try:
                offset = (int(offset) - 1) * settings.SEARCH_PREVIEW_SIZE
                if offset > 1:
                    query['from'] = offset
            except ValueError:
                # offset is not an int
                pass

        return self.paginate(offset, query)

    def paginate(self, offset, q):
        # Sanity check to make sure we do not pass 10000
        if offset and settings.MAX_SEARCH_ITEMS:
            if q['size'] + offset > settings.MAX_SEARCH_ITEMS:
                q['size'] = settings.MAX_SEARCH_ITEMS - offset  # really ??
        return q

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
        response = self.elastic.search(index=settings.ELASTIC_INDICES['DS_BAG'], body=query)
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
            return self.model.objects.filter(id__in=ids).order_by(
                '_openbare_ruimte_naam', 'huisnummer', 'huisletter',
                'huisnummer_toevoeging').values()[:self.preview_size]
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

    # ===============================================
    # Context altering functions to be overwritten
    # ===============================================
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

    def get_term_and_value(self, filter_keyword, val):
        """
        Some fields need to be searched raw while others are analysed with the default string analyser which will
        automatically convert the fields to lowercase in de the index.
        :param filter_keyword: the keyword in the index to search on
        :param val: the value we are searching for
        :return: a small dict that contains the key/value pair to use in the ES search.
        """
        if filter_keyword in self.raw_fields:
            filter_keyword = "{}.raw".format(filter_keyword)
        return {filter_keyword: val}


class CSVExportView(TableSearchView):
    """
    A base class to generate csv exports
    """
    # This is not relevant for csv export
    preview_size = None  # type: int
    # The headers of the csv
    headers = []  # type: List[str]
    # The pretty version of the headers
    pretty_headers = []  # type: List[str]

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
        if query is not None and 'from' in query:
            del (query['from'])
        # Returning the elastic generator
        return scan(self.elastic, query=query)

    def result_generator(self, es_generator, batch_size=100):
        """
        Generate the result set for the CSV eport
        """
        # Als eerst geef de headers terug
        header_dict = {}
        for i in range(len(self.headers)):
            header_dict[self.headers[i]] = self.pretty_headers[i]
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
            qs = self.model.objects.filter(id__in=list(items.keys())).select_related()
            qs = self._convert_to_dicts(qs)
            # Pairing the data
            data = self._combine_data(qs, items)
            for item in data:
                # Only returning fields from the headers
                resp = {}
                for key in self.headers:
                    resp[key] = item.get(key, '')
                yield resp

    def _model_to_dict(self, item):
        """
        Converts a django model to a dict.
        It does not do a deep conversion
        """
        data = {}
        properties = item._meta
        for field in properties.concrete_fields + properties.many_to_many:
            if isinstance(field, ManyToManyField):
                data[field.name] = list(field.value_from_object(item).values_list('pk', flat=True))
            else:
                data[field.name] = field.value_from_object(item)
        return data

    def _convert_to_dicts(self, qs):
        """
        Converts every item in the queryset to a dict
        with property name as key and property value as value
        Overwrite this fnction for custom fields, or following
        relations
        """
        return [self._model_to_dict(d) for d in qs]

    def _combine_data(self, data, es):
        """
        Combines the elastic data with the
        data retrieved from the query
        """
        for item in data:
            # Making sure all the data is in string form
            item.update(
                {k: self._stringify_item_value(v) for k, v in item.items() if
                 not isinstance(v, str)}
            )
            # Adding the elastic context
            for key, value in es[item['id']]['_source'].items():
                item[key] = value
        return data


class Echo(object):
    """
    An object that implements just the write method of the file-like
    interface, for csv file streaming
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
