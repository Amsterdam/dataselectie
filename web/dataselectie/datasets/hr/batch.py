import logging

from django.conf import settings

from datasets.bag import models as bag_models
from datasets.hr import models

from . import documents
from ..generic import index

log = logging.getLogger(__name__)


HR_DOC_TYPES = (
    documents.Inschrijving,
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

    #db = settings.HR_DATABASE

    queryset = (
        models.DataSelectie.objects
        .filter(nummeraanduiding__isnull=False)
        .prefetch_related(
            'nummeraanduiding',
            *bag_models.prefetch_adresseerbaar_objects('nummeraanduiding'),
        )
        .order_by('id')
    )

    def convert(self, obj: models.DataSelectie) -> documents.Inschrijving:
        vestiging = obj
        try:
            bag_obj = vestiging.nummeraanduiding
        except bag_models.Nummeraanduiding.DoesNotExist:
            # This can still happen as there is no DB constraint here.
            bag_obj = None
        return documents.inschrijving_from_hrdataselectie(vestiging, bag_obj)


class BuildIndexHrJob(object):
    name = "Fill HR search-index for all HR data from database"

    @staticmethod
    def tasks():
        return [IndexHrTask()]
