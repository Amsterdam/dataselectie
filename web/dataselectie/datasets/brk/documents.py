import logging

import elasticsearch_dsl as es
from django.conf import settings

log = logging.getLogger(__name__)


class KadastraalObject(es.Document):
    class Meta:
        all = es.MetaField(enabled=False)
        doc_type = 'kadastraalobject'
        index = settings.ELASTIC_INDICES['DS_BRK_INDEX']

    kadastraal_object_id = es.Keyword()
    geo_point = es.GeoPoint()
    geo_poly = es.GeoShape()

    def from_kadastraal_object(self):