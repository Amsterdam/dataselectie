import logging

from django.conf import settings

from datasets.brk import models

from . import documents
from ..generic import index

log = logging.getLogger(__name__)

BRK_DOC_TYPES = (
    documents.KadastraalObject,
)


class DeleteDsBRKIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_BRK_INDEX']
    doc_types = BRK_DOC_TYPES


class RebuildDocTaskBRK(index.CreateDocTypeTask):
    index = settings.ELASTIC_INDICES['DS_BRK_INDEX']
    doc_types = BRK_DOC_TYPES


class ReBuildIndexDsBRKJob(object):
    name = "Recreate search-index for all BRK data from elastic"

    @staticmethod
    def tasks():
        return [
            DeleteDsBRKIndexTask(),
            RebuildDocTaskBRK()
        ]


class DeleteIndexDsBRKJob(object):
    name = "Delete BRK related indexes"

    @staticmethod
    def tasks():
        return [DeleteDsBRKIndexTask()]


class IndexBrkTask(index.ImportIndexTask):
    name = "index brk data"
    sequential = True
    index = settings.ELASTIC_INDICES['DS_BRK_INDEX']

    queryset = models.KadastraalObject.objects.prefetch_related('eigendommen') \
                     .filter(id__in=models.Eigendom.objects.values_list('kadastraal_object_id', flat=True)) \
                     .order_by('id')

    def convert(self, obj):
        return documents.doc_from_kadastraalobject(obj)


class BuildIndexBRKJob(object):
    name = "Fill BRK search-index for all BRK data from database"

    @staticmethod
    def tasks():
        return [IndexBrkTask()]
