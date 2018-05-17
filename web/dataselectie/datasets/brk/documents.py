import logging
import json
import re

from django.conf import settings

import elasticsearch_dsl as es

log = logging.getLogger(__name__)


# Used in function _cleanup():
_RE_NEWLINES_AND_SPACES = re.compile(r'( *\r?\n)+ *')
_RE_MULTIPLE_SPACES = re.compile(r' {2,}')
_RE_TRIMMABLE_WS = re.compile(r'^\s+|\s+$')


def _cleanup(s: str):
    """Removes leading, trailing, and double whitespace."""
    s = _RE_NEWLINES_AND_SPACES.sub('\n', s)
    s = _RE_MULTIPLE_SPACES.sub(' ', s)
    s = _RE_TRIMMABLE_WS.sub('', s)
    return s


class Eigendom(es.DocType):
    class Meta:
        all = es.MetaField(enabled=False)
        doc_type = 'zakelijkrecht'
        index = settings.ELASTIC_INDICES['DS_BRK_INDEX']

    kot_kadastrale_aanduiding = es.Text()  # <-- generated
    kot_kadastrale_gemeentecode = es.Text()
    kot_sectie = es.Text()
    kot_perceelnummer = es.Text()
    kot_indexletter = es.Text()
    kot_indexnummer = es.Text()

    kot_kadastrale_gemeentenaam = es.Text()
    kot_koopsom = es.Float()
    kot_koopjaar = es.Integer()
    kot_grootte = es.Float()
    kot_cultuurcode_bebouwd_oms = es.Text()
    kot_cultuurcode_onbebouwd_oms = es.Text()

    eerste_adres = es.Text()  # <-- generated
    verblijfsobject_id = es.Text()
    verblijfsobject_openbare_ruimte_naam = es.Text()
    verblijfsobject_huisnummer = es.Integer()
    verblijfsobject_huisletter = es.Text()
    verblijfsobject_huisnummer_toevoeging = es.Text()
    verblijfsobject_postcode = es.Text()

    woonplaats = es.Text()

    kot_stadsdeel_naam = es.Text()
    kot_stadsdeel_code = es.Text()
    kot_ggw_naam = es.Text()
    kot_ggw_code = es.Text()
    kot_wijk_naam = es.Text()
    kot_wijk_code = es.Text()
    kot_buurt_naam = es.Text()
    kot_buurt_code = es.Text()
    geo_point = es.GeoPoint()
    geo_poly = es.GeoShape()

    zrt_aard_oms = es.Keyword()
    zrt_aandeel = es.Text()

    sjt_type = es.Keyword()
    sjt_naam = es.Text()  # <-- generated
    sjt_voornamen = es.Text()
    sjt_voorvoegsel_geslachtsnaam = es.Keyword()
    sjt_geslachtsnaam = es.Keyword()
    sjt_geslachtcode_oms = es.Keyword()
    sjt_kad_geboortedatum = es.Date()
    sjt_kad_geboorteplaats = es.Keyword()
    sjt_kad_geboorteland_code = es.Keyword()
    sjt_kad_datum_overlijden = es.Date()
    sjt_nnp_statutaire_naam = es.Keyword()
    sjt_nnp_statutaire_zetel = es.Keyword()
    sjt_nnp_statutaire_rechtsvorm_oms = es.Keyword()
    sjt_nnp_rsin = es.Keyword()
    sjt_nnp_kvknummer = es.Keyword()
    sjt_woonadres = es.Text()
    sjt_woonadres_buitenland = es.Text()
    sjt_postadres = es.Text()
    sjt_postadres_buitenland = es.Text()
    sjt_postadres_postbus = es.Text()

    def save(self, *args, **kwargs):
        """Fills a few dependant fields with data from other fields.

        -   kot_kadastrale_aanduiding
        -   sjt_naam
        -   eerste_adres

        """
        # noinspection PyTypeChecker
        self.kot_kadastrale_aanduiding = _cleanup(
            ' '.join(s for s in [
                self.kot_kadastrale_gemeentecode,
                self.kot_sectie,
                self.kot_perceelnummer,
                self.kot_indexletter,
                self.kot_indexnummer
            ] if s is not None)
        )
        # noinspection PyTypeChecker
        self.sjt_naam = _cleanup(
            ' '.join(s for s in [
                self.sjt_voornamen,
                self.sjt_voorvoegsel_geslachtsnaam,
                self.sjt_geslachtsnaam
            ] if s is not None)
        )
        adressen = []
        # noinspection PyTypeChecker
        for i in range(len(self.verblijfsobject_id)):
            adres = ' '.join(s for s in [
                self.verblijfsobject_openbare_ruimte_naam[i],
                self.verblijfsobject_huisnummer[i],
                self.verblijfsobject_huisletter[i],
                self.verblijfsobject_huisnummer_toevoeging[i]
            ] if s is not None)
            if self.verblijfsobject_postcode[i] is not None:
                adres += ', ' + self.verblijfsobject_postcode[i]
            adressen.append(_cleanup(adres))
        self.eerste_adres = sorted(adressen)[0] if len(adressen) else None
        return super().save(*args, **kwargs)


