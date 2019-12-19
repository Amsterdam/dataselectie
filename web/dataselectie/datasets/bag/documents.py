# Python
import logging

import elasticsearch_dsl as es
from django.conf import settings

from batch import batch
from datasets.bag import models
from datasets.generic.views_mixins import stringify_item_value

log = logging.getLogger(__name__)


class Nummeraanduiding(es.DocType):
    """
    Elastic doc for all meta of a nummeraanduiding.
    Used in the dataselectie portal

    The link with any data that is being used here is
    the bag_id.
    """
    nummeraanduiding_id = es.Keyword()
    landelijk_id = es.Keyword()

    _openbare_ruimte_naam = es.Keyword()
    naam = es.Keyword()
    huisnummer = es.Integer()
    huisnummer_toevoeging = es.Keyword()
    huisletter = es.Keyword()
    postcode = es.Keyword()
    woonplaats = es.Keyword()

    buurt_code = es.Keyword()
    buurt_naam = es.Keyword()
    buurtcombinatie_code = es.Keyword()
    buurtcombinatie_naam = es.Keyword()
    ggw_code = es.Keyword()
    ggw_naam = es.Keyword()

    gsg_naam = es.Keyword()

    stadsdeel_code = es.Keyword()
    stadsdeel_naam = es.Keyword()

    # Extended information
    centroid = es.GeoPoint()
    status = es.Keyword()
    type_desc = es.Keyword()
    type_adres = es.Keyword()

    # Landelijke codes
    openbare_ruimte_landelijk_id = es.Keyword()
    verblijfsobject = es.Keyword()
    ligplaats = es.Keyword()
    standplaats = es.Keyword()

    # Verblijfsobject specific data
    gebruiksdoel = es.Keyword(index=False, multi=True)
    gebruiksdoel_woonfunctie = es.Keyword()
    gebruiksdoel_gezondheidszorgfunctie = es.Keyword()

    geconstateerd = es.Keyword()
    in_onderzoek = es.Keyword()

    aantal_eenheden_complex = es.Integer()
    aantal_kamers = es.Integer()
    toegang = es.Keyword(index=False, multi=True)
    verdieping_toegang = es.Integer()
    bouwlagen = es.Integer()
    hoogste_bouwlaag = es.Integer()
    laagste_bouwlaag = es.Integer()
    bouwjaar = es.Keyword()

    oppervlakte = es.Integer()
    bouwblok = es.Keyword()
    gebruik = es.Keyword()
    panden = es.Keyword()

    class Meta:
        doc_type = 'nummeraanduiding'

    class Index:
        doc_type = 'nummeraanduiding'
        name = settings.ELASTIC_INDICES['DS_BAG_INDEX']


def update_doc_with_adresseerbaar_object(doc: Nummeraanduiding, item: models.Nummeraanduiding):
    """
    Voeg alle adreseerbaarobject shizzel toe.

    ligplaats, standplaats, verblijfsobject

    denk aan gerelateerde gebieden.
    """
    adresseerbaar_object = item.adresseerbaar_object

    try:
        doc.centroid = (
            adresseerbaar_object
            .geometrie.centroid.transform('wgs84', clone=True).coords)
    except AttributeError:
        batch.statistics.add('BAG Missing geometrie', total=False)
        log.error('Missing geometrie %s' % adresseerbaar_object)
        log.error(adresseerbaar_object)

    # Adding the ggw data
    ggw = adresseerbaar_object._gebiedsgerichtwerken
    if ggw:
        batch.statistics.add('BAG Gebiedsgericht werken', total=False)
        doc.ggw_code = ggw.code
        doc.ggw_naam = ggw.naam

    # Grootstedelijk ontbreekt nog
    gsg = adresseerbaar_object._grootstedelijkgebied
    if gsg:
        batch.statistics.add('BAG Grootstedelijk gebied', total=False)
        doc.gsg_naam = gsg.naam

    buurt = adresseerbaar_object.buurt
    if buurt:
        batch.statistics.add('BAG Inclusief buurt', total=False)
        doc.buurt_code = '%s%s' % (
            str(buurt.stadsdeel.code),
            str(buurt.code)
        )

        doc.buurtcombinatie_code = '%s%s' % (
            str(buurt.stadsdeel.code),
            str(buurt.buurtcombinatie.code)
        )

    idx = int(item.type) - 1  # type: int
    doc.type_desc = models.Nummeraanduiding.OBJECT_TYPE_CHOICES[idx][1]


