# Packages
import elasticsearch_dsl as es

from datasets.bag import models
from datasets.generic import analyzers


class NummeraanduidingMeta(es.DocType):
    """
    Elastic doc for all meta of a nummeraanduiding.
    Used in the dataselectie portal
    """
    nummeraanduiding_id = es.String(index='not_analyzed')

    _openbare_ruimte_naam = es.String(
        fields={'raw':es.String(index='not_analyzed')}
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
    nummeraanduiding_landelijk_id = es.String(index='not_analyzed')
    verblijfsobject = es.String(index='not_analyzed')
    ligplaats = es.String(index='not_analyzed')
    standplaats = es.String(index='not_analyzed')

    # Verblijfsobject specific data
    gebruiksdoel_omschrijving = es.String(index='not_analyzed')
    oppervlakte = es.Integer()
    bouwblok = es.String(index='not_analyzed')
    gebruik = es.String(index='not_analyzed')
    panden = es.String(index='not_analyzed')


def meta_from_nummeraanduiding(item: models.Nummeraanduiding):
    doc = NummeraanduidingMeta(_id=item.id)
    doc.nummeraanduiding_id = item.id
    try:
        doc.naam = item.openbare_ruimte.naam
    except Exception as e:
        print('1', repr(e))
        doc.naam = ''
    try:
        doc.woonplaats = item.openbare_ruimte.woonplaats.naam
    except Exception as e:
        print('2', repr(e))
    # Identifing the spatial object
    obj = item.adresseerbaar_object
    headers = (
        'huisnummer', 'huisletter', 'toevoeging', 'postcode',
        '_openbare_ruimte_naam')
    for key in headers:
        setattr(doc, key, getattr(item, key, None))
    if obj:
        # Saving centroind of it exists
        try:
            doc.centroid = obj.geometrie.centroid.transform('wgs84')
        except Exception as e:
            print('3', repr(e))
            doc.centroid = None

        # Adding the buurt -> stadsdeel data
        try:
            ggw = models.Gebiedsgerichtwerken.objects.filter(
                geometrie__contains=obj.geometrie).first()
            if ggw:
                doc.ggw_code = ggw.code
                doc.ggw_naam = ggw.naam
        except Exception as e:
            print('4', repr(e))
        try:
            doc.buurt_naam = obj.buurt.naam
            doc.buurt_code = '%s%s' % (
                str(obj.buurt.stadsdeel.code), str(obj.buurt.code)
            )
        except Exception as e:
            print('5', repr(e))
        try:
            doc.buurtcombinatie_naam = obj.buurt.buurtcombinatie.naam
            doc.buurtcombinatie_code = '%s%s' % (
                obj.buurt.stadsdeel.code, str(obj.buurt.buurtcombinatie.code)
            )
        except Exception as e:
            print('6', repr(e))
        # Extended information
        try:
            doc.status = obj.status.omschrijving
        except Exception as e:
            print('7', repr(e))
    try:
        doc.stadsdeel_code = item.stadsdeel.code
        doc.stadsdeel_naam = item.stadsdeel.naam
    except Exception as e:
        print('8', repr(e))
    try:
        doc.type_desc = models.Nummeraanduiding.OBJECT_TYPE_CHOICES[int(item.type) - 1][1]
    except Exception as e:
        print('9', repr(e))
    try:
        doc.hoofdadres = 'Ja' if item.hoofdadres else 'Nee'
    except:
        print('15', repr(e))
    # Landelijke IDs
    try:
        doc.openabre_ruimte_landelijk_id = item.openbare_ruimte.landelijk_id
    except Exception as e:
        print('16', repr(e))
    try:
        doc.verblijfsobject = item.verblijfsobject.landelijk_id
    except Exception as e:
        print('17', repr(e))
    try:
        doc.ligplaats = item.ligplaats.landelijk_id
    except Exception as e:
        print('18', repr(e))
    try:
        doc.standplaats = item.standplaats.landelijk_id
    except Exception as e:
        print('19', repr(e))

    # Verblijfsobject specific
    if item.verblijfsobject:
        try:
            doc.gebruiksdoel_omschrijving = item.verblijfsobject.gebruiksdoel_omschrijving
        except Exception as e:
            print('14', repr(e))
        try:
            doc.oppervlakte = item.verblijfsobject.oppervlakte
        except Exception as e:
            print('10', repr(e))
        try:
            doc.bouwblok = item.verblijfsobject.bouwblok.code
        except Exception as e:
            print('11', repr(e))
        try:
            doc.gebruik = item.verblijfsobject.gebruik.omschrijving
        except Exception as e:
            print('12', repr(e))
        try:
            doc.panden = '/'.join([i.landelijk_id for i in item.verblijfsobject.panden.all()])
        except Exception as e:
            print('13', repr(e))

    return doc
