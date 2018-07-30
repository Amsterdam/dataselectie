import json
import logging
import re

from collections import Counter

from django.conf import settings
from django.utils.dateparse import parse_date

from dataselectie import utils
from datasets.brk import models as brk_models
from datasets.bag import models as bag_models

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
    eigenaar_type = es.Keyword(multi=True)
    eigenaar_cat_id = es.Integer()
    eigenaar_cat = es.Keyword()
    aard_zakelijk_recht_akr = es.Keyword()

    eigendom_id = es.Keyword()
    aanduiding = es.Keyword()  # <-- generated
    kadastrale_gemeentecode = es.Keyword()
    sectie = es.Keyword()
    perceelnummer = es.Keyword()
    indexletter = es.Keyword()
    indexnummer = es.Keyword()

    kadastrale_gemeentenaam = es.Keyword()
    burgerlijke_gemeentenaam = es.Keyword()
    koopsom = es.Float()
    koopjaar = es.Integer()
    grootte = es.Float()
    cultuurcode_bebouwd = es.Keyword()
    cultuurcode_onbebouwd = es.Keyword()

    adressen = es.Keyword(multi=True)
    verblijfsobject_id = es.Keyword(multi=True)
    openbare_ruimte_naam = es.Keyword()
    huisnummer = es.Integer()
    huisletter = es.Keyword()
    huisnummer_toevoeging = es.Keyword()
    postcode = es.Keyword()
    woonplaats = es.Keyword()
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
    geometrie = es.GeoShape()

    aard_zakelijk_recht = es.Keyword()
    zakelijk_recht_aandeel = es.Keyword()
    zakelijk_recht_aandeel_float = es.Float()

    sjt_id = es.Keyword()
    sjt_type = es.Keyword()
    sjt_voornamen = es.Keyword()
    sjt_voorvoegsels = es.Keyword()
    sjt_geslachtsnaam = es.Keyword()
    sjt_naam = es.Keyword()
    sjt_geslacht_oms = es.Keyword()
    sjt_geboortedatum = es.Date()
    sjt_geboorteplaats = es.Keyword()
    sjt_geboorteland = es.Keyword()
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