def update_doc_from_param_list(target: Nummeraanduiding, source: object, mapping: list) -> None:
    """
    Given a list of parameters (target_field, source_field)
    try to add it to the given document
    from the source object
    """
    for (attr, obj_link) in mapping:
        value = source
        obj_link = obj_link.split('.')
        try:
            for link in obj_link:
                value = getattr(value, link, None)
            setattr(target, attr, value)
        except Exception as e:
            pass


def add_verblijfsobject_data(doc: Nummeraanduiding, vbo: models.Verblijfsobject):
    """
    vbo gerelateerde data
    """
    verblijfsobject_extra = [
        ('verblijfsobject', 'landelijk_id'),
        ('oppervlakte', 'oppervlakte'),
        ('bouwblok', 'bouwblok.code'),
        ('gebruik', 'gebruik'),
        ('gebruiksdoel_woonfunctie', 'gebruiksdoel_woonfunctie'),
        ('gebruiksdoel_gezondheidszorgfunctie', 'gebruiksdoel_gezondheidszorgfunctie'),
        ('aantal_eenheden_complex', 'aantal_eenheden_complex'),
        ('aantal_kamers', 'aantal_kamers'),
        ('verdieping_toegang', 'verdieping_toegang'),
        ('bouwlagen', 'bouwlagen'),
        ('hoogste_bouwlaag', 'hoogste_bouwlaag'),
        ('laagste_bouwlaag', 'laagste_bouwlaag'),
    ]
    update_doc_from_param_list(doc, vbo, verblijfsobject_extra)

    if vbo.indicatie_geconstateerd is not None and vbo.indicatie_geconstateerd is True:
        doc.geconstateerd = "Ja"
    else:
        doc.geconstateerd = "Nee"

    if vbo.indicatie_in_onderzoek is not None and vbo.indicatie_in_onderzoek is True:
        doc.in_onderzoek = "Ja"
    else:
        doc.in_onderzoek = "Nee"

    doc.gebruiksdoel = " | ".join(vbo.gebruiksdoel)
    doc.toegang = " | ".join(vbo.toegang)

    panden_ids = [i.landelijk_id for i in vbo.panden.all()]
    doc.panden = " | ".join(panden_ids)

    panden_bouwjaar = [str(i.bouwjaar) for i in vbo.panden.all()]
    doc.bouwjaar = " | ".join(panden_bouwjaar)


def doc_from_nummeraanduiding(
        item: models.Nummeraanduiding) -> Nummeraanduiding:
    """
    Van een Nummeraanduiding bak een dataselectie document
    met bag informatie en hr informatie
    """

    batch.statistics.add('BAG Nummeraanduiding', total=False)

    # start = time.time()

    doc = Nummeraanduiding(_id=item.landelijk_id)
    parameters = [
        ('nummeraanduiding_id', 'id'),
        ('naam', 'openbare_ruimte.naam'),
        ('woonplaats', 'openbare_ruimte.woonplaats.naam'),
        ('huisnummer', 'huisnummer'),
        ('huisletter', 'huisletter'),
        ('huisnummer_toevoeging', 'huisnummer_toevoeging'),
        ('postcode', 'postcode'),
        ('_openbare_ruimte_naam', '_openbare_ruimte_naam'),
        ('buurt_naam', 'adresseerbaar_object.buurt.naam'),
        ('buurtcombinatie_naam',
         'adresseerbaar_object.buurt.buurtcombinatie.naam'),
        ('status', 'adresseerbaar_object.status'),
        ('stadsdeel_code', 'stadsdeel.code'),
        ('stadsdeel_naam', 'stadsdeel.naam'),

        # Landelijke IDs
        ('openbare_ruimte_landelijk_id', 'openbare_ruimte.landelijk_id'),
        ('ligplaats', 'ligplaats.landelijk_id'),
        ('standplaats', 'standplaats.landelijk_id'),
        ('landelijk_id', 'landelijk_id'),
        ('type_adres', 'type_adres')
    ]
    # Adding the attributes
    update_doc_from_param_list(doc, item, parameters)

    # defaults
    doc.centroid = None

    # hr vestigingen
    if item.adresseerbaar_object:
        # BAG
        batch.statistics.add('BAG Adresseerbaar objecten', total=False)
        update_doc_with_adresseerbaar_object(doc, item)

    # Verblijfsobject specific
    if item.verblijfsobject:
        batch.statistics.add('BAG Verblijfs objecten', total=False)
        add_verblijfsobject_data(doc, item.verblijfsobject)

    # asserts?
    return doc
