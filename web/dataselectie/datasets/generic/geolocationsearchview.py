# Python
import logging
# Packages
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from elasticsearch import Elasticsearch
import rapidjson
# Project
from .elasticsearchmixin import ElasticSearchMixin, BadReq

log = logging.getLogger(__name__)


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
        resp = self.bldresponse(response)

        log.info('response count %s', resp['object_count'])
        return HttpResponse(
            rapidjson.dumps(resp),
            content_type='application/json'
        )

    def bldresponse(self, response):
        resp = {
            'object_count': response['hits']['total'],
            'object_list': response['hits']['hits']
        }
        return resp
