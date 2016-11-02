import logging
import jsonpickle

from django.conf import settings

from . import models
from ..generic import index
from . import documents

log = logging.getLogger(__name__)

HR_DOC_TYPES = (
    documents.sbicodeMeta,
)


class DeleteHrIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_HR']
    doc_types = HR_DOC_TYPES


class IndexGenericTask(index.ImportIndexTask):
    name = "index generic data"
    queryset = models.Nummeraanduiding.objects. \
        prefetch_related('verblijfsobject').\
        prefetch_related('standplaats').\
        prefetch_related('ligplaats').\
        prefetch_related('openbare_ruimte')

    def convert(self, obj):
        return documents.meta_from_nummeraanduiding(obj)


class BuildIndexHrJob(object):
    name = "Create new search-index for all HR data from database"

    @staticmethod
    def tasks():
        return [
            DeleteHrIndexTask(),
            IndexHrTask(),
        ]


class DeleteIndexHrJob(object):
    name = "Delete HR related indexes"

    @staticmethod
    def tasks():
        return [DeleteHrIndexTask()]
