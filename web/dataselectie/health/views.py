# Python
import logging

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from datasets.bag.models import Nummeraanduiding
from datasets.hr.models import DataSelectie

log = logging.getLogger(__name__)


def health(request):
    # check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert cursor.fetchone()
    except:
        log.exception("Database connectivity failed")
        return HttpResponse("Database connectivity failed.",
                            content_type='text/plain',
                            status=500)

    # check elasticsearch
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert client.info()
    except:
        log.exception("Elasticsearch connectivity failed")
        return HttpResponse("Elasticsearch connectivity failed.",
                            content_type='text/plain',
                            status=500)

    # check debug
    if settings.DEBUG:
        log.exception("Debug mode not allowed in production")
        return HttpResponse(
            "Debug mode not allowed in production",
            content_type="text/plain", status=500)

    return HttpResponse("Health OK", content_type='text/plain', status=200)


def check_data(request):
    # check bag / hr

    status, message = checknrs(Nummeraanduiding.objects.count(), settings.MIN_BAG_NR, "BAG")
    if status == 200:
        status, message = checknrs(DataSelectie.objects.count(), settings.MIN_HR_NR, "DataselectieHR")

        if status == 200:
            # check elastic
            try:
                client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
                assert Search().using(client)\
                               .index(settings.ELASTIC_INDICES['DS_BAG'])\
                               .query("match_all", size=0)
            except:
                log.exception("Autocomplete failed")
                message += "\nAutocomplete failed."
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
