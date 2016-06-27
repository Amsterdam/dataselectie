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
    straatnaam = es.String(
        analyzer=analyzers.adres,
        fields={
            'raw': es.String(index='not_analyzed'),
            'ngram_edge': es.String(
                analyzer=analyzers.autocomplete, search_analyzer='standard'
            ),
            'keyword': es.String(analyzer=analyzers.subtype),
        }
    )
    woonplaats = es.String()
    hoofdadres = es.Boolean()
    buurt_code = es.String()
    buurt_naam = es.String()
    wijk_code = es.String()
    wijk_naam = es.String()
    ggw_code = es.String()
    ggw_naam = es.String()
    stadsdeel_code = es.String()
    stadsdeel_naam = es.String()

def meta_from_nummeraanduiding(item: models.Nummeraanduiding):
    headers = ('huisnummer', 'huisletter', 'toevoeging', 'postcode', 'hoofdadres', )
    doc = NummeraanduidingMeta()
    doc.nummeraanduiding_id = item.id
    doc.naam = item.openbare_ruimte.naam
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
        wijk = models.Buurtcombinatie.objects.filter(geometrie__contains=obj.geometrie).first()
        ggw = models.Gebiedsgerichtwerken.objects.filter(geometrie__contains=obj.geometrie).first()
        try:
            doc.buurt_naam = obj.buurt.naam
            doc.buurt_code = '%s%s' % (str(obj.buurt.stadsdeel.code), str(obj.buurt.code))
            doc.stadsdeel_code = obj.buurt.stadsdeel.code
            doc.stadsdeel_naam = obj.buurt.stadsdeel.naam
        except:
            pass
        if wijk:
            doc.wijk_naam = wijk.naam
            try:
                doc.wijk_code = '%s%s' % (obj.buurt.stadsdeel.code, str(wijk.code))
            except:
                pass
        if ggw:
            doc.ggw_code = ggw.code
            doc.ggw_naam = ggw.naam
        return doc
 