def doc_from_eigendom(eigendom):
    eigendommen = eigendom.kadastraal_object.eigendommen.all()

    doc = Eigendom()
    doc.kadastraal_object_id = eigendom.id
    if eigendom.kadastraal_object.point_geom:
        doc.geo_point = eigendom.kadastraal_object.point_geom.transform('wgs84', clone=True).coords
    if eigendom.kadastraal_object.poly_geom:
        multipolygon_wgs84 = eigendom.kadastraal_object.poly_geom.transform('wgs84', clone=True)
        # geoshape expects a dict with 'type' and 'coords'
        doc.geo_poly = json.loads(multipolygon_wgs84.geojson)
    doc.eigenaar_cat = [str(eigendom.eigenaar_categorie.id) for eigendom in eigendommen]
    doc.grondeigenaar = [eigendom.grondeigenaar for eigendom in eigendommen]
    doc.aanschrijfbaar = [eigendom.aanschrijfbaar for eigendom in eigendommen]
    doc.appartementeigenaar = [eigendom.appartementeigenaar for eigendom in eigendommen]

    doc.buurt = [str(buurt.id) for buurt in eigendom.kadastraal_object.buurten.all()]
    doc.wijk = [str(wijk.id) for wijk in eigendom.kadastraal_object.wijken.all()]
    doc.ggw = [str(ggw.id) for ggw in eigendom.kadastraal_object.ggws.all()]
    doc.stadsdeel = [str(stadsdeel.id) for stadsdeel in eigendom.kadastraal_object.stadsdelen.all()]

    return doc


# class KadastraalObject(es.DocType):
#     class Meta:
#         all = es.MetaField(enabled=False)
#         doc_type = 'kadastraalobject'
#         index = settings.ELASTIC_INDICES['DS_BRK_INDEX']
#
#     kadastraal_object_id = es.Keyword()
#     geo_point = es.GeoPoint()
#     geo_poly = es.GeoShape()
#     eigenaar_cat = es.Keyword(multi=True)
#     grondeigenaar = es.Boolean(multi=True)
#     aanschrijfbaar = es.Boolean(multi=True)
#     appartementeigenaar = es.Boolean(multi=True)
#
#     buurt = es.Keyword(multi=True)
#     wijk = es.Keyword(multi=True)
#     ggw = es.Keyword(multi=True)
#     stadsdeel = es.Keyword(multi=True)
#
#
# def doc_from_kadastraalobject(kadastraalobject):
#     eigendommen = kadastraalobject.eigendommen.all()
#
#     doc = KadastraalObject()
#     doc.kadastraal_object_id = kadastraalobject.id
#     if kadastraalobject.point_geom:
#         doc.geo_point = kadastraalobject.point_geom.transform('wgs84', clone=True).coords
#     if kadastraalobject.poly_geom:
#         multipolygon_wgs84 = kadastraalobject.poly_geom.transform('wgs84', clone=True)
#         # geoshape expects a dict with 'type' and 'coords'
#         doc.geo_poly = json.loads(multipolygon_wgs84.geojson)
#     doc.eigenaar_cat = [str(eigendom.eigenaar_categorie.id) for eigendom in eigendommen]
#     doc.grondeigenaar = [eigendom.grondeigenaar for eigendom in eigendommen]
#     doc.aanschrijfbaar = [eigendom.aanschrijfbaar for eigendom in eigendommen]
#     doc.appartementeigenaar = [eigendom.appartementeigenaar for eigendom in eigendommen]
#
#     doc.buurt = [str(buurt.id) for buurt in kadastraalobject.buurten.all()]
#     doc.wijk = [str(wijk.id) for wijk in kadastraalobject.wijken.all()]
#     doc.ggw = [str(ggw.id) for ggw in kadastraalobject.ggws.all()]
#     doc.stadsdeel = [str(stadsdeel.id) for stadsdeel in kadastraalobject.stadsdelen.all()]
#
#     return doc
#
