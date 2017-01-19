# Python
import codecs
from typing import Generator
import copy
import csv
import logging
from datetime import date, datetime
import io
# Packages
from django.conf import settings
from django.db.models.fields.related import ManyToManyField
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.views.generic import ListView, View
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from pytz import timezone
import rapidjson
# Project
from datasets.bag.models import Nummeraanduiding

log = logging.getLogger(__name__)

# =============================================================
# Views
# =============================================================

BAG_APIFIELDS = []


class BadReq(Exception):
    pass


class ElasticSearchMixin(object):
    """
    A mixin provinding several elastic search utility functions

    geo_fields tuple format per dict is as follow:
        - key: the field to use,
        - value: type of geospatial search

    """

    # A set of optional keywords to filter the results further
    keywords = ()
    raw_fields = []
    geo_fields = {}
    keyword_mapping = {}
    fixed_filters = []
    default_search = 'term'
    allowed_parms = ('page', 'shape')
    request = None

    def build_elastic_query(self, query):
        """
        Builds the dictionary query to send to elastic
        Parameters:
        query - The q dict returned from the queries file
        Returns:
        The following query dict is sent to elastic
        from dataselectie-hr and will return the
        vestigingsinfo and the bag info,
        The matchall will make sure that the
        linked info from bag is retrieved

        {
            "query":{
                "bool": {
                    "must": [
                        {
                            "term": {"_type": "bag_locatie"}
                        },{
                            "has_child": {
                                "type": "vestiging",
                                "query": [
                                    {
                                        "term": {"sbi_code": "6420"}
                                    }
                                ],
                                "inner_hits":{}
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "postcode": {
                    "terms": {"field": "postcode"},
                    "vestiging": {
                        "children": {
                            "type": "vestiging"
                        },
                        "aggs": {
                            "sbi_code":{
                                "terms": { "field":"sbi_code"}
                            }
                        }
                    }
                }
            }
        }
        The "match_all" can be replaced with selections on the
        parent. i.e. buurtnaam:
        {
            "bool": {
                "must: [
                    { "match": {"stadsdeel_naam": "Centrum"}}
                ]
            }
        }
        """
        # Adding filters
        if self.fixed_filters:
            filters = copy.copy(self.fixed_filters)
        else:
            filters = []
        # Retrieving the request parameters
        request_parameters = getattr(self.request, self.request.method)

        entered_parms = [prm for prm in request_parameters.keys() if prm not in self.allowed_parms]

        child_filters = []
        self.selection = []         # cash bashing!
        for filter_keyword in self.keywords:
            val = request_parameters.get(filter_keyword, None)
            if val is not None:     # parameter is entered
                del entered_parms[entered_parms.index(filter_keyword)]
                filters, child_filters = self.proc_parameters(filter_keyword, val, child_filters, filters)
                self.filterkeys(filter_keyword, val)

        if len(entered_parms):
            wrongparms = ','.join(entered_parms)
            raise BadReq(entered_parms, "Parameter(s) {} not supported".format(wrongparms))

        # Adding geo filters
        for term, geo_type in self.geo_fields.items():
            val = request_parameters.get(term, None)
            if val is not None:
                # Checking if val needs to be converted from string
                if isinstance(val, str):
                    try:
                        val = rapidjson.loads(val)
                    except ValueError:
                        # Bad formatted json.
                        val = []
                # Only adding filter if at least 3 points are given
                if (len(val)) > 2:
                    filters.append({geo_type[1]: {geo_type[0]: {'points': val}}})

        query = self.build_el_query(filters, child_filters, query)

        return self.handle_query_size_offset(query)

    def filterkeys(self, filter_keyword: str, val: str):
        pass

    def proc_parameters(self, filter_keyword: str, val: str, child_filters: list, filters: list) -> (list, list):
        filters.append({self.default_search: self.get_term_and_value(filter_keyword, val)})
        return filters, child_filters

    def build_el_query(self, filters: list, child_filters: list, query: dict) -> dict:
        """
        Allows for addition of extra conditions if keyword mapping
        found, default it creates a bool query
        :param filters: Filters for the primary (parent) selection
        :param child_filters: Filters for the secundary (child) selection
        :param query: query to start with
        :return: query
        """
        filters += child_filters
        query['query'] = {
            'bool': {
                'must': [query['query']],
                'filter': filters,
            }
        }
        return query

    def fill_ids(self, response: dict, elastic_data: dict) -> dict:
        # Can be overridden in the view to allow for other primary keys
        for hit in response['hits']['hits']:
            elastic_data['ids'].append(hit['_id'])
        return elastic_data

    def handle_query_size_offset(self, query: dict) -> dict:
        """
        Handles query size and offseting
        By defualt it does nothing
        """
        return query

    def get_term_and_value(self, filter_keyword: str, val: str) -> dict:
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


