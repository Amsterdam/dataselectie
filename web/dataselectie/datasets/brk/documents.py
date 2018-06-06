import logging
import re
import redis

from collections import Counter

from django.conf import settings
from django.utils.dateparse import parse_date

from dataselectie import utils
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
        # all = es.MetaField(enabled=False)
        doc_type = 'eigendom'
        index = settings.ELASTIC_INDICES['DS_BRK_INDEX']

    kadastraal_object_id = es.Keyword()
    kadastraal_object_index = es.Short()
    eigenaar_cat_id = es.Integer()
    eigenaar_cat = es.Keyword()
    grondeigenaar = es.Boolean()
    aanschrijfbaar = es.Boolean()
    appartementeigenaar = es.Boolean()
    aard_zakelijk_recht_akr = es.Keyword()

    eigendom_id = es.Keyword()
    aanduiding = es.Keyword()  # <-- generated
    kadastrale_gemeentecode = es.Keyword()
    sectie = es.Keyword()
    perceelnummer = es.Keyword()
    indexletter = es.Keyword()
    indexnummer = es.Keyword()

    kadastrale_gemeentenaam = es.Keyword()
    koopsom = es.Float()
    koopjaar = es.Integer()
    grootte = es.Float()
    cultuurcode_bebouwd = es.Keyword()
    cultuurcode_onbebouwd = es.Keyword()

    adressen = es.Keyword(multi=True)
    verblijfsobject_id = es.Keyword(multi=True)
    openbare_ruimte_naam = es.Keyword(multi=True)
    huisnummer = es.Integer(multi=True)
    huisletter = es.Keyword(multi=True)
    huisnummer_toevoeging = es.Keyword(multi=True)
    postcode = es.Keyword(multi=True)
    woonplaats = es.Keyword(multi=True)
    eerste_adres = es.Keyword()

    stadsdeel_naam = es.Keyword(multi=True)
    stadsdeel_code = es.Keyword(multi=True)
    ggw_naam = es.Keyword(multi=True)
    ggw_code = es.Keyword(multi=True)
    wijk_naam = es.Keyword(multi=True)
    wijk_code = es.Keyword(multi=True)
    buurt_naam = es.Keyword(multi=True)
    buurt_code = es.Keyword(multi=True)
    geometrie_rd = es.Keyword(index=False, ignore_above=256)
    geometrie_wgs84 = es.Keyword(index=False, ignore_above=256)
    centroid = es.GeoPoint()  # centroid is required for shape search. Which items are inside the shape ?

    aard_zakelijk_recht = es.Keyword()
    zakelijk_recht_aandeel = es.Keyword()

    sjt_id = es.Keyword()
    sjt_type = es.Keyword()
    sjt_is_natuurlijk_persoon = es.Boolean()
    sjt_voornamen = es.Keyword()
    sjt_voorvoegsels = es.Keyword()
    sjt_geslachtsnaam = es.Keyword()
    sjt_naam = es.Keyword()
    sjt_geslacht_oms = es.Keyword()
    sjt_geboortedatum = es.Date()
    sjt_geboorteplaats = es.Keyword()
    sjt_geboorteland_code = es.Keyword()
    sjt_datum_overlijden = es.Date()
    sjt_statutaire_naam = es.Keyword()
    sjt_statutaire_zetel = es.Keyword()
    sjt_statutaire_rechtsvorm = es.Keyword()
    sjt_rsin = es.Keyword()
    sjt_kvknummer = es.Keyword()
    sjt_woonadres = es.Keyword()
    sjt_woonadres_buitenland = es.Keyword()
    sjt_postadres = es.Keyword()
    sjt_postadres_buitenland = es.Keyword()
    sjt_postadres_postbus = es.Keyword()

    # def save(self, *args, **kwargs):
    #     """Fills a few dependant fields with data from other fields.
    #
    #     -   kot_kadastrale_aanduiding
    #     -   sjt_naam
    #     -   eerste_adres
    #
    #     """
    #     # noinspection PyTypeChecker
    #     self.aanduiding = _cleanup(
    #         ' '.join(s for s in [
    #             self.kadastrale_gemeentecode,
    #             self.sectie,
    #             self.perceelnummer,
    #             self.indexletter,
    #             self.indexnummer
    #         ] if s is not None)
    #     )
    #     # noinspection PyTypeChecker
    #     # self.kadastraal_subject.append({
    #     #      'naam' : _cleanup(
    #     #         ' '.join(s for s in [
    #     #             self.kadastraal_subject.voornamen,
    #     #             self.kadastraal_subject.voorvoegsel_geslachtsnaam,
    #     #             self.kadastraal_subject.geslachtsnaam
    #     #         ] if s is not None) )
    #     # })
    #     adressen = []
    #     # noinspection PyTypeChecker
    #     for i in range(len(self.verblijfsobject_id)):
    #         adres = ' '.join(s for s in [
    #             self.verblijfsobject_openbare_ruimte_naam[i],
    #             self.verblijfsobject_huisnummer[i],
    #             self.verblijfsobject_huisletter[i],
    #             self.verblijfsobject_huisnummer_toevoeging[i]
    #         ] if s is not None)
    #         if self.verblijfsobject_postcode[i] is not None:
    #             adres += ', ' + self.verblijfsobject_postcode[i]
    #         adressen.append(_cleanup(adres))
    #     self.eerste_adres = sorted(adressen)[0] if len(adressen) else None
    #     return super().save(*args, **kwargs)


