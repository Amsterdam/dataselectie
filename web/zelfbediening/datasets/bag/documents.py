# Python
import json
# Packages
import elasticsearch_dsl as es
# Project
from . import models
from datasets.generic import analyzers
from django.conf import settings


class NummeraanduidingMeta(es.DocType):
    """
    Elastic doc for all meta of a nummeraanduiding.
    Used in the zelfbediening portal
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
    postcode = es.String(analyzer=analyzers.postcode)
    woonplaats = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    hoofdadres = es.Boolean()
    buurt_code = es.String()
    buurt_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    wijk_code = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    wijk_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )
    ggw_code = es.String()
    ggw_naam = es.String()
        fields={'raw': es.String(index='not_analyzed')}
    )
    stadsdeel_code = es.String()
    stadsdeel_naam = es.String(
        fields={'raw': es.String(index='not_analyzed')}
    )

def meta_from_nummeraanduiding(item: models.Nummeraanduiding):
    headers = ('huisnummer', 'huisletter', 'toevoeging', 'postcode', 'hoofdadres', )
    doc = NummeraanduidingMeta(_id=item.id)
    doc.nummeraanduiding_id = item.id
    try:
        doc.naam = item.openbare_ruimte.naam
    except Exception as e:
        print('1', repr(e))
        doc.naam = ''
    doc.woonplaats = 'Amsterdam'
    # Identifing the spatial object
    if item.verblijfsobject:
        obj = item.verblijfsobject
    elif item.ligplaats:
        obj = item.ligplaats
    elif item.standplaats:
        obj = item.standplaats
    else:
        obj = None
    for key in headers:
         setattr(doc, key, getattr(item, key, None))
    if obj:
        try:
            wijk = models.Buurtcombinatie.objects.filter(geometrie__contains=obj.geometrie).first()
            ggw = models.Gebiedsgerichtwerken.objects.filter(geometrie__contains=obj.geometrie).first()
        except Exception as e:
            print ('2:', repr(e))
            wijk = None
            ggw = None
        try:
            doc.buurt_naam = obj.buurt.naam
            doc.buurt_code = '%s%s' % (str(obj.buurt.stadsdeel.code), str(obj.buurt.code))
            doc.stadsdeel_code = obj.buurt.stadsdeel.code
            doc.stadsdeel_naam = obj.buurt.stadsdeel.naam
        except Exception as e:
            print('3:', repr(e))
        if wijk:
            doc.wijk_naam = wijk.naam
            try:
                doc.wijk_code = '%s%s' % (obj.buurt.stadsdeel.code, str(wijk.code))
            except Exception as e:
                print('4:', repr(e))
        if ggw:
            doc.ggw_code = ggw.code
            doc.ggw_naam = ggw.naam
    return doc

