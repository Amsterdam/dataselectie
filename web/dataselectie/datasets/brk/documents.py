import logging
import json

from django.conf import settings

import elasticsearch_dsl as es

log = logging.getLogger(__name__)


class KadastraalObject(es.DocType):
    class Meta:
        all = es.MetaField(enabled=False)
        doc_type = 'kadastraalobject'
        index = settings.ELASTIC_INDICES['DS_BRK_INDEX']

    kadastraal_object_id = es.Keyword()
    geo_point = es.GeoPoint()
    geo_poly = es.GeoShape()
    eigenaar_cat = es.Keyword(multi=True)
    grondeigenaar = es.Boolean(multi=True)
    aanschrijfbaar = es.Boolean(multi=True)
    appartementeigenaar = es.Boolean(multi=True)

    buurt = es.Keyword(multi=True)
    wijk = es.Keyword(multi=True)
    ggw = es.Keyword(multi=True)
    stadsdeel = es.Keyword(multi=True)


def doc_from_kadastraalobject(kadastraalobject):
    eigendommen = kadastraalobject.eigendommen.all()

    doc = KadastraalObject()
    doc.kadastraal_object_id = kadastraalobject.id
    if kadastraalobject.point_geom:
        doc.geo_point = kadastraalobject.point_geom.transform('wgs84', clone=True).coords
    if kadastraalobject.poly_geom:
        multipolygon_wgs84 = kadastraalobject.poly_geom.transform('wgs84', clone=True)
        # geoshape expects a dict with 'type' and 'coords'
        doc.geo_poly = json.loads(multipolygon_wgs84.geojson)
    doc.eigenaar_cat = [str(eigendom.eigenaar_categorie.id) for eigendom in eigendommen]
    doc.grondeigenaar = [eigendom.grondeigenaar for eigendom in eigendommen]
    doc.aanschrijfbaar = [eigendom.aanschrijfbaar for eigendom in eigendommen]
    doc.appartementeigenaar = [eigendom.appartementeigenaar for eigendom in eigendommen]

    doc.buurt = [str(buurt.id) for buurt in kadastraalobject.buurten.all()]
    doc.wijk = [str(wijk.id) for wijk in kadastraalobject.wijken.all()]
    doc.ggw = [str(ggw.id) for ggw in kadastraalobject.ggws.all()]
    doc.stadsdeel = [str(stadsdeel.id) for stadsdeel in kadastraalobject.stadsdelen.all()]

    return doc