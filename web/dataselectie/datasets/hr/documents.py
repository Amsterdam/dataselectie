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
    vestiging_id = es.Keyword()
    kvk_nummer = es.Keyword()
    handelsnaam = es.Keyword()
    datum_aanvang = es.Date()
    datum_einde = es.Date()
    eigenaar_naam = es.Keyword()
    eigenaar_id = es.Keyword()
    non_mailing = es.Boolean()

    # Address information
    bezoekadres_volledig_adres = es.Keyword()
    bezoekadres_correctie = es.Boolean()
    bezoekadres_afgeschermd = es.Boolean()
    bezoekadres_openbare_ruimte = es.Keyword()
    bezoekadres_huisnummer = es.Integer()
    bezoekadres_huisletter = es.Keyword()
    bezoekadres_huisnummertoevoeging = es.Keyword()
    bezoekadres_postcode = es.Keyword()
    bezoekadres_plaats = es.Keyword()

    bezoekadres_buurt_code = es.Keyword()
    bezoekadres_buurt_naam = es.Keyword()
    bezoekadres_buurtcombinatie_code = es.Keyword()
    bezoekadres_buurtcombinatie_naam = es.Keyword()
    bezoekadres_ggw_code = es.Keyword()
    bezoekadres_ggw_naam = es.Keyword()
    bezoekadres_gsg_naam = es.Keyword()
    bezoekadres_stadsdeel_code = es.Keyword()
    bezoekadres_stadsdeel_naam = es.Keyword()

    postadres_volledig_adres = es.Keyword()
    postadres_correctie = es.Boolean()
    postadres_afgeschermd = es.Boolean()
    postadres_openbare_ruimte = es.Keyword()
    postadres_huisnummer = es.Integer()
    postadres_huisletter = es.Keyword()
    postadres_huisnummertoevoeging = es.Keyword()
    postadres_postcode = es.Keyword()
    postadres_plaats = es.Keyword()

    # And the bag numid
    bag_numid = es.Keyword()
    centroid = es.GeoPoint()

    # Categores
    hoofdcategorie = es.Keyword(multi=True)
    subcategorie = es.Keyword(multi=True)
    # SBI codes
    sbi_code = es.Keyword(multi=True)
    sbi_omschrijving = es.Keyword(multi=True)

    sbi_l1 = es.Keyword(multi=True)
    sbi_l2 = es.Keyword(multi=True)
    sbi_l3 = es.Keyword(multi=True)
    sbi_l4 = es.Keyword(multi=True)
    sbi_l5 = es.Keyword(multi=True)

    # bijzondere rechtstoestand

    # status = es.Keyword()

    bijzondere_rechtstoestand = es.Keyword()

    class Meta:
        all = es.MetaField(enabled=False)
        doc_type = 'vestiging'
        index = settings.ELASTIC_INDICES['DS_HR_INDEX']


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


def add_bag_info(doc, ves):
    """
    Adding bag information
    """
    adresseerbaar_object = ves.adresseerbaar_object
    # If there is no adresseerbaar_object there is no
    # point to continue
    if not adresseerbaar_object:
        return

    # Adding geolocation
    try:
        geom = adresseerbaar_object.geometrie
        doc.centroid = geom.centroid.transform('wgs84', clone=True).coords
    except AttributeError:
        log.error('Missing geometrie %s', adresseerbaar_object)

    # Adding the ggw data
    ggw = adresseerbaar_object._gebiedsgerichtwerken   # noqa
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


def add_adres_to_doc(doc, ves_data):

    # Address
    for address_type in ('bezoekadres', 'postadres'):
        adres = ves_data[address_type]
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


def _log_sbi_error(doc, activiteit):

    log.error("""

    No sbi information for activiteit:
    %s
    %s
    %s

        """, doc.handelsnaam, activiteit, doc.vestiging_id)


def add_sbi_to_doc(doc, ves_data):
    """
    Add sbi information to doc

    levels and qa tree
    """
    # SBI codes, categories and subcategories
    # Creating lists of the values and then setting
    # the document

    codes = {
        'hoofdcategorie': [],
        'subcategorie': [],

        'sbi_code': [],
        'sbi_omschrijving': [],
    }

    levels = {
        'l1': [],    # will be added as sbi_l1 in doc..etc
        'l2': [],
        'l3': [],
        'l4': [],
        'l5': [],
    }

    for activiteit in ves_data['activiteiten']:
        # Flattening the sbi information
        activiteit, error = flatten_sbi(activiteit)

        if error:
            _log_sbi_error(doc, activiteit)

        for key, bucket in codes.items():
            bucket.append(activiteit.get(key, ''))

        # extract levels
        sbi_tree = activiteit.get('sbi_tree', {})

        for key, bucket in levels.items():
            if not sbi_tree:
                continue
            level_omschrijving = sbi_tree.get(key, [])
            if not level_omschrijving:
                continue
            bucket.append("-".join(level_omschrijving))

    for key, datalist in codes.items():
        setattr(doc, key, datalist)

    for key, datalist in levels.items():
        # add sbi_lx keys
        setattr(doc, 'sbi_%s' % key, datalist)


def set_eigenaar_to_doc(doc, eigenaar):
    """
    Set eigenaar information to doc
    """

    doc.eigenaar_naam = eigenaar.get('volledige_naam', '')
    doc.eigenaar_id = eigenaar.get('id', '')

    if eigenaar.get('faillissement'):
        doc.bijzondere_rechtstoestand = 'Failliet'
    elif eigenaar.get('status', ''):
        doc.bijzondere_rechtstoestand = 'Surseance'
    else:
        # The 'geen' categorie.
        doc.bijzondere_rechtstoestand = ''

    # bijzondere rechtstoestand
    # doc.reden_insolvatie = eigenaar.get('reden_insolvatie', '')
    # doc.duur = eigenaar.get('reden_insolvatie', '')


def jsonpprint(data):
    import json
    print(json.dumps(data, sort_keys=True, indent=4))


def vestiging_from_hrdataselectie(
        ves: DataSelectie, bag_item: Nummeraanduiding) -> Vestiging:
    doc = Vestiging(_id=ves.id)  # HR is added to prevent id collisions
    """
    Create vestiging document from vesitiging json data.
    """
    doc.bag_numid = ves.bag_numid
    # Working with the json
    ves_data = ves.api_json
    # jsonpprint(ves_data)
    doc.vestiging_id = ves_data['vestigingsnummer']
    # Maatschapelijke activiteit
    mac = ves_data['maatschappelijke_activiteit']
    for attrib in (
            'kvk_nummer', 'datum_aanvang',
            'datum_einde', 'eigenaar_naam',
            'eigenaar_id', 'non_mailing'):
        setattr(doc, attrib, mac.get(attrib, ''))

    set_eigenaar_to_doc(doc, mac['eigenaar'])

    # Using Vestiging name, otherwise,
    # maatschappelijke_activiteit name, otherwise empty
    doc.handelsnaam = ves_data.get('naam', mac.get('naam', ''))

    add_adres_to_doc(doc, ves_data)
    add_sbi_to_doc(doc, ves_data)

    if bag_item:
        add_bag_info(doc, bag_item)

    return doc
