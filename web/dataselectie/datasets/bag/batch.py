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

    queryset = (
        models.Nummeraanduiding.objects
        .prefetch_related(
            # adresseerbaar_object returns:
            # ligplaats or self.standplaats or self.verblijfsobject
            'ligplaats',
            'ligplaats__buurt',
            'ligplaats__buurt__buurtcombinatie',
            'ligplaats__buurt__stadsdeel',
            'ligplaats___gebiedsgerichtwerken',
            'ligplaats___grootstedelijkgebied',
            'standplaats',
            'standplaats__buurt',
            'standplaats__buurt__buurtcombinatie',
            'standplaats__buurt__stadsdeel',
            'standplaats___gebiedsgerichtwerken',
            'standplaats___grootstedelijkgebied',
            'verblijfsobject',
            'verblijfsobject__buurt',
            'verblijfsobject__buurt__buurtcombinatie',
            'verblijfsobject__buurt__stadsdeel',
            'verblijfsobject__panden',
            'verblijfsobject__panden__bouwblok',
            'verblijfsobject___gebiedsgerichtwerken',
            'verblijfsobject___grootstedelijkgebied',
            'openbare_ruimte',
            'openbare_ruimte__woonplaats',
        )
    )

    def convert(self, obj):
        return documents.doc_from_nummeraanduiding(obj)


class BuildIndexDsBagJob(object):
    name = "Fill DS BAG search-index for database"

    @staticmethod
    def tasks():
        return [IndexDsBagTask()]
