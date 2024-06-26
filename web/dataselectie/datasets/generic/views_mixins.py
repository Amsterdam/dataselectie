# Python
import ast
import codecs
import csv
import io
import json
import logging
from datetime import date, datetime

from typing import Generator

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseBadRequest
from django.views.generic import View
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from pytz import timezone

log = logging.getLogger(__name__)


def stringify_item_value(value) -> str:
    """
    Makes sure that the dict contains only strings for easy jsoning of the dict
    Following actions are taken:
    - Nothing is done to a value that is a string already
    - None is replace by empty string
    - Boolean is converted to string
    - Numbers are converted to string
    - Datetime and Dates are converted to EU norm dates

    Important!
    If NO conversion can be found the same value is returned
    This may, or may not break the jsoning of the object list

    @Parameter:
    value - a value to convert to string

    @Returns:
    The string representation of the value
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, (date, datetime)):
        return value.strftime('%d-%m-%Y')
    elif isinstance(value, list):
        return ' | '.join([stringify_item_value(val) for val in value])
    elif isinstance(value, bool):
        if value:
            return 'Ja'
        return 'Nee'
    elif value is None:
        return ''
    else:
        # Trying repr, otherwise trying str
        try:
            return str(value)
        except:
            try:
                return repr(value)
            except:
                pass
        return ''


def create_geometry_dict(item):
    """
    Creates a geometry dict that can be used to add
    geometry information to the result set

    Returns a dict with geometry information if one
    can be created. If not, an empty dict is returned
    """
    res = {}
    try:
        geom_wgs = GEOSGeometry(
            f"POINT ({item['centroid'][0]} {item['centroid'][1]}) ", srid=4326)
    except(AttributeError, KeyError):
        geom_wgs = None

    if geom_wgs:
        # Convert to wgs
        geom = geom_wgs.transform(28992, clone=True).coords
        geom_wgs = geom_wgs.coords
        res = {
            'geometrie_rd_x': int(geom[0]),
            'geometrie_rd_y': int(geom[1]),
            'geometrie_wgs_lat': (
                '{:.7f}'.format(geom_wgs[1])).replace('.', ','),

            'geometrie_wgs_lon': (
                '{:.7f}'.format(geom_wgs[0])).replace('.', ',')

        }
        item.update(res)


class InvalidParameter(Exception):
    pass


class SingleDispatchMixin(object):
    """
    Checks only allowed methods are handled
    and unifies how they are treated
    """
    # Allowed methods
    http_methods_allowed = ['GET', 'POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        """
        Since there is no difference in the handling of POST
        and GET request. dispatch is overwritten to always go
        to the same handler
        """
        try:
            if self.request.method == 'OPTIONS':
                return super(SingleDispatchMixin, self).dispatch(request, *args,
                                                                 **kwargs)
            if self.request.method in self.http_methods_allowed:
                self.request_parameters = getattr(request, request.method)
                data = self.handle_request(request, *args, **kwargs)
                return self.render_to_response(request, data)

            return self.http_method_not_allowed(request, *args, **kwargs)
        except Exception as exc:
            if isinstance(exc, InvalidParameter):
                response = {
                    'message': 'Bad Request (400)',
                    'detail': str(exc)
                }
                return HttpResponseBadRequest(json.dumps(response), content_type='application/json')
            else:
                raise exc


    def render_to_response(self, request, response):
        return HttpResponse(json.dumps(response),
                            content_type='application/json')


class ElasticSearchMixin(object):
    """
    A mixin provinding several elastic search utility functions

    geo_fields tuple format per dict is as follow:
        - key: the field to use,
        - value: type of geospatial search

    """

    # optional manual filters
    filters = {}
    # A set of optional keywords to filter the results further
    keywords = ()
    geo_fields = [
        {'query_param': 'shape',
         'es_doc_field': 'centroid',
         'es_query_type': 'geo_polygon'}
    ]
    keyword_mapping = {}
    request = None

    def elastic_query(self, query):
        raise NotImplementedError

    def handle_query_size_offset(self, query: dict) -> dict:
        """
        Handles query size and offseting
        By defualt it does nothing
        """
        return query

    def add_page_counters(self, object_count: int) -> dict:
        count = {
            'page_count': object_count // self.preview_size
        }
        if object_count % self.preview_size:
            count['page_count'] += 1
        return count

    def add_elastic_filters(self, query):
        """
        Builds the dictionary query to send to elastic
        Parameters:
        query - The q dict returned from the queries file
        Returns:
        A query dict to send to elastic
        """
        # Adding filters
        if 'filter' in query['query']['bool']:
            filters = query['query']['bool']['filter']
        else:
            filters = []
        # Retrieving the request parameters
        request_parameters = getattr(self.request, self.request.method)

        self._add_keyword_filters(request_parameters, filters)
        self._add_geo_filters(request_parameters, filters)

        if filters:
            query['query']['bool']['filter'] = filters

        return self.handle_query_size_offset(query)

    def _bool_query(self, filters: list, filter_keyword: str, values: list):
        """
        Deal with Multi value filter.
        """
        terms = []

        for xvalue in values:
            terms.append({
                'term': self.get_term_and_value(
                    filter_keyword, xvalue)})

        filters.append({'bool': {"should": terms}})

    def _convert_value_to_list(self, value):
        """
        Convert value safely to Python literal structures:
        strings, numbers, tuples, lists, dicts, booleans, and None.
        """
        try:
            value = ast.literal_eval(value)
            return value
        except (SyntaxError, ValueError):
            pass

        return value

    def _build_filter(self, filters, filter_keyword, value):
        """
        Build term / bool filter for keyword
        """
        value = self._convert_value_to_list(value)

        if isinstance(value, list):
            self._bool_query(filters, filter_keyword, value)
            return

        filters.append({
            'term': self.get_term_and_value(
                filter_keyword, value)})

    def _add_keyword_filters(self, request_parameters, filters):
        """add keyword filters"""

        # Checking for known keyword filters
        for filter_keyword in self.keywords:
            value = request_parameters.get(filter_keyword, None)
            # Since a parameter can be 0, which evalutes to False, a check
            # is actually made that the value is not None
            if value is None:
                continue

            self._build_filter(filters, filter_keyword, value)

        # add custom filter
        for filter_keyword, value in self.filters.items():
            self._build_filter(filters, filter_keyword, value)

    def _add_geo_filters(self, request_parameters, filters):
        """ Adding geo filters """

        def unmarshal(val):
            """Checking if val needs to be converted from string"""
            if isinstance(val, str):
                try:
                    val = json.loads(val)
                except ValueError:
                    # Bad formatted json.
                    val = []
            return val

        for geo_dict in self.geo_fields:
            val = request_parameters.get(geo_dict['query_param'], None)
            if val is not None:
                val = unmarshal(val)
                # Only adding filter if at least 3 points are given
                if (len(val)) > 2:
                    if geo_dict['es_query_type'] == 'geo_polygon':
                        filters.append(
                            {'geo_polygon': {geo_dict['es_doc_field']: {'points': val}}})
                    elif geo_dict['es_query_type'] == 'geo_shape':
                        val.append(val[0]) #close polygon
                        filters.append({
                            "geo_shape": {
                                geo_dict['es_doc_field']: {
                                    "shape": {
                                        "type": "polygon",
                                        "coordinates" : [val]
                                    },
                                    "relation": "intersects"
                                }
                            }
                        })

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
        # looking for a query
        query_string = self.request_parameters.get('query', None)

        # Building the query
        q = self.elastic_query(query_string)
        query = self.add_elastic_filters(q)
        # Performing the search
        response = self.elastic.search(
            index=settings.ELASTIC_INDICES[self.index], body=query, 
            timeout=settings.ELASTIC_SEARCH_TIMEOUT_SECONDS)
        elastic_data = {
            'aggs_list': self.process_aggs(response.get('aggregations', {})),
            'object_list': [item['_source'] for item in
                            response['hits']['hits']],
            'object_count': response['hits']['total']}

        try:
            elastic_data.update(
                self.add_page_counters(int(elastic_data['object_count'])))
        except TypeError:
            # There is no definition for the preview size
            pass

        return elastic_data

    def get_term_and_value(self, filter_keyword: str, val: str) -> dict:
        """
        Some fields need to be searched raw while others are analysed with
        the default string analyser which will automatically convert the fields
        to lowercase in de the index.
        :param filter_keyword: the keyword in the index to search on
        :param val: the value we are searching for
        :return: a small dict that contains the key/value pair
                 to use in the ES search.
        """
        # checking for keyword mapping to the actual elastic name
        filter_keyword = self.keyword_mapping.get(
            filter_keyword, filter_keyword)

        return {filter_keyword: val}

    def process_aggs(self, aggs):
        """
        Process the aggregation create by elastic.
        It seaches for agg_name and agg_name_count
        and then adds its
        value to the agg_name, removing the agg_name count

        This creates a unified aggregation for the front end
        to work with
        """
        count_keys = [
            key for key in aggs.keys() if
            key.endswith('_count') and key[0:-6] in aggs]

        for key in count_keys:
            aggs[key[0:-6]]['doc_count'] = aggs[key]['value']
            # Removing the individual count aggregation
            del aggs[key]

        return aggs


class TableSearchView(ElasticSearchMixin, SingleDispatchMixin, View):
    """
    A base class to generate tables from search results
    """
    # attributes:
    # ---------------------
    # The name of the index to search in
    index = None  # 'DS_INDEX'
    # A set of optional keywords to filter the results further
    keywords = None
    # The name of the index to search in
    # mapping keywords from parameters to elastic fields
    keyword_mapping = {}
    # request parameters
    request_parameters = None

    preview_size = settings.SEARCH_PREVIEW_SIZE  # type int

    def __init__(self):
        super(View, self).__init__()
        self.elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS, retry_on_timeout=True,
            refresh=True
        )

    def handle_request(self, request, *args, **kwargs):
        elastic_data = self.load_from_elastic()
        # customize agg filters results for frontend
        self.custom_aggs(elastic_data, request)
        # See method for details
        return self.filter_data(elastic_data, request)

    def custom_aggs(self, elastic_data, request):
        """
        Allow custom filtering on aggs
        """
        pass

    def handle_query_size_offset(self, query: dict) -> dict:
        """
        Handles query size and offsets
        """
        # Adding sizing if not given. In bag we also accept page_size parameter
        size = self.request_parameters.get('size', self.request_parameters.get('page_size', None))
        if size:
            try:
                size = int(size)
            except ValueError:
                raise InvalidParameter(f"Invalid size {size}")
            if size < 1 or size > settings.MAX_SEARCH_ITEMS:
                raise InvalidParameter(f"Invalid size {size}. Should be between 1 and {settings.MAX_SEARCH_ITEMS}")
            if size:
                self.preview_size = size

        if 'size' not in query and self.preview_size:
            query['size'] = self.preview_size
        page = self.request_parameters.get('page', None)
        if page and self.preview_size:
            try:
                page = int(page)
            except ValueError:
                raise InvalidParameter(f"Invalid page {page}")
            if page * self.preview_size > settings.MAX_SEARCH_ITEMS:
                raise InvalidParameter(f"Invalid page:{page}, size:{self.preview_size}, page * size > {settings.MAX_SEARCH_ITEMS}")
            elif page < 1:
                raise InvalidParameter(f"Invalid page {page}. Cannot be less then 1")
            offset = (page - 1) * self.preview_size
            if offset > 0:
                query['from'] = offset
        return query

    def filter_data(self, elastic_data, request):
        """
        Allow implementations to do additional filtering based on
        criteria that are hard (or impossible) to mix into the
        elastic query
        :param elastic_data:
            The result that will be returned to the upstream view
        :param request: The incoming request
        :return:
            Something that resembles the original data minus sensitive fields.
        """
        return elastic_data


class GeoLocationSearchView(ElasticSearchMixin, SingleDispatchMixin, View):
    """
    A base class to search elastic for geolocation
    of items
    """
    # To overwrite methods
    index = 'DS_INDEX'  # type: str

    def __init__(self):
        super(View, self).__init__()
        self.request_parameters = None
        self.elastic = Elasticsearch(
            hosts=settings.ELASTIC_SEARCH_HOSTS, retry_on_timeout=True,
            refresh=True
        )

    def handle_request(self, request, *args, **kwargs):
        """
        Handling the request for goelocation information
        """
        # looking for a query
        query_string = self.request_parameters.get('query', None)

        # Building the query
        q = self.elastic_query(query_string)
        query = self.add_elastic_filters(q)
        # Removing size limit
        query['size'] = settings.MAX_SEARCH_ITEMS
        # Performing the search
        response = self.elastic.search(
            index=settings.ELASTIC_INDICES[self.index],
            body=query,
            _source_include=['centroid']
        )
        data = self.build_response(response)

        log.info('response count %s', data['object_count'])
        return data

    @staticmethod
    def build_response(response):

        resp = {
            'object_count': response['hits']['total'],
            'object_list': response['hits']['hits']
        }
        return resp


class CSVExportView(TableSearchView):
    """
    A base class to generate csv exports
    """
    # This is not relevant for csv export
    preview_size = None
    # The fields we use in the csv
    field_names = []
    # The pretty version of the headers
    csv_headers = []

    def item_data_update(self, item, _request):
        """
        Allow for subclasses to add custom fields to the item before it is
        stringified for export
        """
        return item

    def load_from_elastic(self) -> Generator:
        """
        Instead of normal results
        it returns an elastic scroll api generator
        """
        query_string = self.request_parameters.get('query', None)
        # Building the query
        q = self.elastic_query(query_string)
        query = self.add_elastic_filters(q)
        # Making sure there is no pagination
        if query is not None and 'from' in query:
            del query['from']
        # Returning the elastic generator
        return scan(
            self.elastic, query=query,
            index=settings.ELASTIC_INDICES[self.index])

    def result_generator(self, request, es_generator):
        """
        Generate the result set for the CSV eport
        """
        batch_size = settings.DOWNLOAD_BATCH

        write_buffer = io.StringIO()  # The buffer to stream to
        writer = csv.DictWriter(write_buffer, self.field_names, delimiter=';')
        more = True  # More results flag

        header_dict = {}  # A dict for the CSV headers
        for i in range(len(self.field_names)):
            header_dict[self.field_names[i]] = self.csv_headers[i]

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
            item_count = 0
            # Collecting items for batch
            for item_hit in es_generator:
                item = item_hit['_source']
                item_count += 1
                # Allowing for custompdates
                item = self.item_data_update(item, request)
                # Making sure all the data is in string form
                self.sanitize_fields(item, self.field_names)
                resp = {}
                # Only returning fields from the headers
                for key in self.field_names:
                    resp[key] = item.get(key, '')
                writer.writerow(resp)
                if item_count == batch_size:
                    break

            yield read_and_empty_buffer()

            # Stop the run, if end is reached
            more = item_count >= batch_size

        # Yielding (batch size) results
        yield read_and_empty_buffer()

    def sanitize_fields(self, item, field_names):
        pass

    def render_to_response(self, request, data, **response_kwargs):
        gen = self.result_generator(request, data)
        response = StreamingHttpResponse(gen, content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; ' \
            'filename="export_{0:%Y%m%d_%H%M%S}.csv"'.format(datetime.now(
                tz=timezone('Europe/Amsterdam')))
        return response
