import logging

from django.conf import settings

from ..bag import models as bagmodels
from ..hr import models as hrmodels
from ..generic import index
from ..bag import documents as bagdocuments
from ..hr import documents as hrdocuments

log = logging.getLogger(__name__)

DOC_TYPES = (
    bagdocuments.NummeraanduidingMeta,
    hrdocuments.VestigingenMeta
)


class DeleteDsIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['DS_BAG']
    doc_types = DOC_TYPES


class IndexDsTask(index.ImportIndexTask):
    name = "index bag data"
    index = settings.ELASTIC_INDICES['DS_BAG']

    queryset = bagmodels.Nummeraanduiding.objects.\
        prefetch_related('verblijfsobject').\
        prefetch_related('standplaats').\
        prefetch_related('ligplaats').\
        prefetch_related('openbare_ruimte')

    def convert_bag(self, obj):
        return bagdocuments.meta_from_nummeraanduiding(obj)

    def convert_hr(self, obj):
        return hrdocuments.meta_from_hrdataselectie(obj)


class BuildIndexDsJob(object):
    name = "Create new search-index for all BAG and HR data from database"

    @staticmethod
    def tasks():
        return [IndexDsTask()]


class DeleteIndexDsBagJob(object):
    name = "Delete BAG related indexes"

    @staticmethod
    def tasks():
        return [DeleteDsIndexTask()]
