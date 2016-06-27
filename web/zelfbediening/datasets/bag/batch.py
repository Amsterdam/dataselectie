# Python
# import datetime
# import json
import logging
import os
# Packages
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import connection
from django.utils.text import slugify
# import requests
# Project
from batch import batch
from datasets.generic import index
from . import models, documents

log = logging.getLogger(__name__)


BAG_DOC_TYPES = (
    documents.NummeraanduidingMeta,
)


class DeleteBagIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['ZB_BAG']
    doc_types = BAG_DOC_TYPES


class IndexBagTask(index.ImportIndexTask):
    name = "index bag data"
    queryset = models.Nummeraanduiding.objects.\
        prefetch_related('verblijfsobject').\
        prefetch_related('standplaats').\
        prefetch_related('ligplaats').\
        prefetch_related('openbare_ruimte')

    def convert(self, obj):
        return documents.meta_from_nummeraanduiding(obj)


class BuildIndexBagJob(object):
    name = "Create new search-index for all BAG data from database"

    def tasks(self):
        return [
            DeleteBagIndexTask(),
            IndexBagTask(),
        ]


class DeleteIndexBagJob(object):

    name = "Delete BAG related indexes"

    def tasks(self):
        return [
            DeleteBagIndexTask(),
        ]


