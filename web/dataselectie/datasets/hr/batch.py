import logging

from django.conf import settings

from datasets.bag import models as bag_models
from datasets.hr import models

from . import documents
from ..generic import index

log = logging.getLogger(__name__)


HR_DOC_TYPES = (
    documents.Vestiging,
)


class RebuildDocTaskHR(index.CreateDocTypeTask):
    index = settings.ELASTIC_INDICES['DS_HR_INDEX']
    doc_types = HR_DOC_TYPES


class ReBuildIndexDsHRJob(object):
    name = "Recreate search-index for all HR data from elastic"

    @staticmethod
    def tasks():
        return [
            DeleteDsHRIndexTask(),
            RebuildDocTaskHR()
        ]


class DeleteIndexDsHRJob(object):
    name = "Delete HR related indexes"

    @staticmethod
    def tasks():
        return [DeleteDsHRIndexTask()]


class DeleteDsHRIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_HR_INDEX']
    doc_types = HR_DOC_TYPES


class IndexHrTask(index.ImportIndexTask):
    name = "index hr data"
    index = settings.ELASTIC_INDICES['DS_HR_INDEX']

    queryset = models.DataSelectie.objects.filter(
        bag_numid__isnull=False).order_by('id')

    def convert(self, obj):
        vestiging = obj
        try:
            bag_obj = bag_models.Nummeraanduiding.objects.get(
                landelijk_id=vestiging.bag_numid)
        except bag_models.Nummeraanduiding.DoesNotExist:
            bag_obj = None
        return documents.vestiging_from_hrdataselectie(vestiging, bag_obj)


class BuildIndexHrJob(object):
    name = "Create new search-index for all HR data from database"

    @staticmethod
    def tasks():
        return [IndexHrTask()]
