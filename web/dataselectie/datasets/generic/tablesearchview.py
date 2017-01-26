# Python
import logging
import rapidjson
from datetime import date, datetime

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import ListView
from elasticsearch import Elasticsearch

from .elasticsearchmixin import ElasticSearchMixin, BadReq

log = logging.getLogger(__name__)

# =============================================================
# Views
# =============================================================

BAG_APIFIELDS = []


def process_aggs(aggs: dict) -> dict:
    """
    Merging count with regular aggregation for a single level result

    :param aggs:
    :return:
    """

    count_keys = [key for key in aggs.keys() if
                  key.endswith('_count') and key[0:-6] in aggs]
    for key in count_keys:
        aggs[key[0:-6]]['doc_count'] = aggs[key]['value']
        # Removing the individual count aggregation
        del aggs[key]
    return aggs


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
    # request parameters
    request_parameters = None
    # rename fields from elastic
    mapped_elastic_fieldname = {}

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
            response = super(TableSearchView, self).dispatch(request, *args,
                                                             **kwargs)
        except BadReq as e:
            response = HttpResponseBadRequest(content=str(e))
        return response

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

    def render_to_response(self, context: dict,
                           **response_kwargs) -> HttpResponse:
        # Checking if pretty and debug
        resp = {'object_list': list(context['object_list'])}
        # Cleaning all but the objects and aggregations
        try:
            resp['aggs_list'] = context['aggs_list']
        except KeyError:
            pass
        # If there is a total count, adding it as well
        try:
            resp['object_count'] = context['total']
        except KeyError:
            pass
        else:
            resp['page_count'] = int(int(context['total']) / self.preview_size)
            if int(context['total']) % self.preview_size:
                resp['page_count'] += 1

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
        response = self.elastic.search(
            index=settings.ELASTIC_INDICES[self.index], body=query)
        elastic_data = self.fill_ids(response, elastic_data)
        # add aggregations
        self.add_aggregates(response)
        # Enrich result data with neede info
        self.save_context_data(response, elastic_data=elastic_data)

        return elastic_data

    def create_queryset(self, elastic_data: dict) -> QuerySet:
        """
        Generates a query set based on the ids retrieved from elastic
        """
        ids = elastic_data.get('ids', None)
        if ids:
            if isinstance(self.sorts, list):
                qs = self.model.objects.filter(id__in=ids).order_by(*self.sorts)
            elif self.sorts:
                qs = self.model.objects.filter(id__in=ids).order_by(self.sorts)
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

    def add_aggregates(self, response: dict):
        aggs = response.get('aggregations', {})
        self.extra_context_data['aggs_list'] = process_aggs(aggs)
        self.extra_context_data['total'] = response['hits']['total']

    def includeagg(self, aggs: dict) -> dict:
        return aggs

    def add_api_fields(self, item: dict, id_value: str):
        for field in self.apifields:
            self.extra_context_data['items'][id_value][
                field] = self.get_field_value_from_elastic(item, field)

    def get_field_value_from_elastic(self, item: dict, field: str):
        field = self.get_mapped_fieldname(field)
        try:
            value = item['_source'][field]
        except KeyError:
            value = self.get_data_from_function(item, field)

        return value

    def get_mapped_fieldname(self, fieldnm):
        if fieldnm in self.mapped_elastic_fieldname:
            fieldnm = self.mapped_elastic_fieldname[fieldnm]
        return fieldnm

    def get_data_from_function(self, item: dict, field: str):
        try:
            getfield = getattr(self, 'process_' + field)
        except AttributeError:
            pass
        else:
            return getfield(item['_source'])

    # ===============================================
    # Context altering functions to be overwritten
    # ===============================================
    def save_context_data(self, response: dict, elastic_data: dict = None):
        """
        Can be used by the subclass to save extra data to be used
        later to correct context data

        Parameter:
        response - the elastic response dict
        """

        if 'items' not in self.extra_context_data:
            self.extra_context_data['items'] = {}

        for item in response['hits']['hits']:
            el_id = self.define_id(item, elastic_data)
            self.extra_context_data['items'][el_id] = {}
            self.add_api_fields(item, el_id)

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


def _stringify_item_value(value) -> str:
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
