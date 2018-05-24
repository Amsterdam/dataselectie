import logging
import json
import re

from django.conf import settings
from django.utils.dateparse import parse_date
from datasets.brk import models as brk_models

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

    eigendom_id = es.Keyword()
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

    kot_stadsdeel_naam = es.Text(multi=True)
    kot_stadsdeel_code = es.Text(multi=True)
    kot_ggw_naam = es.Text(multi=True)
    kot_ggw_code = es.Text(multi=True)
    kot_wijk_naam = es.Text(multi=True)
    kot_wijk_code = es.Text(multi=True)
    kot_buurt_naam = es.Text(multi=True)
    kot_buurt_code = es.Text(multi=True)
    geo_point = es.GeoPoint()
    geo_poly = es.GeoShape()

    zrt_aardzakelijkrecht_oms = es.Keyword()
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


lookup_tables = {}


def get_omschrijving(clazz, code):
    if code is None:
        return None
    global lookup_tables
    class_name = clazz.__name__
    if class_name not in lookup_tables:
        lookup_tables[class_name] = {}
        elements = clazz.objects.all()
        for e in elements:
            lookup_tables[class_name][e.code] = e.omschrijving
    return lookup_tables[class_name].get(code)

def get_date(val):
    if val is None or val == '':
        result = None
    else:
        try:
            result = parse_date(val)
        except ValueError:
            result = None
    return result


def doc_from_eigendom(eigendom: object):
    kot = eigendom.kadastraal_object
    # eigendommen = kot.eigendommen.all()

    doc = Eigendom(_id=eigendom.id)
    doc.eigendom_id = eigendom.id
    # kot_kadastrale_aanduiding = es.Text()  # <-- generated
    doc.kot_kadastrale_gemeentecode = kot.kadastrale_gemeente_id
    doc.kot_sectie = kot.sectie_id
    doc.kot_perceelnummer = kot.perceelnummer
    doc.kot_indexletter = kot.indexletter
    doc.kot_indexnummer = kot.indexnummer

    doc.kot_kadastrale_gemeentenaam = kot.kadastrale_gemeente.naam

    doc.kot_koopsom = kot.koopsom
    doc.kot_koopjaar = kot.koopjaar
    doc.kot_grootte = kot.grootte

    doc.kot_cultuurcode_bebouwd_oms = kot.cultuurcode_bebouwd_id
    doc.kot_cultuurcode_onbebouwd_oms = kot.cultuurcode_onbebouwd_id

    vbo_list = kot.verblijfsobjecten.all()  # This is already ordered

    # eerste_adres = es.Text()  # <-- generated
    if vbo_list:
        vbo = vbo_list[0]
        doc.verblijfsobject_id =  vbo.landelijk_id
        doc.verblijfsobject_openbare_ruimte_naam = vbo._openbare_ruimte_naam
        doc.verblijfsobject_huisnummer = vbo._huisnummer
        doc.verblijfsobject_huisletter = vbo._huisletter
        doc.verblijfsobject_huisnummer_toevoeging = vbo._huisnummer_toevoeging
        hoofdadres = vbo.hoofdadres
        doc.verblijfsobject_postcode = hoofdadres.postcode
        doc.woonplaats = str(hoofdadres.woonplaats)

    stadsdelen = kot.stadsdelen.all()
    if stadsdelen:
        doc.kot_stadsdeel_naam = [stadsdeel.naam for stadsdeel in stadsdelen]
        doc.kot_stadsdeel_code = [stadsdeel.code for stadsdeel in stadsdelen]
    ggws = kot.ggws.all()
    if ggws:
        doc.kot_ggw_code = [ggw.code for ggw in ggws]
        doc.kot_ggw_naam = [ggw.naam for ggw in ggws]
    wijken = kot.wijken.all()
    if wijken:
        doc.kot_wijk_naam = [wijk.naam for wijk in wijken]
        doc.kot_wijk_code = [wijk.code for wijk in wijken]
    buurten = kot.buurten.all()
    if buurten:
        doc.kot_buurt_naam = [buurt.naam for buurt in buurten]
        doc.kot_buurt_code = [buurt.code for buurt in buurten]

    if kot.point_geom:
        doc.geo_point = kot.point_geom.transform('wgs84', clone=True).coords
    if kot.poly_geom:
        multipolygon_wgs84 = kot.poly_geom.transform('wgs84', clone=True)
        # geoshape expects a dict with 'type' and 'coords'
        doc.geo_poly = json.loads(multipolygon_wgs84.geojson)

    zrt = eigendom.zakelijk_recht
    if zrt:
        doc.zrt_aardzakelijkrecht_oms = get_omschrijving(brk_models.AardZakelijkRecht, zrt.aard_zakelijk_recht_id)
        doc.zrt_aandeel = f"{zrt.teller}/{zrt.noemer}"

    kst = eigendom.kadastraal_subject
    if kst:
        doc.sjt_type = kst.type
        # doc.sjt_naam = es.Text()  # <-- generated
        doc.sjt_voornamen = kst.voornamen
        doc.sjt_voorvoegsel_geslachtsnaam = kst.voorvoegsels
        doc.sjt_geslachtsnaam = kst.naam
        doc.sjt_geslachtcode_oms = get_omschrijving(brk_models.Geslacht, kst.geslacht_id)
        doc.sjt_kad_geboortedatum = get_date(kst.geboortedatum)
        doc.sjt_kad_geboorteplaats = kst.geboorteplaats
        doc.sjt_kad_geboorteland_code = kst.geboorteland_id
        doc.sjt_kad_datum_overlijden = get_date(kst.overlijdensdatum)
        doc.sjt_nnp_statutaire_naam = kst.statutaire_naam
        doc.sjt_nnp_statutaire_zetel = kst.statutaire_zetel
        doc.sjt_nnp_statutaire_rechtsvorm_oms = get_omschrijving(brk_models.Rechtsvorm, kst.rechtsvorm_id)
        doc.sjt_nnp_rsin = kst.rsin
        doc.sjt_nnp_kvknummer = kst.kvknummer
        woonadres = kst.woonadres
        if woonadres:
            doc.sjt_woonadres = woonadres.volledig_adres()
            doc.sjt_woonadres_buitenland = woonadres.volledig_buitenland_adres()
        postadres = kst.postadres
        if postadres:
            doc.sjt_postadres = postadres.volledig_adres()
            doc.sjt_postadres_buitenland = postadres.volledig_buitenland_adres()
            doc.sjt_postadres_postbus = postadres.postbus_adres()

    # doc.kadastraal_object_id = eigendom.id
    # doc.eigenaar_cat = [str(eigendom.eigenaar_categorie_id) for eigendom in eigendommen]
    # doc.grondeigenaar = [eigendom.grondeigenaar for eigendom in eigendommen]
    # doc.aanschrijfbaar = [eigendom.aanschrijfbaar for eigendom in eigendommen]
    # doc.appartementeigenaar = [eigendom.appartementeigenaar for eigendom in eigendommen]


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
