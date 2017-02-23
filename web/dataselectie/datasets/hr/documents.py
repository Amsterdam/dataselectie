# Python
import logging

import elasticsearch_dsl as es
from django.conf import settings

from datasets.hr.models import DataSelectie

log = logging.getLogger(__name__)

saved_existing_bag_vbid = None


class Vestiging(es.DocType):
    """
    Elastic data for vestigingen of handelsregister
    """
    vestiging_id = es.String(index='not_analyzed')
    kvk_nummer = es.String(index='not_analyzed')
    handelsnaam = es.String(index='not_analyzed')
    datum_aanvang = es.Date()
    datum_einde = es.Date()
    eigenaar_naam = es.String(index='not_analyzed')
    eigenaar_id = es.String(index='not_analyzed')

    # Address information
    bezoekadres_volledig_adres = es.String(index='not_analyzed')
    bezoekadres_correctie = es.Boolean()
    bezoekadres_openbare_ruimte = es.String(index='not_analyzed')
    bezoekadres_huisnummer = es.String(index='not_analyzed')
    bezoekadres_huisletter = es.String(index='not_analyzed')
    bezoekadres_huisnummertoevoeging = es.String(index='not_analyzed')
    bezoekadres_postcode = es.String(index='not_analyzed')
    bezoekadres_woonplaats = es.String(index='not_analyzed')
    postadres_volledig_adres = es.String(index='not_analyzed')
    # And the bag numid
    bag_numid = es.String(index='not_analyzed')

    # Categores
    hcat = es.String(index='not_analyzed', multi=True)
    hoofdcategorie = es.String(index='not_analyzed', multi=True)
    scat = es.String(index='not_analyzed', multi=True)
    subcategorie = es.String(index='not_analyzed', multi=True)
    # SBI codes
    sbi_code = es.String(index='not_analyzed', multi=True)
    sbi_omschrijving = es.String(index='not_analyzed', multi=True)


    class Meta:
        doc_type = 'vestiging'
        index = settings.ELASTIC_INDICES['DS_INDEX']


def flatten_sbi(activiteit):
    """
    This is a fill gap until HR will create flat sbi codes
    """
    return {
        'sbi_code': activiteit['sbi_code'],
        'sbi_omschrijving': activiteit['sbi_omschrijving'],
        'title': activiteit['sbi_code_link']['title'],
        'scat': (activiteit['sbi_code_link'].get('sub_cat', {})).get('scat', ''),
        'subcategorie': (activiteit['sbi_code_link'].get('sub_cat', {})).get('subcategorie', ''),
        'hcat': ((activiteit['sbi_code_link'].get('sub_cat', {})).get('hcat', {})).get('hcat', ''),
        'hoofdcategorie': ((activiteit['sbi_code_link'].get('sub_cat', {})).get('hcat', {})).get('hoofdcategorie', ''),
    }

def vestiging_from_hrdataselectie(item: DataSelectie) -> Vestiging:
    doc = Vestiging(_id=item.id)  # HR is added to prevent id collisions

    doc.vestiging_id = item.id
    doc.bag_numid = item.bag_numid

    # Working with the json
    data = item.api_json
    # Maatschapelijke activiteit
    mat = data['maatschappelijke_activiteit']
    for attrib in ('kvk_nummer', 'datum_aanvang', 'datum_einde', 'eigenaar_naam', 'eigenaar_id'):
        setattr(doc, attrib, mat.get(attrib, ''))
    doc.eigenaar_naam = mat['eigenaar'].get('volledig_naam', '')
    doc.eigenaar_id = mat['eigenaar'].get('id', '')

    # Using Vestiging name, otherwise, maatschappelijke_activiteit name, otherwise empty
    doc.handelsnaam = data.get('naam', mat.get('naam', ''))

    # Address
    bezoekadres = data['bezoekadres']
    for attrib in ('volledig_adres', 'correctie', 'openbare_ruimte', 'huisnummer',
                   'huisletter', 'huisnummertoevoeging', 'postcode', 'woonplaats'):
        setattr(doc, f'bezoekadres_{attrib}', bezoekadres.get(attrib, ''))
    doc.postadres_volledig_adres = data['postadres']['volledig_adres']

    # SBI codes, categories and subcategories
    # Creating lists of the values and then setting
    # the document
    attributes = ('hcat', 'hoofdcategorie', 'scat', 'subcategorie', 'sbi_code', 'sbi_omschrijving')
    codes = {}  # @TODO named tuple
    for activiteit in data['activiteiten']:
        activiteit = flatten_sbi(activiteit)
        print(activiteit)
        for attrib in attributes:
            codes[attrib] = codes.get(attrib, []) + [activiteit.get(attrib, '')]
    for attrib in attributes:
        setattr(doc, attrib, codes.get(attrib))

    return doc
