# Python
from typing import List, cast
# Packages
from django.conf import settings
import elasticsearch_dsl as es
# Project
from datasets.bag import models
from datasets.generic import analyzers


class NummeraanduidingMeta(es.DocType):
    """
    Elastic doc for all meta of a nummeraanduiding.
    Used in the dataselectie portal
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

    class Meta(object):
        index = settings.ELASTIC_INDICES['DS_BAG']
        all = es.MetaField(enabled=False)


def meta_from_nummeraanduiding(item: models.Nummeraanduiding) -> NummeraanduidingMeta:
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
        ('buurtcombinatie_naam', 'adresseerbaar_object.buurt.buurtcombinatie.naam'),
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

    # Saving centroind of it exists
    try:
        doc.centroid = item.adresseerbaar_object.geometrie.centroid.transform('wgs84')
    except Exception as e:
        doc.centroid = None

    # Adding the ggw data
    try:
        ggw = models.Gebiedsgerichtwerken.objects.filter(
            geometrie__contains=item.adresseerbaar_object.geometrie).first()
        if ggw:
            doc.ggw_code = ggw.code
            doc.ggw_naam = ggw.naam
    except Exception as e:
        pass
    try:
        doc.buurt_code = '%s%s' % (
            str(item.adresseerbaar_object.buurt.stadsdeel.code),
            str(item.adresseerbaar_object.buurt.code)
        )
    except Exception as e:
        pass
    try:
        doc.buurtcombinatie_code = '%s%s' % (
            str(item.adresseerbaar_object.buurt.stadsdeel.code),
            str(item.adresseerbaar_object.buurt.buurtcombinatie.code)
        )
    except Exception as e:
        pass
    try:
        idx = int(item.type) - 1  # type: int
        doc.type_desc = models.Nummeraanduiding.OBJECT_TYPE_CHOICES[idx][1]
    except Exception as e:
        pass

    # Verblijfsobject specific
    if item.verblijfsobject:
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

    return doc


def update_doc_from_param_list(doc: dict, item: object, params: list) -> None:
    for (attr, obj_link) in params:
        value = item
        obj_link = obj_link.split('.')
        try:
            for link in obj_link:
                value = getattr(value, link, None)
            setattr(doc, attr, value)
        except Exception as e:
            pass
