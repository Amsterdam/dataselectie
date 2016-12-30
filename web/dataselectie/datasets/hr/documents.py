import elasticsearch_dsl as es
from django.conf import settings

from ..bag.models import Nummeraanduiding, Verblijfsobject

count_ok = 0
count_error = 0

import logging
log = logging.getLogger(__name__)

class VestigingenMeta(es.DocType):
    """
    Elastic data for vestigingen of handelsregister
    """
    def __init__(self, *args, **kwargs):
        super(VestigingenMeta, self).__init__(*args, **kwargs)

    hoofdcategorie = es.String(index='not_analyzed', multi=True)
    subcategorie = es.String(index='not_analyzed', multi=True)
    sbi_code = es.String(index='not_analyzed', multi=True)
    bedrijfsnaam = es.String(index='not_analyzed')
    bag_numid = es.String(index='not_analyzed')

    class Meta:
        doc_type = 'vestiging'
        parent = es.MetaField(type='bag_locatie')
        index = settings.ELASTIC_INDICES['DS_BAG']


def meta_from_hrdataselectie(obj):
    global count_error, count_ok
    numaan = Nummeraanduiding.objects.filter(landelijk_id=obj.bag_numid).first()
    if not numaan:
        numaan = Verblijfsobject.objects.filter(landelijk_id=obj.bag_numid).first()
    doc = VestigingenMeta(_id="HR" + obj.id)      # HR is added to prevent id collisions
    doc.hoofdcategorie = [sbi['hoofdcategorie'] for sbi in obj.api_json['sbi_codes']]
    doc.subcategorie = [sbi['subcategorie'] for sbi in obj.api_json['sbi_codes']]
    doc.sbi_code = [sbi['sbi_code'] for sbi in obj.api_json['sbi_codes']]
    doc.bedrijfsnaam = obj.api_json['naam']
    doc.bag_numid = obj.bag_numid

    if numaan:
        doc._parent = numaan.id                  # reference to the parent
        count_ok += 1
    else:
        count_error += 1
        doc._parent = obj.bag_numid
        log.error("bag_numid %s NIET gevonden, is dus niet gekoppeld aan een nummeraanduiding", obj.bag_numid)
        
    return doc
