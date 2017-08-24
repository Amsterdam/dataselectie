# Python
import logging

import elasticsearch_dsl as es
from django.conf import settings

from datasets.bag.models import Nummeraanduiding
from datasets.hr.models import DataSelectie

log = logging.getLogger(__name__)


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
    non_mailing = es.Boolean()

    # Address information
    bezoekadres_volledig_adres = es.String(index='not_analyzed')
    bezoekadres_correctie = es.Boolean()
    bezoekadres_afgeschermd = es.Boolean()
    bezoekadres_openbare_ruimte = es.String(index='not_analyzed')
    bezoekadres_huisnummer = es.Integer(index='not_analyzed')
    bezoekadres_huisletter = es.String(index='not_analyzed')
    bezoekadres_huisnummertoevoeging = es.String(index='not_analyzed')
    bezoekadres_postcode = es.String(index='not_analyzed')
    bezoekadres_plaats = es.String(index='not_analyzed')

    bezoekadres_buurt_code = es.String(index='not_analyzed')
    bezoekadres_buurt_naam = es.String(index='not_analyzed')
    bezoekadres_buurtcombinatie_code = es.String(index='not_analyzed')
    bezoekadres_buurtcombinatie_naam = es.String(index='not_analyzed')
    bezoekadres_ggw_code = es.String(index='not_analyzed')
    bezoekadres_ggw_naam = es.String(index='not_analyzed')
    bezoekadres_gsg_naam = es.String(index='not_analyzed')
    bezoekadres_stadsdeel_code = es.String(index='not_analyzed')
    bezoekadres_stadsdeel_naam = es.String(index='not_analyzed')

    postadres_volledig_adres = es.String(index='not_analyzed')
    postadres_correctie = es.Boolean()
    postadres_afgeschermd = es.Boolean()
    postadres_openbare_ruimte = es.String(index='not_analyzed')
    postadres_huisnummer = es.Integer(index='not_analyzed')
    postadres_huisletter = es.String(index='not_analyzed')
    postadres_huisnummertoevoeging = es.String(index='not_analyzed')
    postadres_postcode = es.String(index='not_analyzed')
    postadres_plaats = es.String(index='not_analyzed')

    # And the bag numid
    bag_numid = es.String(index='not_analyzed')
    centroid = es.GeoPoint()

    # Categores
    hoofdcategorie = es.String(index='not_analyzed', multi=True)
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
    error = None

    sbi_code_tree = activiteit.get('sbi_code_tree', {})

    if not sbi_code_tree:
        error = "missing sbi information"
        qa_tree = {}
        sbi_code_tree = {}
    else:
        qa_tree = sbi_code_tree.get('qa_tree', {}) or {}

    return {
        'sbi_code': activiteit.get('sbi_code', ''),
        'sbi_omschrijving': activiteit.get('sbi_omschrijving', ''),
        'qa_tree': sbi_code_tree.get('qa_tree', ''),
        'sbi_tree': sbi_code_tree.get('sbi_tree', ''),
        'title': sbi_code_tree.get('title', ''),

        'hoofdcategorie': qa_tree.get('q1', ''),
        'subcategorie': qa_tree.get('q2', ''),
    }, error


def add_bag_info(doc, item):
    """
    Adding bag information
    """
    adresseerbaar_object = item.adresseerbaar_object
    # If there is no adresseerbaar_object there is no
    # point to continue
    if not adresseerbaar_object:
        return

    # Adding geolocation
    try:
        geom = adresseerbaar_object.geometrie
        doc.centroid = geom.centroid.transform('wgs84', clone=True).coords
    except AttributeError:
        log.error('Missing geometrie %s' % adresseerbaar_object)

    # Adding the ggw data
    ggw = adresseerbaar_object._gebiedsgerichtwerken
    if ggw:
        doc.bezoekadres_ggw_code = ggw.code
        doc.bezoekadres_ggw_naam = ggw.naam

    # Grootstedelijk ontbreekt nog
    gsg = adresseerbaar_object._grootstedelijkgebied
    if gsg:
        doc.bezoekadres_gsg_naam = gsg.naam

    buurt = adresseerbaar_object.buurt
    if buurt:
        # Buurt
        doc.bezoekadres_buurt_code = '%s%s' % (
            str(buurt.stadsdeel.code),
            str(buurt.code)
        )
        doc.bezoekadres_buurt_naam = buurt.naam
        # Buurtcombinatie
        doc.bezoekadres_buurtcombinatie_code = '%s%s' % (
            str(buurt.stadsdeel.code),
            str(buurt.buurtcombinatie.code)
        )
        doc.bezoekadres_buurtcombinatie_naam = buurt.buurtcombinatie.naam
        # Stadsdeel
        doc.bezoekadres_stadsdeel_naam = buurt.stadsdeel.naam
        doc.bezoekadres_stadsdeel_code = buurt.stadsdeel.code


def vestiging_from_hrdataselectie(
        item: DataSelectie, bag_item: Nummeraanduiding) -> Vestiging:
    doc = Vestiging(_id=item.id)  # HR is added to prevent id collisions
    doc.bag_numid = item.bag_numid

    # Working with the json
    data = item.api_json
    doc.vestiging_id = data['vestigingsnummer']
    # Maatschapelijke activiteit
    mat = data['maatschappelijke_activiteit']
    for attrib in (
            'kvk_nummer', 'datum_aanvang',
            'datum_einde', 'eigenaar_naam',
            'eigenaar_id', 'non_mailing'):
        setattr(doc, attrib, mat.get(attrib, ''))
    doc.eigenaar_naam = mat['eigenaar'].get('volledige_naam', '')
    doc.eigenaar_id = mat['eigenaar'].get('id', '')

    # Using Vestiging name, otherwise,
    # maatschappelijke_activiteit name, otherwise empty
    doc.handelsnaam = data.get('naam', mat.get('naam', ''))

    # Address
    for address_type in ('bezoekadres', 'postadres'):
        adres = data[address_type]
        if isinstance(adres, dict):
            for attrib in (
                    'volledig_adres', 'correctie', 'huisnummer',
                    'huisletter', 'huisnummertoevoeging',
                    'postcode', 'plaats'):
                setattr(doc, f'{address_type}_{attrib}', adres.get(attrib, ''))

            # In HR is the openbareruimte naam is
            # called straatnaam
            setattr(
                doc, f'{address_type}_openbare_ruimte',
                adres.get('straatnaam'))

            correctie = True if adres.get('correctie') else False
            setattr(doc, f'{address_type}_correctie', correctie)
            afgeschermd = adres.get('afgeschermd', False)
            setattr(doc, f'{address_type}_afgeschermd', afgeschermd)

    # SBI codes, categories and subcategories
    # Creating lists of the values and then setting
    # the document

    codes = {
        'hoofdcategorie': [],
        'subcategorie': [],
        'sbi_code': [],
        'sbi_omschrijving': [],

        # 'sbi_l1': [],
        # 'sbi_l2': [],
        # 'sbi_l3': [],
        # 'sbi_l4': [],
        # 'sbi_l5': [],
    }

    for activiteit in data['activiteiten']:
        # Flattening the sbi information
        activiteit, error = flatten_sbi(activiteit)

        if error:
            log.error("""

            No sbi information for activiteit:
            %s
            %s
            %s

                """, doc.handelsnaam, activiteit, doc.vestiging_id)

        for key, items in codes.items():
            items.append(activiteit.get(key, ''))

    for key, datalist in codes.items():
        setattr(doc, key, datalist)

    if bag_item:
        add_bag_info(doc, bag_item)

    return doc
