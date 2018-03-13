import logging

from django.conf import settings

from datasets.bag import models as bag_models
from datasets.brk import models

from . import documents
from ..generic import index

log = logging.getLogger(__name__)

BRK_DOC_TYPES = (
    documents.KadastraalObject,
)


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


class DeleteDsBRKIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_BRK_INDEX']
    doc_types = BRK_DOC_TYPES


class IndexBrkTask(index.ImportIndexTask):
    name = "index brk data"
    index = settings.ELASTIC_INDICES['DS_BRK_INDEX']

    queryset = models.KadastraalObject.objects.filter.order_by('id')

    def convert(self, obj):
        kadastraalobject = obj
        try:
            bag_obj = bag_models.Nummeraanduiding.objects.get(
                landelijk_id=vestiging.bag_numid)
        except bag_models.Nummeraanduiding.DoesNotExist:
            bag_obj = None
        return documents.KadastraalObject(

        )


class BuildIndexBRKJob(object):
    name = "Fill BRK search-index for all BRK data from database"

    @staticmethod
    def tasks():
        return [IndexBrkTask()]