class GeoLocationSearchView(ElasticSearchMixin, View):
    """
    A base class to search elastic for geolocation
    of items
    """
    http_method_names = ['get', 'post']
    # To overwrite methods
    index = 'DS_INDEX'  # type: str

    def __init__(self):
        super(View, self).__init__()
        self.request_parameters = None
        self.elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS, retry_on_timeout=True,
            refresh=True
        )

    def elastic_query(self, query):
        raise NotImplemented

    def dispatch(self, request, *args, **kwargs):
        self.request_parameters = getattr(request, request.method)

        if request.method.lower() in self.http_method_names:
            try:
                response = self.handle_request(self, request, *args, **kwargs)
            except BadReq as e:
                response = HttpResponseBadRequest(content=str(e))
            return response
        else:
            return self.http_method_not_allowed(request, *args, **kwargs)

    def handle_request(self, request, *args, **kwargs):
        """
        Handling the request for goelocation information
        """
        # looking for a query
        query_string = self.request_parameters.get('query', None)

        # Building the query
        q = self.elastic_query(query_string)
        query = self.build_elastic_query(q)
        # Removing size limit
        query['size'] = settings.MAX_SEARCH_ITEMS
        # Performing the search
        log.info('use index %s', settings.ELASTIC_INDICES[self.index])
        response = self.elastic.search(
            index=settings.ELASTIC_INDICES[self.index],
            body=query,
            _source_include=['centroid']
        )
        resp = {
            'object_count': response['hits']['total'],
            'object_list': response['hits']['hits']
        }
        log.info('response count %s', resp['object_count'])
        return HttpResponse(
            rapidjson.dumps(resp),
            content_type='application/json'
        )


