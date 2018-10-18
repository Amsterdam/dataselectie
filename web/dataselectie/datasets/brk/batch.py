import logging

from django.conf import settings
from django.db.models import Q

from dataselectie import utils
from datasets.brk import models

from . import documents
from ..generic import index

log = logging.getLogger(__name__)

# When examining Postgres query performance the following logs queries and runtime
# l = logging.getLogger('django.db.backends')
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())

BRK_DOC_TYPES = (
    documents.Eigendom,
)


class DeleteDsBRKIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_BRK_INDEX']
    doc_types = BRK_DOC_TYPES


class RebuildDocTaskBRK(index.CreateDocTypeTask):
    index = settings.ELASTIC_INDICES['DS_BRK_INDEX']
    doc_types = BRK_DOC_TYPES

class FlushRedisDbTask():
    def __init__(self):
        pass

    def execute(self):
        redis = utils.get_redis()
        if redis:
            redis.flushall()
            log.info("Flushing redis")
        else:
            log.warning("Redis not available for flushing")


class ReBuildIndexDsBRKJob(object):
    name = "Recreate search-index for all BRK data from elastic"

    @staticmethod
    def tasks():
        return [
            DeleteDsBRKIndexTask(),
            RebuildDocTaskBRK(),
            FlushRedisDbTask(),
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
        .prefetch_related('zakelijk_recht')
        .prefetch_related('zakelijk_recht__aard_zakelijk_recht')
        .prefetch_related('kadastraal_object')
        .prefetch_related('kadastraal_object__kadastrale_gemeente')
        .prefetch_related('kadastraal_object__buurten')
        .prefetch_related('kadastraal_object__wijken')
        .prefetch_related('kadastraal_object__ggws')
        .prefetch_related('kadastraal_object__sectie')
        .prefetch_related('kadastraal_object__stadsdelen')
        .prefetch_related('kadastraal_object__verblijfsobjecten')
        .prefetch_related('kadastraal_object__verblijfsobjecten__adressen')
        .prefetch_related('kadastraal_object__appartementsplot')
        .prefetch_related('kadastraal_subject')
        .prefetch_related('kadastraal_subject__postadres')
        .prefetch_related('kadastraal_subject__woonadres')

        # Order by kadastraal_object_id because we keep track of kadastraal_objects_oid to count them
        # Therefore we do not want to minimize to have the same kadastraal_object_id in different
        # batches
        .order_by('zakelijk_recht__id')
    )

    def convert(self, obj):
        return documents.doc_from_eigendom(obj)

    def get_queryset(self):
        return self.queryset.order_by('zakelijk_recht__id')


class BuildIndexBRKJob(object):
    name = "Fill BRK search-index for all BRK data from database"

    @staticmethod
    def tasks():
        return [IndexBrkTask()]
