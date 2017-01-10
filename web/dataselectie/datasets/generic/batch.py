import logging

from django.conf import settings

from ..generic import index
from ..bag import documents as bagdocuments
from ..hr import documents as hrdocuments

log = logging.getLogger(__name__)

DOC_TYPES = (
    bagdocuments.NummeraanduidingMeta,
    hrdocuments.VestigingenMeta
)


class DeleteDsIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_INDEX']
    doc_types = DOC_TYPES


class RebuildDocTask(index.CreateDocTypeTask):
    index = settings.ELASTIC_INDICES['DS_INDEX']
    doc_types = DOC_TYPES


class ReBuildIndexDsJob(object):
    name = "Recreate search-index for all BAG and HR data from database"

    @staticmethod
    def tasks():
        return [DeleteDsIndexTask(), RebuildDocTask()]


class DeleteIndexDsBagJob(object):
    name = "Delete BAG related indexes"

    @staticmethod
    def tasks():
        return [DeleteDsIndexTask()]
