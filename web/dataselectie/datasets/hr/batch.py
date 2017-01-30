import logging

from django.conf import settings

from data import models, build_ds_data
from . import documents
from ..generic import index

log = logging.getLogger(__name__)

HR_DOC_TYPES = (
    documents.VestigingenMeta,
)


class IndexHrTask(index.ImportIndexTask):
    name = "index hr data"
    index = settings.ELASTIC_INDICES['DS_INDEX']

    queryset = models.DataSelectie.objects

    def convert(self, obj):
        return documents.meta_from_hrdataselectie(obj)


class ImportHrTask(index.ImportIndexTask):
    name = "import hr data"

    queryset = models.DataSelectie.objects

    def convert(self, obj):
        return build_ds_data._build_joined_ds_table()


class BuildIndexHrJob(object):
    name = "Create new search-index for all HR data from database"

    @staticmethod
    def tasks():
        return [IndexHrTask()]


class ImportHr(object):
    name = "Import HR data"

    @staticmethod
    def tasks():
        return [ImportHrTask()]
