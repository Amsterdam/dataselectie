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


class IndexHrTask(index.ImportIndexTask):
    name = "index hr data"
    index = settings.ELASTIC_INDICES['DS_INDEX']

    queryset = models.DataSelectie.objects.filter(bag_numid__isnull=False).order_by('id')

    def convert(self, obj):
        # @TODO this can be switched to use the elasitc index to retrieve the data
        # This will create a better contained unit
        try:
            bag_obj = bag_models.Nummeraanduiding.objects.get(landelijk_id=obj.bag_numid)
        except bag_models.Nummeraanduiding.DoesNotExist:
            bag_obj = None
        return documents.vestiging_from_hrdataselectie(obj, bag_obj)


class BuildIndexHrJob(object):
    name = "Create new search-index for all HR data from database"

    @staticmethod
    def tasks():
        return [IndexHrTask()]
