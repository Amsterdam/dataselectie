# Python
import codecs
import csv
from datetime import date, datetime
import io
import json
import logging
from typing import Generator
# Packages
from django.conf import settings
from django.db.models import QuerySet
from django.db.models.fields.related import ManyToManyField
from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.views.generic import View
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from pytz import timezone


log = logging.getLogger(__name__)


def stringify_item_value(value) -> str:
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


class SingleDispatchMixin(object):
    """
    Checks only allowed methods are handled
    and unifies how they are treated
    """
    # Allowed methods
    http_methods_allowed = ['GET', 'POST']

    def dispatch(self, request, *args, **kwargs):
        """
        Since there is no difference in the handling of POST
        and GET request. dispatch is overwritten to always go
        to the same handler
        """
        if self.request.method in self.http_methods_allowed:
            self.request_parameters = getattr(request, request.method)
            response = self.handle_request(request, *args, **kwargs)
            return self.render_to_response(response)
        else:
            return self.http_method_not_allowed(request, *args, **kwargs)

    def render_to_response(self, response):
        return HttpResponse(json.dumps(response), content_type='application/json')


class ElasticSearchMixin(object):
    """
    A mixin provinding several elastic search utility functions

    geo_fields tuple format per dict is as follow:
        - key: the field to use,
        - value: type of geospatial search

    """

    # A set of optional keywords to filter the results further
    keywords = ()
    geo_fields = {
        'shape': ['centroid', 'geo_polygon'],
    }
    raw_fields = []
    keyword_mapping = {}
    default_search = 'term'
    request = None

    def elastic_query(self, query):
        raise NotImplemented

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
        filters = []
        # Retrieving the request parameters
        request_parameters = getattr(self.request, self.request.method)

        # Checking for known keyword filters
        for filter_keyword in self.keywords:
            val = request_parameters.get(filter_keyword, None)
            # Since a parameter can be 0, which evalutes to False, a check
            # is actually made that the value is not None
            if val is not None:
                filters.append({self.default_search: self.get_term_and_value(filter_keyword, val)})

        # Adding geo filters
        for term, geo_type in self.geo_fields.items():
            val = request_parameters.get(term, None)
            if val is not None:
                # Checking if val needs to be converted from string
                if isinstance(val, str):
                    try:
                        val = json.loads(val)
                    except ValueError:
                        # Bad formatted json.
                        val = []
                # Only adding filter if at least 3 points are given
                if (len(val)) > 2:
                    filters.append({geo_type[1]: {geo_type[0]: {'points': val}}})

        if filters:
            query['query']['bool']['filter'] = filters

        return self.handle_query_size_offset(query)

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
            index=settings.ELASTIC_INDICES[self.index], body=query)
        elastic_data = {
            'aggs_list':  self.process_aggs(response.get('aggregations', {})),
            'object_list': [item['_source'] for item in response['hits']['hits']],
        }
        # Add total count
        elastic_data['object_count'] = response['hits']['total']
        try:
            elastic_data.update(self.add_page_counters(int(elastic_data['object_count'])))
        except TypeError:
            # There is no definition for the preview size
            pass

        return elastic_data

    def get_term_and_value(self, filter_keyword: str, val: str) -> dict:
        """
        Some fields need to be searched raw while others are analysed with the default string analyser which will
        automatically convert the fields to lowercase in de the index.
        :param filter_keyword: the keyword in the index to search on
        :param val: the value we are searching for
        :return: a small dict that contains the key/value pair to use in the ES search.
        """
        # checking for keyword mapping to the actual elastic name
        filter_keyword = self.keyword_mapping.get(filter_keyword, filter_keyword)
        # Checking if a raw field is needed
        if filter_keyword in self.raw_fields:
            filter_keyword = "{}.raw".format(filter_keyword)
        return {filter_keyword: val}

    def process_aggs(self, aggs):
        """
        Process the aggregation create by elastic.
        It seaches for agg_name and agg_name_count and then adds its
        value to the agg_name, removing the agg_name count

        This creates a unified aggregation for the front end
        to work with
        """
        count_keys = [key for key in aggs.keys() if
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
    index = 'DS_INDEX'
    # A set of optional keywords to filter the results further
    keywords = None
    # The name of the index to search in
    raw_fields = None
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
        elastic_data = self.load_from_elastic()  # See method for details
        return elastic_data

    # Tableview methods

    def paginate(self, offset: int, q: dict) -> dict:
        # Sanity check to make sure we do not pass 10000
        if offset and settings.MAX_SEARCH_ITEMS:
            if q['size'] + offset > settings.MAX_SEARCH_ITEMS:
                size = settings.MAX_SEARCH_ITEMS - offset
                q['size'] = size if size > 0 else 0
        return q

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
                int_offset = int(offset)
            except ValueError:
                int_offset = 1
            if int_offset > 100:
                int_offset = 100
            offset = (int_offset - 1) * settings.SEARCH_PREVIEW_SIZE
            if offset > 1:
                query['from'] = offset
        return self.paginate(offset, query)


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
        resp = self.bldresponse(response)

        log.info('response count %s', resp['object_count'])
        return resp

    def bldresponse(self, response):
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
    # The headers of the csv
    headers = []
    # The pretty version of the headers
    pretty_headers = []

    def item_data_update(self, item):
        """
        Allow for subclasses to add custom fields to the item before it is
        strigified for export
        """
        pass

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
            del (query['from'])
        # Returning the elastic generator
        return scan(self.elastic, query=query, index=settings.ELASTIC_INDICES[self.index])

    # TODO type es_generator
    def result_generator(self, es_generator, batch_size: int=100):
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
        item_count = 0
        while more:
            item_count = 0
            # Collecting items for batch
            for item_hit in es_generator:
                item = item_hit['_source']
                item_count += 1
                # Allowing for custom updates
                self.item_data_update(item)
                # Making sure all the data is in string form
                item.update(
                    {k: stringify_item_value(v) for k, v in item.items() if
                    not isinstance(v, str) or v is None}
                )
                resp = {}
                # Only returning fields from the headers
                for key in self.headers:
                    resp[key] = item.get(key, '')
                writer.writerow(resp)

            # Yielding results
            yield read_and_empty_buffer()
            # Stop the run, if end is reached
            more = item_count >= batch_size

    def render_to_response(self, data, **response_kwargs):
        # Returning a CSV
        # Streaming!
        gen = self.result_generator(data)
        response = StreamingHttpResponse(gen, content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; ' \
            'filename="export_{0:%Y%m%d_%H%M%S}.csv"'.format(datetime.now(
                tz=timezone('Europe/Amsterdam')))
        return response