class TableSearchView(ElasticSearchMixin, ListView):
    """
    A base class to generate tables from search results
    """
    # attributes:
    # ---------------------
    # The model class to use
    model = None
    # The name of the index to search in
    index = 'DS_INDEX'
    # A set of optional keywords to filter the results further
    keywords = None
    # The name of the index to search in
    raw_fields = None
    # Fixed filters that are always applied
    fixed_filters = []
    # Sorting of the queryset
    sorts = []
    # mapping keywords
    keyword_mapping = {}
    # context data saved
    extra_context_data = {'items': {}}
    # apifields
    apifields = []

    preview_size = settings.SEARCH_PREVIEW_SIZE  # type int
    http_method_names = ['get', 'post']

    def elastic_query(self, query):
        raise NotImplemented

    def __init__(self):
        super(ListView, self).__init__()
        self.elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS, retry_on_timeout=True,
            refresh=True
        )

    def dispatch(self, request, *args, **kwargs):
        self.request_parameters = getattr(request, request.method)
        try:
            response = super(TableSearchView, self).dispatch(request, *args, **kwargs)
        except BadReq as e:
            response = HttpResponseBadRequest(content=str(e))
        return response

    def _stringify_item_value(self, value) -> str:
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
        if isinstance(value, date) or isinstance(value, datetime):
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
    def get_queryset(self) -> QuerySet:
        """
        This function is called by list view to generate the query set
        It is overwritten to first use elastic to retrieve the ids then
        return a queryset based on the ids
        """
        elastic_data = self.load_from_elastic()  # See method for details
        qs = self.create_queryset(elastic_data)
        return qs

    def render_to_response(self, context: dict, **response_kwargs) -> HttpResponse:
        # Checking if pretty and debug
        resp = {}
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

        return self.Send_Response(resp, response_kwargs)

    def Send_Response(self, resp: dict, response_kwargs) -> HttpResponse:

        return HttpResponse(rapidjson.dumps(resp),
                            content_type='application/json',
                            **response_kwargs)
    # Tableview methods

    def paginate(self, offset: int, q: dict) -> dict:
        # Sanity check to make sure we do not pass 10000
        if offset and settings.MAX_SEARCH_ITEMS:
            if q['size'] + offset > settings.MAX_SEARCH_ITEMS:
                size = settings.MAX_SEARCH_ITEMS - offset
                q['size'] = size if size > 0 else 0
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
        elastic_data = {'ids': [], 'filters': {}, 'extra_data': []}
        # looking for a query
        query_string = self.request_parameters.get('query', None)

        # Building the query
        q = self.elastic_query(query_string)
        query = self.build_elastic_query(q)
        # Performing the search
        response = self.elastic.search(index=settings.ELASTIC_INDICES[self.index], body=query)
        elastic_data = self.fill_ids(response, elastic_data)
        # add aggregations
        self.add_aggs(response)
        # Enrich result data with neede info
        self.save_context_data(response, elastic_data=elastic_data)

        return elastic_data

    def create_queryset(self, elastic_data: dict) -> QuerySet:
        """
        Generates a query set based on the ids retrieved from elastic
        """
        ids = elastic_data.get('ids', None)
        if ids:
            if self.sorts:
                qs = self.model.objects.filter(id__in=ids).order_by(*self.sorts)
            else:
                qs = self.model.objects.filter(id__in=ids)
            return qs.values()[:self.preview_size]
        else:
            # No ids where found
            return self.model.objects.none().values()

    def handle_query_size_offset(self, query: dict) -> dict:
        """
        Handles query size and offseting
        """
        # Adding sizing if not given
        if 'size' not in query and self.preview_size:
            query['size'] = self.preview_size
        # Adding offset in case of paging
        offset = self.request_parameters.get('page', None)
        if offset:
            try:
                offset = (int(offset) - 1) * settings.SEARCH_PREVIEW_SIZE
                if offset > 1:
                    query['from'] = offset
            except ValueError:
                # offset is not an int
                pass
        return self.paginate(offset, query)

    def get_context_data(self, **kwargs) -> dict:
        """
        Overwrite the context retrital
        """
        context = super(TableSearchView, self).get_context_data(**kwargs)
        context = self.update_context_data(context)
        return context

    def add_aggs(self, response: dict):
        aggs = response.get('aggregations', {})
        self.extra_context_data['aggs_list'] = self.process_aggs(aggs)
        self.extra_context_data['total'] = response['hits']['total']

    def includeagg(self, aggs: dict) -> dict:
        return aggs

    def add_api_fields(self, item: dict, id: str):
        for field in self.apifields:
            try:
                self.extra_context_data['items'][id][field] = \
                    item['_source'][field]
            except:
                self.extra_context_data['items'][id][field] = None
                try:
                    getfield = getattr(self, 'process_' + field)
                except AttributeError:
                    pass
                else:
                    self.extra_context_data['items'][id][field] = getfield(item['_source'])

    def process_aggs(self, aggs: dict) -> dict:
        """
        Merging count with regular aggregation for a single level result

        :param aggs:
        :return:
        """

        count_keys = [key for key in aggs.keys() if key.endswith('_count') and key[0:-6] in aggs]
        for key in count_keys:
            aggs[key[0:-6]]['doc_count'] = aggs[key]['value']
            # Removing the individual count aggregation
            del aggs[key]
        return aggs

    # ===============================================
    # Context altering functions to be overwritten
    # ===============================================
    def save_context_data(self, response: dict, elastic_data: dict=None):
        """
        Can be used by the subclass to save extra data to be used
        later to correct context data

        Parameter:
        response - the elastic response dict
        """

        if 'items' not in self.extra_context_data:
            self.extra_context_data = {'items': {}}

        for item in response['hits']['hits']:
            el_id = self.define_id(item, elastic_data)
            self.extra_context_data['items'][el_id] = {}
            self.add_api_fields(item, el_id)

        self.define_total(response)

    def update_context_data(self, context):
        """
        Enables the subclasses to update/change the object list
        """
        return context

    def define_id(self, item: dict, elastic_data: dict) -> str:
        """
        Define the id that is used to retrieve the extra context data
        :param item:
        :param elastic_data:
        :return: id
        """
        return item['_id']

    def define_total(self, response: dict):
        self.extra_context_data['total'] = response['hits']['total']


