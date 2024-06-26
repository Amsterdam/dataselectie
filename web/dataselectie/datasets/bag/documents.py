# Python
import logging
from typing import List

import elasticsearch_dsl as es
from django.conf import settings

from batch import batch
from datasets.bag import models
from datasets.generic.views_mixins import stringify_item_value

log = logging.getLogger(__name__)


class Nummeraanduiding(es.Document):
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

    oppervlakte = es.Integer()
    bouwblok = es.Keyword()
    gebruik = es.Keyword()
    eigendomsverhouding = es.Keyword()

    # Only for CSV
    panden = es.Keyword()  # id values
    pandnaam = es.Keyword()
    bouwjaar = es.Keyword()
    type_woonobject = es.Keyword()
    ligging = es.Keyword()

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

    # Seems lat/lon needs to be swapped, could be because of a new
    # GDAL version.
    try:
        swap = settings.ELASTIC_SWAP_LAT_LON_COORDS 
        centroid = (
            adresseerbaar_object
            .geometrie.centroid.transform('wgs84', clone=True).coords)
        doc.centroid = centroid[::-1] if swap else centroid
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
    if buurt and buurt.buurtcombinatie:
        batch.statistics.add('BAG Inclusief buurt', total=False)
        doc.buurt_code = str(buurt.code)
        doc.buurtcombinatie_code = str(buurt.buurtcombinatie.code)

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
        ('eigendomsverhouding', 'eigendomsverhouding'),
    ]
    update_doc_from_param_list(doc, vbo, verblijfsobject_extra)

    doc.geconstateerd = "Ja" if vbo.indicatie_geconstateerd else "Nee"
    doc.in_onderzoek = "Ja" if vbo.indicatie_in_onderzoek else "Nee"

    # These fields are only indexed to generate the BagCSV.
    # Hence this data is not structured for search, but flattened.
    doc.gebruiksdoel = " | ".join(vbo.gebruiksdoel)
    doc.toegang = " | ".join(vbo.toegang)

    # pandnaam is often empty, except for things like "Centraal Station".
    panden: List[models.Pand] = list(vbo.panden.all())
    doc.panden = stringify_item_value([p.landelijk_id for p in panden])
    doc.pandnaam = stringify_item_value([p.pandnaam for p in panden if p.pandnaam])
    doc.bouwjaar = stringify_item_value([
        "onbekend" if p.bouwjaar == 1005 else p.bouwjaar for p in panden
    ])
    doc.type_woonobject = stringify_item_value([p.type_woonobject for p in panden])
    doc.ligging = stringify_item_value([p.ligging for p in panden])


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
