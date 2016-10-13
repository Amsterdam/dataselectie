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
    postcode = es.String(
        analyzer=analyzers.postcode,
        fields={'raw': es.String(index='not_analyzed')}
        )
    woonplaats = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    hoofdadres = es.Boolean()
    buurt_code = es.String()
    buurt_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    buurtcombinatie_code = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    buurtcombinatie_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    ggw_code = es.String()
    ggw_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    stadsdeel_code = es.String()
    stadsdeel_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    ),
    centroid = es.GeoPoint()


def meta_from_nummeraanduiding(item: models.Nummeraanduiding):
    headers = (
        'huisnummer', 'huisletter', 'toevoeging', 'postcode', 'hoofdadres',)
    doc = NummeraanduidingMeta(_id=item.id)
    doc.nummeraanduiding_id = item.id
    try:
        doc.naam = item.openbare_ruimte.naam
    except Exception as e:
        doc.naam = ''
    doc.woonplaats = 'Amsterdam'
    # Identifing the spatial object
    obj = item.adresseerbaar_object
    for key in headers:
        setattr(doc, key, getattr(item, key, None))
    if obj:
        # Saving centroind of it exists
        try:
            doc.centroid = obj.geometrie.centroid.transform('wgs84')
        except:
            doc.centroid = None

        # Adding the buurt -> stadsdeel data
        try:
            ggw = models.Gebiedsgerichtwerken.objects.filter(
                geometrie__contains=obj.geometrie).first()
            if ggw:
                doc.ggw_code = ggw.code
                doc.ggw_naam = ggw.naam
        except:
            pass
        try:
            doc.buurt_naam = obj.buurt.naam
            doc.buurt_code = '%s%s' % (
                str(obj.buurt.stadsdeel.code), str(obj.buurt.code)
            )
        except:
            pass
        try:
            doc.buurtcombinatie_naam = obj.buurt.buurtcombinatie.naam
            doc.buurtcombinatie_code = '%s%s' % (
                obj.buurt.stadsdeel.code, str(obj.buurt.buurtcombinatie.code)
            )
        except:
            pass
        try:
            doc.stadsdeel_code = obj.buurt.stadsdeel.code
            doc.stadsdeel_naam = obj.buurt.stadsdeel.naam
        except:
            print('Cannot add stadsdeel') 

    return doc
