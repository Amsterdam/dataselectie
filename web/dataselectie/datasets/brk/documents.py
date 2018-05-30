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
        # all = es.MetaField(enabled=False)
        doc_type = 'eigendom'
        index = settings.ELASTIC_INDICES['DS_BRK_INDEX']

    kadastraal_object_id = es.Keyword()
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

    eerste_adres = es.Keyword()  # <-- generated
    verblijfsobject_id = es.Keyword(multi=True)
    verblijfsobject_openbare_ruimte_naam = es.Keyword(multi=True)
    verblijfsobject_huisnummer = es.Keyword(multi=True)
    verblijfsobject_huisletter = es.Keyword(multi=True)
    verblijfsobject_huisnummer_toevoeging = es.Keyword(multi=True)
    verblijfsobject_postcode = es.Keyword(multi=True)
    verblijfsobject_woonplaats = es.Keyword(multi=True)

    stadsdeel_naam = es.Keyword(multi=True)
    stadsdeel_code = es.Keyword(multi=True)
    ggw_naam = es.Keyword(multi=True)
    ggw_code = es.Keyword(multi=True)
    wijk_naam = es.Keyword(multi=True)
    wijk_code = es.Keyword(multi=True)
    buurt_naam = es.Keyword(multi=True)
    buurt_code = es.Keyword(multi=True)
    geo_point = es.GeoPoint()
    geo_poly = es.GeoShape()

    aard_zakelijk_recht = es.Keyword()
    zakelijk_recht_aandeel = es.Keyword()

    kadastraal_subject = es.Nested(
        properties = {
            'id': es.Keyword(),
            'type': es.Keyword(),
            'is_natuurlijk_persoon': es.Boolean(),
            'voornamen': es.Keyword(),
            'voorvoegsels':es.Keyword(),
            'naam': es.Keyword(),
            'geslacht_omschrijving': es.Keyword(),
            'geboortedatum': es.Date(),
            'geboorteplaats': es.Keyword(),
            'geboorteland_code': es.Keyword(),
            'datum_overlijden': es.Date(),
            'statutaire_naam': es.Keyword(),
            'statutaire_zetel': es.Keyword(),
            'statutaire_rechtsvorm': es.Keyword(),
            'rsin': es.Keyword(),
            'kvknummer': es.Keyword(),
            'woonadres': es.Keyword(),
            'woonadres_buitenland': es.Keyword(),
            'postadres': es.Keyword(),
            'postadres_buitenland': es.Keyword(),
            'postadres_postbus': es.Keyword()
        }
    )

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