def get_woonplaats(nummeraanduiding):
    openbare_ruimte_id = nummeraanduiding.openbare_ruimte_id
    clazz = bag_models.OpenbareRuimte
    class_name = clazz.__name__
    if class_name not in lookup_tables:
        lookup_tables[class_name] = {}
        elements = clazz.objects.values('id', 'woonplaats_id')
        for e in elements:
            lookup_tables[class_name][e['id']] = e['woonplaats_id']
    woonplaats_id =  lookup_tables[class_name].get(openbare_ruimte_id)
    clazz = bag_models.Woonplaats
    class_name = clazz.__name__
    if class_name not in lookup_tables:
        lookup_tables[class_name] = {}
        elements = clazz.objects.values('id', 'naam')
        for e in elements:
            lookup_tables[class_name][e['id']] = e['naam']
    return lookup_tables[class_name].get(woonplaats_id)


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
# we create the indexes in batches, because then we create a new empty Counter dictionary for each batch,
# and we will have identical kadastrale objecten in different batches with index 0
# Therefore we try to keep the counter in a redis service. This will be accessed by all batches.
# This works if we can connect to the redis server./ Otherwise the normal counter will be use
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
    doc.eigenaar_type = []
    if eigendom.grondeigenaar:
        doc.eigenaar_type.append('Grondeigenaar')
    if eigendom.aanschrijfbaar:
        doc.eigenaar_type.append('Pandeigenaar')
    if eigendom.appartementeigenaar:
        doc.eigenaar_type.append('Appartementseigenaar')
    doc.aard_zakelijk_recht_akr = eigendom.aard_zakelijk_recht_akr

    # kot_kadastrale_aanduiding = es.Keyword()  # <-- generated
    doc.kadastrale_gemeentecode = kot.kadastrale_gemeente_id
    doc.sectie = get_omschrijving(brk_models.KadastraleSectie, kot.sectie_id, code_field='id',
                                  omschrijving_field='sectie')
    doc.perceelnummer = str(kot.perceelnummer)
    doc.indexletter = kot.indexletter
    doc.indexnummer = str(kot.indexnummer)
    doc.kadastrale_gemeentenaam = kot.kadastrale_gemeente.naam
    doc.burgerlijke_gemeentenaam = kot.kadastrale_gemeente.gemeente_id
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
        doc.openbare_ruimte_naam = vbo_list[0]._openbare_ruimte_naam
        doc.huisnummer = vbo_list[0]._huisnummer
        doc.huisletter = vbo_list[0]._huisletter
        doc.huisnummer_toevoeging = vbo_list[0]._huisnummer_toevoeging
        hoofdadres = vbo_list[0].hoofdadres
        if hoofdadres:
            doc.woonplaats = get_woonplaats(hoofdadres)
            doc.postcode = hoofdadres.postcode
        else:
            doc.postcode = ''
            doc.woonplaats = ''

        doc.adressen = []

        for vbo in vbo_list:
            doc.verblijfsobject_id.append(vbo.landelijk_id)
            adres = str(vbo)
            doc.adressen.append(adres)
    else:
        doc.openbare_ruimte_naam = ''
        doc.huisnummer = ''
        doc.huisletter = ''
        doc.huisnummer_toevoeging = ''
        doc.postcode = ''
        doc.woonplaats = ''

    if doc.adressen:
        doc.eerste_adres = doc.adressen[0]

    stadsdelen = kot.stadsdelen.all()
    if stadsdelen:
        doc.stadsdeel_naam = [stadsdeel.naam for stadsdeel in stadsdelen]
        doc.stadsdeel_code = [stadsdeel.code for stadsdeel in stadsdelen]
    else:
        doc.stadsdeel_naam = ['']
        doc.stadsdeel_code = ['']

    ggws = kot.ggws.all()
    if ggws:
        doc.ggw_code = [ggw.code for ggw in ggws]
        doc.ggw_naam = [ggw.naam for ggw in ggws]
    else:
        doc.ggw_code = ['']
        doc.ggw_naam = ['']
    wijken = kot.wijken.all()
    if wijken:
        doc.wijk_naam = [wijk.naam for wijk in wijken]
        doc.wijk_code = [wijk.code for wijk in wijken]
    else:
        doc.wijk_naam = ['']
        doc.wijk_code = ['']
    buurten = kot.buurten.all()
    if buurten:
        doc.buurt_naam = [buurt.naam for buurt in buurten]
        doc.buurt_code = [buurt.code for buurt in buurten]
    else:
        doc.buurt_naam = ['']
        doc.buurt_code = ['']

    geom = kot.point_geom if kot.point_geom else kot.poly_geom
    if geom:
        doc.geometrie_rd = geom.transform('28992', clone=True).wkt
        geometrie_wgs84 = geom.transform('wgs84', clone=True)
        doc.geometrie_wgs84 = geometrie_wgs84.wkt
        doc.geometrie = json.loads(geometrie_wgs84.geojson)
    if hasattr(kot, 'appartementsplot'):
        doc.geometrie = json.loads(kot.appartementsplot.plot.geojson)

    zrt = eigendom.zakelijk_recht
    if zrt:
        doc.aard_zakelijk_recht = get_omschrijving(brk_models.AardZakelijkRecht, zrt.aard_zakelijk_recht_id)
        if zrt.teller is not None and zrt.noemer is not None:
            doc.zakelijk_recht_aandeel = f"{zrt.teller}/{zrt.noemer}"
            doc.zakelijk_recht_aandeel_float = zrt.teller / zrt.noemer

    kst = eigendom.kadastraal_subject
    if kst:
        doc.sjt_id = kst.id
        doc.sjt_type =  brk_models.Eigenaar.SUBJECT_TYPE_CHOICES[kst.type][1]
        doc.sjt_voornamen = kst.voornamen
        doc.sjt_voorvoegsels = kst.voorvoegsels
        if kst.is_natuurlijk_persoon():
            doc.sjt_geslachtsnaam = kst.naam
            doc.sjt_naam = kst.volledige_naam()
        doc.sjt_geslacht_omschrijving = get_omschrijving(brk_models.Geslacht, kst.geslacht_id)
        doc.sjt_geboortedatum = get_date(kst.geboortedatum)
        doc.sjt_geboorteplaats = kst.geboorteplaats
        doc.sjt_geboorteland = get_omschrijving(brk_models.Land, kst.geboorteland_id)
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
