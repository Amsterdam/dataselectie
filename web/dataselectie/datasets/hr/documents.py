# Python
import logging
# Packages
import elasticsearch_dsl as es
from django.conf import settings
from django.db.models import Q
# Project
from ..bag.models import Nummeraanduiding
from ..hr.models import DataSelectie
from batch import batch

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
    sbi_omschrijving = es.String(index='not_analyzed', multi=True)

    class Meta:
        doc_type = 'vestiging'
        parent = es.MetaField(type='bag_locatie')
        index = settings.ELASTIC_INDICES['DS_INDEX']


def meta_from_hrdataselectie(obj: DataSelectie) -> VestigingenMeta:
    doc = VestigingenMeta(_id="HR" + obj.id)      # HR is added to prevent id collisions
    doc.hoofdcategorie = [sbi['hoofdcategorie'] for sbi in obj.api_json['sbi_codes']]
    doc.subcategorie = [sbi['subcategorie'] for sbi in obj.api_json['sbi_codes']]
    doc.sbi_code = [sbi['sbi_code'] for sbi in obj.api_json['sbi_codes']]
    doc.sbi_omschrijving = [sbi['sub_sub_categorie'] for sbi in obj.api_json['sbi_codes']]
    doc.bedrijfsnaam = obj.api_json['naam']
    doc._parent = obj.bag_vbid          # default value prevent crash if not found!
    doc.bag_vbid = obj.bag_vbid

    nummeraanduiding = get_nummeraanduiding(obj, doc)

    if nummeraanduiding:
        doc._parent = nummeraanduiding.id                  # reference to the parent

    return doc


def get_nummeraanduiding(obj: DataSelectie, doc: VestigingenMeta) -> Nummeraanduiding:
    nummeraanduiding = Nummeraanduiding.objects.filter(hoofdadres=True,
                                                       verblijfsobject__landelijk_id=obj.bag_vbid).first()
    if nummeraanduiding:
        batch.statistics.add('HR verblijfsobjecten')
    else:

        nummeraanduiding = Nummeraanduiding.objects.filter(Q(hoofdadres=True),
                                                           Q(ligplaats__landelijk_id=obj.bag_vbid) |
                                                           Q(standplaats__landelijk_id=obj.bag_vbid)).first()
        if nummeraanduiding:
            batch.statistics.add('HR ligplaatsen/standplaatsen')
        else:
            nummeraanduiding = Nummeraanduiding.objects.filter(landelijk_id=obj.bag_numid).first()
            if nummeraanduiding:
                batch.statistics.add('HR Nummeraanduiding via bag_numid')
            else:
                no_nummeraanduiding_found(obj, doc.bedrijfsnaam)

    return nummeraanduiding


def no_nummeraanduiding_found(obj: DataSelectie, bedrijfsnaam: es.String):
    if 'amsterdam' in obj.api_json['bezoekadres_volledig_adres'].lower():
        batch.statistics.add('HR bezoekadressen in Amsterdam niet gevonden',
                             (obj.bag_numid, obj.id, bedrijfsnaam))

    elif 'amsterdam' in obj.api_json['postadres_volledig_adres'].lower():
        batch.statistics.add('HR postadressen in Amsterdam niet gevonden',
                             (obj.bag_numid, obj.id, bedrijfsnaam))
    else:
        batch.statistics.add('HR adressen buiten Amsterdam niet gevonden',
                             (obj.bag_numid, obj.id, bedrijfsnaam))