class CSVExportView(TableSearchView):
    """
    A base class to generate csv exports
    """
    # This is not relevant for csv export
    preview_size = None
    # The headers of the csv
    headers = []
    # The pretty version of the headers
    pretty_headers = []

    def get_queryset(self) -> Generator:
        """
        Instead of an actual queryset,
        it returns an elastic scroll api generator
        """
        query_string = self.request_parameters.get('query', None)
        # Building the query
        q = self.elastic_query(query_string)
        query = self.build_elastic_query(q)
        # Making sure there is no pagination
        if query is not None and 'from' in query:
            del (query['from'])

        # Returning the elastic generator
        return scan(
            self.elastic, query=query,
            index=settings.ELASTIC_INDICES[self.index])

    def result_generator(self, es_generator: Generator, batch_size: int=100):
        """
        Generate the result set for the CSV eport
        """
        write_buffer = io.StringIO()  # The buffer to stream to
        writer = csv.DictWriter(write_buffer, self.headers, delimiter=';')
        more = True  # More results flag
        header_dict = {}  # A dict for the CSV headers
        for i in range(len(self.headers)):
            header_dict[self.headers[i]] = self.pretty_headers[i]

        # A func to read and empty the buffer
        def read_and_empty_buffer():
            write_buffer.seek(0)
            buffer_data = write_buffer.read()
            write_buffer.seek(0)
            write_buffer.truncate()
            return buffer_data

        # Yielding BOM for utf8 encoding
        yield codecs.BOM_UTF8
        # Yielding headers as first line
        writer.writerow(header_dict)
        yield read_and_empty_buffer()

        # Yielding results in batches of batch_size
        while more:

            items = {}
            # Collecting items for batch
            for item in es_generator:
                items = self._fill_item(items, item)
                # Breaking on batch size
                if len(items) >= batch_size:
                    break

            # Retrieving the database data

            qs = self.model.objects.filter(id__in=list(items.keys()))
            qs = self._convert_to_dicts(qs)

            # Pairing the data
            data = self._combine_data(qs, items)
            for item in data:
                # Only returning fields from the headers
                resp = {}
                for key in self.headers:
                    resp[key] = item.get(key, '')
                writer.writerow(resp)
            yield read_and_empty_buffer()

            # Stop the run, if end is reached
            more = len(items) >= batch_size

    def _model_to_dict(self, item: Nummeraanduiding) -> dict:
        """
        Converts a django model to a dict.
        It does not do a deep conversion
        """
        data = {}  # type dict[str, str]
        properties = item._meta
        for field in properties.concrete_fields + properties.many_to_many:
            if isinstance(field, ManyToManyField):
                data[field.name] = list(
                    field.value_from_object(item).values_list('pk', flat=True))
            else:
                data[field.name] = field.value_from_object(item)
        return data

    def _convert_to_dicts(self, qs) -> list:
        """
        Converts every item in the queryset to a dict
        with property name as key and property value as value
        Overwrite this fnction for custom fields, or following
        relations
        """
        return [self._model_to_dict(d) for d in qs]

    def _combine_data(self, data: list, es: dict) -> list:
        """
        Combines the elastic data with the
        data retrieved from the query
        """
        for item in data:
            # Making sure all the data is in string form
            item.update(
                {k: self._stringify_item_value(v) for k, v in item.items() if
                 not isinstance(v, str) or v is None}
            )
            # Adding the elastic context
            for key, value in es[item['id']]['_source'].items():
                item[key] = value
        return data

    def _fill_item(self, items, item):
        """
        Function can be overwritten in the using class to allow for
        specific output (hr has multi outputs

        :param items:   Resulting dictionary containing the
        :param item:    Item from elastic
        :return: items
        """
        items[item['_id']] = item

        return items

    def render_to_response(self, context, **response_kwargs):
        # Returning a CSV
        # Streaming!
        gen = self.result_generator(context['object_list'])
        response = StreamingHttpResponse(gen, content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; ' \
            'filename="export_{0:%Y%m%d_%H%M%S}.csv"'.format(datetime.now(
                tz=timezone('Europe/Amsterdam')))
        return response