def doc_from_eigendom(eigendom: object) -> Eigendom:
    kot = eigendom.kadastraal_object
    # eigendommen = kot.eigendommen.all()

    doc = Eigendom(_id=eigendom.id)
    doc.eigendom_id = eigendom.id

    doc.kadastraal_object_id = kot.id
    doc.eigenaar_cat_id = eigendom.eigenaar_categorie_id
    doc.eigenaar_cat = get_omschrijving(brk_models.EigenaarCategorie, eigendom.eigenaar_categorie_id, code_field='id',
                                        omschrijving_field='categorie')
    doc.grondeigenaar = eigendom.grondeigenaar
    doc.aanschrijfbaar = eigendom.aanschrijfbaar
    doc.appartementeigenaar = eigendom.appartementeigenaar
    doc.aard_zakelijk_recht_akr = eigendom.aard_zakelijk_recht_akr

    # kot_kadastrale_aanduiding = es.Keyword()  # <-- generated
    doc.kadastrale_gemeentecode = kot.kadastrale_gemeente_id
    doc.sectie = kot.sectie_id
    doc.perceelnummer = str(kot.perceelnummer)
    doc.indexletter = kot.indexletter
    doc.indexnummer = str(kot.indexnummer)

    doc.kadastrale_gemeentenaam = kot.kadastrale_gemeente.naam

    doc.aanduiding = _cleanup(
        ' '.join(s for s in [
            doc.kadastrale_gemeentecode,
            doc.sectie,
            doc.perceelnummer,
            doc.indexletter,
            doc.indexnummer
        ] if s is not None)
    )

    doc.koopsom = kot.koopsom
    doc.koopjaar = kot.koopjaar
    doc.grootte = kot.grootte

    doc.cultuurcode_bebouwd = get_omschrijving(brk_models.CultuurCodeBebouwd, kot.cultuurcode_bebouwd_id)
    doc.cultuurcode_onbebouwd = get_omschrijving(brk_models.CultuurCodeOnbebouwd, kot.cultuurcode_onbebouwd_id)

    vbo_list = kot.verblijfsobjecten.all()  # This is already ordered
    # eerste_adres = es.Keyword()  # <-- generated
    if vbo_list:
        doc.verblijfsobject_id = []
        doc.verblijfsobject_openbare_ruimte_naam = []
        doc.verblijfsobject_huisnummer = []
        doc.verblijfsobject_huisletter = []
        doc.verblijfsobject_huisnummer_toevoeging = []
        doc.verblijfsobject_postcode = []
        doc.verblijfsobject_woonplaats = []

        doc.eerste_adres = None
        for vbo in vbo_list:
            doc.verblijfsobject_id.append(vbo.landelijk_id)
            doc.verblijfsobject_openbare_ruimte_naam.append(vbo._openbare_ruimte_naam)
            doc.verblijfsobject_huisnummer.append(str(vbo._huisnummer))
            doc.verblijfsobject_huisletter.append(vbo._huisletter)
            doc.verblijfsobject_huisnummer_toevoeging.append(vbo._huisnummer_toevoeging)
            hoofdadres = vbo.hoofdadres
            if hoofdadres:
                postcode = hoofdadres.postcode
                woonplaats = str(hoofdadres.woonplaats) if hoofdadres.woonplaats else ''
            else:
                postcode = None
                woonplaats = None
            doc.verblijfsobject_postcode.append(postcode)
            doc.verblijfsobject_woonplaats.append(woonplaats)
            if doc.eerste_adres is None:
                doc.eerste_adres = _cleanup(
                    ' '.join(s for s in [
                        vbo._openbare_ruimte_naam,
                        str(vbo._huisnummer),
                        vbo._huisletter,
                        vbo._huisnummer_toevoeging] if s is not None))

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
        doc.geo_point = kot.point_geom.transform('wgs84', clone=True).coords
    if kot.poly_geom:
        multipolygon_wgs84 = kot.poly_geom.transform('wgs84', clone=True)
        # geoshape expects a dict with 'type' and 'coords'
        doc.geo_poly = json.loads(multipolygon_wgs84.geojson)

    zrt = eigendom.zakelijk_recht
    if zrt:
        doc.aard_zakelijk_recht = get_omschrijving(brk_models.AardZakelijkRecht, zrt.aard_zakelijk_recht_id)
        doc.zakelijk_recht_aandeel = f"{zrt.teller}/{zrt.noemer}"

    kst = eigendom.kadastraal_subject
    if kst:
        kst_properties = {
            'id': kst.id,
            'type': kst.type,
            'is_natuurlijk_persoon': kst.is_natuurlijk_persoon(),
            'voornamen': kst.voornamen,
            'voorvoegsels': kst.voorvoegsels,
            'naam': kst.naam,
            'geslacht_omschrijving': get_omschrijving(brk_models.Geslacht, kst.geslacht_id),
            'geboortedatum': get_date(kst.geboortedatum),
            'geboorteplaats': kst.geboorteplaats,
            'geboorteland_code': kst.geboorteland_id,
            'datum_overlijden': get_date(kst.overlijdensdatum),
            'statutaire_naam': kst.statutaire_naam,
            'statutaire_zetel': kst.statutaire_zetel,
            'statutaire_rechtsvorm': get_omschrijving(brk_models.Rechtsvorm, kst.rechtsvorm_id),
            'rsin': kst.rsin,
            'kvknummer': kst.kvknummer,
        }
        woonadres = kst.woonadres
        if woonadres:
            kst_properties.update(
                {
                    'woonadres': woonadres.volledig_adres(),
                    'woonadres_buitenland': woonadres.volledig_buitenland_adres()
                }
            )
        postadres = kst.postadres
        if postadres:
            kst_properties.update(
                {
                    'postadres': postadres.volledig_adres(),
                    'postadres_buitenland': postadres.volledig_buitenland_adres(),
                    'postadres_postbus': postadres.postbus_adres()

                }
            )
        doc.kadastraal_subject.append(kst_properties)

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
