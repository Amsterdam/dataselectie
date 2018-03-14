# Python
import logging

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

log = logging.getLogger(__name__)


def health(request):
    # check database
    message = 'OK'
    status = 200

    # check elasticsearch
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert client.info()
    except:
        log.exception("Elasticsearch connectivity failed")
        message += "\nElasticsearch connectivity failed."
        status = 500
        return HttpResponse(message, content_type='text/plain', status=status)

    # return HttpResponse(message, content_type='text/plain', status=status)
    return check_data(request)


def check_data(request):
    # check bag / hr documents in elastic
    message = ''
    status = 200

    # check elastic
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        keys = [key for key in settings.ELASTIC_INDICES.keys() if key != 'DS_BRK_INDEX']
        for index in keys:
            # check that we have some documents in index.
            es_index = settings.ELASTIC_INDICES[index]
            count = (
                Search()
                .using(client)
                .index(es_index)
                .query("match_all").count())
            log.debug('%s -  %s', es_index, count)
            assert count

    except:
        message += "Elastic data missing."
        log.exception(message)
        status = 500

    if not message:
        message = "Data OK"

    return HttpResponse(message, content_type='text/plain', status=status)
