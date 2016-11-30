# Python
from django.conf import settings
import elasticsearch_dsl as es
# Project
from datasets.bag import models
from datasets.hr import models as hrmodels
from datasets.generic import analyzers

import time
import logging

log = logging.getLogger(__name__)


class NummeraanduidingMeta(es.DocType):
    """
    Elastic doc for all meta of a nummeraanduiding.
    Used in the dataselectie portal

    The link with any data that is being used here is
    the bag_id.
    """

    def __init__(self, *args, **kwargs):
        super(NummeraanduidingMeta, self).__init__(*args, **kwargs)

    nummeraanduiding_id = es.String(index='not_analyzed')

    _openbare_ruimte_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    naam = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'keyword': es.String(analyzer=analyzers.subtype),
        }
    )
    huisnummer = es.Integer()
    toevoeging = es.String()
    huisletter = es.String()
    postcode = es.String(index='not_analyzed')
    woonplaats = es.String(index='not_analyzed')

    hoofdadres = es.Boolean()

    buurt_code = es.String(index='not_analyzed')
    buurt_naam = es.String(index='not_analyzed')
    buurtcombinatie_code = es.String(index='not_analyzed')
    buurtcombinatie_naam = es.String(index='not_analyzed')
    ggw_code = es.String(index='not_analyzed')
    ggw_naam = es.String(index='not_analyzed')

    gsg_naam = es.String(index='not_analyzed')

    stadsdeel_code = es.String(index='not_analyzed')
    stadsdeel_naam = es.String(index='not_analyzed')

    # Extended information
    centroid = es.GeoPoint()
    status = es.String(index='not_analyzed')
    type_desc = es.String(index='not_analyzed')
    hoofdadres = es.String(index='not_analyzed')  # Is there a choice option?
    # Landelijke codes
    openabre_ruimte_landelijk_id = es.String(index='not_analyzed')
    verblijfsobject = es.String(index='not_analyzed')
    ligplaats = es.String(index='not_analyzed')
    standplaats = es.String(index='not_analyzed')

    # Verblijfsobject specific data
    gebruiksdoel_omschrijving = es.String(index='not_analyzed')
    oppervlakte = es.Integer()
    bouwblok = es.String(index='not_analyzed')
    gebruik = es.String(index='not_analyzed')
    panden = es.String(index='not_analyzed')

    sbi_codes = es.Nested({
        'properties': {
            'sbi_code': es.String(index='not_analyzed'),
            'hcat': es.String(index='not_analyzed'),
            'scat': es.String(index='not_analyzed'),
            'hoofdcategorie': es.String(index='not_analyzed'),
            'subcategorie': es.String(index='not_analyzed'),
            'sub_sub_categorie': es.String(index='not_analyzed'),
            'bedrijfsnaam': es.String(index='not_analyzed'),
            'vestigingsnummer': es.String(index='not_analyzed')
                }
    })
    is_hr_address = es.Boolean()

    class Meta(object):
        index = settings.ELASTIC_INDICES['DS_BAG']
        all = es.MetaField(enabled=False)


def update_doc_with_adresseerbaar_object(doc, item):
    """
    Voeg alle adreseerbaarobject shizzel toe.

    ligplaats, standplaats, verblijfsobject

    denk aan gerelateerde gebieden.
    """
    adresseerbaar_object = item.adresseerbaar_object

    doc.centroid = (
        adresseerbaar_object
        .geometrie.centroid.transform('wgs84', clone=True).coords)

    # Adding the ggw data
    ggw = adresseerbaar_object._gebiedsgerichtwerken
    if ggw:
        doc.ggw_code = ggw.code
        doc.ggw_naam = ggw.naam

    # Grootstedelijk ontbreekt nog
    gsg = adresseerbaar_object._grootstedelijkgebied
    if gsg:
        doc.gsg_naam = gsg.naam

    doc.buurt_code = '%s%s' % (
        str(adresseerbaar_object.buurt.stadsdeel.code),
        str(adresseerbaar_object.buurt.code)
    )

    doc.buurtcombinatie_code = '%s%s' % (
        str(adresseerbaar_object.buurt.stadsdeel.code),
        str(adresseerbaar_object.buurt.buurtcombinatie.code)
    )

    idx = int(item.type) - 1  # type: int
    doc.type_desc = models.Nummeraanduiding.OBJECT_TYPE_CHOICES[idx][1]


def add_verblijfsobject_data(item, doc):
    """
    vbo gerelateerde data
    """

    obj = item.verblijfsobject

    verblijfsobject_extra = [
        ('verblijfsobject', 'landelijk_id'),
        ('gebruiksdoel_omschrijving', 'gebruiksdoel_omschrijving'),
        ('oppervlakte', 'oppervlakte'),
        ('bouwblok', 'bouwblok.code'),
        ('gebruik', 'gebruik.omschrijving')
    ]

    update_doc_from_param_list(doc, obj, verblijfsobject_extra)

    try:
        doc.panden = '/'.join([i.landelijk_id for i in obj.panden.all()])
    except:
        pass


def meta_from_nummeraanduiding(
        item: models.Nummeraanduiding) -> NummeraanduidingMeta:
    """
    Van een Nummeraanduiding bak een dataselectie document
    met bag informatie en hr informatie
    """

    start = time.time()

    doc = NummeraanduidingMeta(_id=item.id)
    parameters = [
        ('nummeraanduiding_id', 'id'),
        ('naam', 'openbare_ruimte.naam'),
        ('woonplaats', 'openbare_ruimte.woonplaats.naam'),
        ('huisnummer', 'huisnummer'),
        ('huisletter', 'huisletter'),
        ('toevoeging', 'toevoeging'),
        ('postcode', 'postcode'),
        ('_openbare_ruimte_naam', '_openbare_ruimte_naam'),
        ('buurt_naam', 'adresseerbaar_object.buurt.naam'),
        ('buurtcombinatie_naam',
            'adresseerbaar_object.buurt.buurtcombinatie.naam'),
        ('status', 'adresseerbaar_object.status.omschrijving'),
        ('stadsdeel_code', 'stadsdeel.code'),
        ('stadsdeel_naam', 'stadsdeel.naam'),

        # Landelijke IDs
        ('openabre_ruimte_landelijk_id', 'openbare_ruimte.landelijk_id'),
        ('ligplaats', 'ligplaats.landelijk_id'),
        ('standplaats', 'standplaats.landelijk_id'),

    ]
    # Adding the attributes
    update_doc_from_param_list(doc, item, parameters)

    # defaults
    doc.is_hr_address = False
    doc.centroid = None

    # hr vestigingen
    if item.adresseerbaar_object:
        # BAG
        update_doc_with_adresseerbaar_object(doc, item)
        # HR
        update_doc_with_sbicodes(doc, item)

    # Verblijfsobject specific
    if item.verblijfsobject:
        add_verblijfsobject_data(doc, item)

    log.debug('doctime %s', (time.time() - start))

    # asserts?
    return doc


def update_doc_with_sbicodes(doc, item):
    """
    Geef een nummeraanduiding eventuele hr data attributen mee

    denk aan sbi.
    """

    sbi_codes = []
    for hrinfo in hrmodels.DataSelectie.objects.filter(
            bag_vbid=item.adresseerbaar_object.landelijk_id).all():

        sbi_codes += hrinfo.api_json['sbi_codes']
        doc.is_hr_address = True
    if doc.is_hr_address:
        doc.sbi_codes = sbi_codes
    else:
        doc.sbi_codes = []


def update_doc_from_param_list(
        target: dict, source: object, mapping: list) -> None:
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
