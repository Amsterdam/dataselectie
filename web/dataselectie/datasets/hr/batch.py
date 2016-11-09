import logging
import jsonpickle

from django.conf import settings

from . import models
from ..generic import index
from . import documents

log = logging.getLogger(__name__)

HR_DOC_TYPES = (
    documents.HandelsregisterMeta,
)


class DeleteHrIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_HR']
    doc_types = HR_DOC_TYPES


class IndexGenericTask(index.ImportIndexTask):
    name = "index generic data"
    queryset = models.HandelsRegister.objects

    def convert(self, obj):
        return documents.meta_from_handelsregister(obj)


class BuildIndexDsHrJob(object):
    name = "Create new search-index for all HR data from database"

    @staticmethod
    def tasks():
        return [
            DeleteHrIndexTask(),
            IndexHrTask(), ''
        ]


class DeleteIndexHrJob(object):
    name = "Delete HR related indexes"

    @staticmethod
    def tasks():
        return [DeleteHrIndexTask()]

def indexElastic(Indexname, documenttypes, searchfields):
    pass