lookup_tables = {}


def get_omschrijving(clazz, code, code_field='code', omschrijving_field='omschrijving'):
    if code is None:
        return None
    global lookup_tables
    class_name = clazz.__name__
    if class_name not in lookup_tables:
        lookup_tables[class_name] = {}
        elements = clazz.objects.all()
        for e in elements:
            lookup_tables[class_name][getattr(e, code_field)] = getattr(e, omschrijving_field)
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


# For the 'lijst'  view we only need to see the  kadastrale object. Because there can be multiple
# Eigendommen for one kadastraal_object we keep a counter for kadastrale objecten. In that way
# we can select the first kadastrale_object by having additional constraint : kadastraal_object_index == 0
# To create we keep a Counter dictionary for each kadastraal_object.  This does not work correctly if
# create the indexes in batches, because then we create a new empty Counter dictionary for each batch.
# In order to account for this in the original query we order by kadastraal_object_id.
# Then it could still be that on the end of one batch and beginning of another batch
# there are duplicate kadastrale objects. But that will be very rare.
kadastraal_object_index = Counter()
redis_db = None
use_redis = None


def get_kadastraal_object_index(key):
    global use_redis
    global redis_db
    if use_redis is None:
        redis_db = utils.get_redis()
        if redis_db is None:
            use_redis = False
            log.warning("Redis is not available. Use local check for kadastraal_object_seen")
        else:
            use_redis = True
    if use_redis:
        result = redis_db.incr(key) - 1  # start with 0
    else:
        result = kadastraal_object_index[key]
        kadastraal_object_index[key] += 1
    return result


