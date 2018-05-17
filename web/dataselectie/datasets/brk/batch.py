import logging

from django.conf import settings

from datasets.brk import models

from . import documents
from ..generic import index

log = logging.getLogger(__name__)

BRK_DOC_TYPES = (
    documents.Eigendom,
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

    queryset = (
        models.Eigendom.objects
        .prefetch_related('kadastraal_object')
        .prefetch_related('kadastraal_object__buurten')
        .prefetch_related('kadastraal_object__wijken')
        .prefetch_related('kadastraal_object__ggws')
        .prefetch_related('kadastraal_object__stadsdelen')
        .prefetch_related('kadastraal_object__verblijfsobjecten')
        .prefetch_related('kadastraal_object__verblijfsobjecten__adressen')
        .prefetch_related('kadastraal_subject')
        .prefetch_related('kadastraal_subject__postadres')
        .prefetch_related('kadastraal_subject__woonadres')
        .order_by('zakelijk_recht')
    )

    def convert(self, obj):
        return documents.doc_from_eigendom(obj)

    def get_queryset(self):
        return self.queryset.order_by('zakelijk_recht')

    # queryset = models.KadastraalObject.objects \
    #     .prefetch_related('eigendommen') \
    #     .prefetch_related('buurten') \
    #     .prefetch_related('wijken') \
    #     .prefetch_related('ggws') \
    #     .prefetch_related('stadsdelen') \
    #     .filter(id__in=models.Eigendom.objects.values_list('kadastraal_object_id', flat=True)) \
    #     .order_by('id')
    #
    # def convert(self, obj):
    #     return documents.doc_from_zakelijkrecht(obj)


class BuildIndexBRKJob(object):
    name = "Fill BRK search-index for all BRK data from database"

    @staticmethod
    def tasks():
        return [IndexBrkTask()]
