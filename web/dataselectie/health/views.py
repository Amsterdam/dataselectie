# Python
import logging

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

log = logging.getLogger(__name__)


def health(_request):
    # check database
    message = ''
    status = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert cursor.fetchone()
    except:
        log.exception("Database connectivity failed")
        message += "\nDatabase connectivity failed."
        status = 500
        return HttpResponse(message, content_type='text/plain', status=status)

    # check elasticsearch
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert client.info()
    except:
        log.exception("Elasticsearch connectivity failed")
        message += "\nElasticsearch connectivity failed."
        status = 500
        return HttpResponse(message, content_type='text/plain', status=status)

    if not message:
        message = "Connectivity OK"

    return HttpResponse(message, content_type='text/plain', status=status)


def check_data(request):
    # check bag / hr
    message = None
    status = 200

    # check elastic
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        for index in settings.ELASTIC_INDICES.keys():
            assert (
                Search()
                .using(client)
                .index(settings.ELASTIC_INDICES[index])
                .query("match_all", size=0)
            )
    except:
        message += "\nElastic data missing."
        log.exception(message)
        status = 500

    if not message:
        message = "Data Ok"

    return HttpResponse(message, content_type='text/plain', status=status)


def checknrs(obj_count: int, min_required: int, dataset: str) -> (int, str):
    message = ''
    status = 200
    if obj_count < min_required:
        msg = "Database connects, but {} has too few rows".format(dataset)
        log.exception(msg)
        message += "\n" + msg
        status = 500
    return status, message