def doc_from_eigendom(eigendom: object) -> Eigendom:
    kot = eigendom.kadastraal_object
    # eigendommen = kot.eigendommen.all()

    doc = Eigendom(_id=eigendom.id)
    doc.eigendom_id = eigendom.id

    kadastraal_object_id = kot.id
    doc.kadastraal_object_id = kadastraal_object_id

    doc.kadastraal_object_index = get_kadastraal_object_index(kadastraal_object_id)

    doc.eigenaar_cat_id = eigendom.eigenaar_categorie_id
    doc.eigenaar_cat = get_omschrijving(brk_models.EigenaarCategorie, eigendom.eigenaar_categorie_id, code_field='id',
                                        omschrijving_field='categorie')
    doc.grondeigenaar = eigendom.grondeigenaar
    doc.aanschrijfbaar = eigendom.aanschrijfbaar
    doc.appartementeigenaar = eigendom.appartementeigenaar
    doc.aard_zakelijk_recht_akr = eigendom.aard_zakelijk_recht_akr

    # kot_kadastrale_aanduiding = es.Keyword()  # <-- generated
    doc.kadastrale_gemeentecode = kot.kadastrale_gemeente_id
    doc.sectie = get_omschrijving(brk_models.KadastraleSectie, kot.sectie_id, code_field='id',
                                  omschrijving_field='sectie')
    doc.perceelnummer = str(kot.perceelnummer)
    doc.indexletter = kot.indexletter
    doc.indexnummer = str(kot.indexnummer)
    doc.kadastrale_gemeentenaam = kot.kadastrale_gemeente.naam
    doc.aanduiding = kot.get_aanduiding_spaties()
    doc.koopsom = kot.koopsom
    doc.koopjaar = kot.koopjaar
    doc.grootte = kot.grootte

    # There can be more culturecode_bebouwd in the id, separated by commas
    if kot.cultuurcode_bebouwd_id:
        doc.cultuurcode_bebouwd = ",".join(map(lambda x: get_omschrijving(brk_models.CultuurCodeBebouwd, x),
                                           [x.strip() for x in kot.cultuurcode_bebouwd_id.split(',')]))
    else:
        doc.cultuurcode_bebouwd = None
    doc.cultuurcode_onbebouwd = get_omschrijving(brk_models.CultuurCodeOnbebouwd, kot.cultuurcode_onbebouwd_id)

    vbo_list = kot.verblijfsobjecten.all()  # This is already ordered
    # eerste_adres = es.Keyword()  # <-- generated
    if vbo_list:
        doc.verblijfsobject_id = []
        doc.openbare_ruimte_naam = []
        doc.huisnummer = []
        doc.huisletter = []
        doc.huisnummer_toevoeging = []
        doc.postcode = []
        doc.woonplaats = []
        doc.adressen = []

        for vbo in vbo_list:
            doc.verblijfsobject_id.append(vbo.landelijk_id)
            doc.openbare_ruimte_naam.append(vbo._openbare_ruimte_naam)
            doc.huisnummer.append(vbo._huisnummer)
            doc.huisletter.append(vbo._huisletter)
            doc.huisnummer_toevoeging.append(vbo._huisnummer_toevoeging)
            hoofdadres = vbo.hoofdadres
            if hoofdadres:
                postcode = hoofdadres.postcode
                woonplaats = str(hoofdadres.woonplaats) if hoofdadres.woonplaats else ''
            else:
                postcode = None
                woonplaats = None
            doc.postcode.append(postcode)
            doc.woonplaats.append(woonplaats)
            adres = _cleanup(' '.join(s for s in [
                        vbo._openbare_ruimte_naam,
                        str(vbo._huisnummer),
                        vbo._huisletter,
                        vbo._huisnummer_toevoeging] if s is not None))
            if postcode: # Add postcode with comma
                adres += ', ' + postcode
            doc.adressen.append(adres)

    if doc.adressen:
        doc.eerste_adres = doc.adressen[0]

    stadsdelen = kot.stadsdelen.all()
    if stadsdelen:
        doc.stadsdeel_naam = [stadsdeel.naam for stadsdeel in stadsdelen]
        doc.stadsdeel_code = [stadsdeel.code for stadsdeel in stadsdelen]
    ggws = kot.ggws.all()
    if ggws:
        doc.ggw_code = [ggw.code for ggw in ggws]
        doc.ggw_naam = [ggw.naam for ggw in ggws]
    wijken = kot.wijken.all()
    if wijken:
        doc.wijk_naam = [wijk.naam for wijk in wijken]
        doc.wijk_code = [wijk.code for wijk in wijken]
    buurten = kot.buurten.all()
    if buurten:
        doc.buurt_naam = [buurt.naam for buurt in buurten]
        doc.buurt_code = [buurt.code for buurt in buurten]

    if kot.point_geom:
        doc.geometrie_rd = kot.point_geom.transform('28992', clone=True).wkt
        geometrie_wgs84 = kot.point_geom.transform('wgs84', clone=True)
        doc.geometrie_wgs84 = geometrie_wgs84.wkt
        doc.centroid = geometrie_wgs84.coords
    elif kot.poly_geom:
        doc.geometrie_rd = kot.poly_geom.transform('28992', clone=True).wkt
        geometrie_wgs84 = kot.poly_geom.transform('wgs84', clone=True)
        doc.geometrie_wgs84 = geometrie_wgs84.wkt
        doc.centroid = geometrie_wgs84.centroid.coords

    zrt = eigendom.zakelijk_recht
    if zrt:
        doc.aard_zakelijk_recht = get_omschrijving(brk_models.AardZakelijkRecht, zrt.aard_zakelijk_recht_id)
        if zrt.teller is not None and zrt.noemer is not None:
            doc.zakelijk_recht_aandeel = f"{zrt.teller}/{zrt.noemer}"

    kst = eigendom.kadastraal_subject
    if kst:
        doc.sjt_id = kst.id
        doc.sjt_type = kst.type
        doc.sjt_is_natuurlijk_persoon = kst.is_natuurlijk_persoon()
        doc.sjt_voornamen = kst.voornamen
        doc.sjt_voorvoegsels = kst.voorvoegsels
        doc.sjt_geslachtsnaam = kst.naam
        doc.sjt_naam = kst.volledige_naam()
        doc.sjt_geslacht_omschrijving = get_omschrijving(brk_models.Geslacht, kst.geslacht_id)
        doc.sjt_geboortedatum = get_date(kst.geboortedatum)
        doc.sjt_geboorteplaats = kst.geboorteplaats
        doc.sjt_geboorteland_code = kst.geboorteland_id
        doc.sjt_datum_overlijden = get_date(kst.overlijdensdatum)
        doc.sjt_statutaire_naam = kst.statutaire_naam
        doc.sjt_statutaire_zetel = kst.statutaire_zetel
        doc.sjt_statutaire_rechtsvorm = get_omschrijving(brk_models.Rechtsvorm, kst.rechtsvorm_id)
        doc.sjt_rsin = kst.rsin
        doc.sjt_kvknummer = kst.kvknummer

        woonadres = kst.woonadres
        if woonadres:
            doc.sjt_woonadres = woonadres.volledig_adres()
            doc.sjt_woonadres_buitenland = woonadres.volledig_buitenland_adres()
        postadres = kst.postadres
        if postadres:
            doc.sjt_postadres = postadres.volledig_adres()
            doc.sjt_postadres_buitenland = postadres.volledig_buitenland_adres()
            doc.sjt_postadres_postbus = postadres.postbus_adres()

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
