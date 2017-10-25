import logging

from django.conf import settings

from . import models
from ..generic import index
from . import documents

log = logging.getLogger(__name__)

BAG_DOC_TYPES = (
    documents.Nummeraanduiding,
)


class DeleteDsBAGIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_BAG_INDEX']
    doc_types = BAG_DOC_TYPES


class RebuildDocTaskBAG(index.CreateDocTypeTask):
    index = settings.ELASTIC_INDICES['DS_BAG_INDEX']
    doc_types = BAG_DOC_TYPES


class ReBuildIndexDsBAGJob(object):
    name = "Recreate search-index for all BAG data from elastic"

    @staticmethod
    def tasks():
        return [
            DeleteDsBAGIndexTask(),
            RebuildDocTaskBAG()
        ]


class DeleteIndexDsBAGJob(object):
    name = "Delete BAG related indexes"

    @staticmethod
    def tasks():
        return [DeleteDsBAGIndexTask()]


class IndexDsBagTask(index.ImportIndexTask):
    name = "index bag data"
    index = settings.ELASTIC_INDICES['DS_BAG_INDEX']

    queryset = models.Nummeraanduiding.objects.\
        prefetch_related('verblijfsobject').\
        prefetch_related('standplaats').\
        prefetch_related('ligplaats').\
        prefetch_related('openbare_ruimte')

    def convert(self, obj):
        return documents.doc_from_nummeraanduiding(obj)


class BuildIndexDsBagJob(object):
    name = "Fill DS BAG search-index for database"

    @staticmethod
    def tasks():
        return [IndexDsBagTask()]
