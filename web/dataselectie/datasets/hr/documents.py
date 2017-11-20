# Python
import logging

import elasticsearch_dsl as es
from elasticsearch_dsl import analysis

from django.conf import settings

from datasets.bag.models import Nummeraanduiding
from datasets.hr.models import DataSelectie

log = logging.getLogger(__name__)


edge_ngram_filter = analysis.token_filter(
    'edge_ngram_filter',
    type='edge_ngram',
    min_gram=1,
    max_gram=15
)


autocomplete = es.analyzer(
    'autocomplete',
    tokenizer='standard',
    filter=['lowercase', edge_ngram_filter]
)


class Inschrijving(es.DocType):
    """
    Elastic data of 'vestigingen' or 'mac'
    from handelsregister
    """
    maatschappelijke_activiteit_id = es.Keyword()
    vestiging_id = es.Keyword()

    dataset = es.Keyword()

    kvk_nummer = es.Keyword()
    handelsnaam = es.Keyword()
    datum_aanvang = es.Date()
    eigenaar_naam = es.Keyword()
    eigenaar_id = es.Keyword()
    non_mailing = es.Boolean()

    aantal_werkzame_personen = es.Integer()
    rechtsvorm = es.Keyword()

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
    sbi_code = es.String(
        multi=True,
        fielddata=True,
        analyzer=autocomplete,
    )

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


def add_adres_to_doc(doc, inschrijving):

    # Address
    for address_type in ('bezoekadres', 'postadres'):
        adres = inschrijving.get(address_type)
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
            bucket.append(": ".join(level_omschrijving))

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
    doc.rechtsvorm = eigenaar.get('rechtsvorm', '')

    if eigenaar.get('faillissement'):
        doc.bijzondere_rechtstoestand = 'Faillissement'
    elif eigenaar.get('status', ''):
        # YES status is a bad variable name..
        # any text in status means 'in Surseance'
        doc.bijzondere_rechtstoestand = 'Surseance van betaling'
    else:
        # The 'geen' categorie.
        doc.bijzondere_rechtstoestand = ''

    # bijzondere rechtstoestand
    # doc.reden_insolvatie = eigenaar.get('reden_insolvatie', '')
    # doc.duur = eigenaar.get('reden_insolvatie', '')


def jsonpprint(data):
    import json
    print(json.dumps(data, sort_keys=True, indent=4))


def _handle_mac_information(doc, mac):
    for attrib in (
            'kvk_nummer', 'datum_aanvang',
            'non_mailing'):
        setattr(doc, attrib, mac.get(attrib, ''))


def _handle_onderneming(doc, inschrijving):
    """
    extract werkzame personen
    """

    onderneming = inschrijving.get('ondernemeing')

    if onderneming:
        doc.aantal_werkzame_personen = onderneming.get(
            'totaal_werkzame_personen')


def _handle_commerciele_vestiging(doc, inschrijving):
    """
    extract werkzame personen
    """

    com_ves = inschrijving.get('commerciele_vestiging')

    if com_ves:
        doc.aantal_werkzame_personen = com_ves.get(
            'totaal_werkzame_personen')


def _handle_ves_fields(doc, inschrijving):

    if not doc.dataset == 'ves':
        return

    mac = inschrijving['maatschappelijke_activiteit']
    set_eigenaar_to_doc(doc, mac['eigenaar'])
    # Using Vestiging name, otherwise,
    # maatschappelijke_activiteit name, otherwise empty
    doc.handelsnaam = inschrijving.get('naam', mac.get('naam', '')).strip()

    # Maatschapelijke activiteit in case of ves
    mac = inschrijving.get('maatschappelijke_activiteit')
    _handle_mac_information(doc, mac)

    _handle_commerciele_vestiging(doc, inschrijving)


def _handle_mac_fields(doc, inschrijving):

    if not doc.dataset == 'mac':
        return

    set_eigenaar_to_doc(doc, inschrijving)
    doc.maatschappelijke_activiteit_id = inschrijving.get('id', '')
    doc.handelsnaam = inschrijving.get('naam', '').strip()
    # Maatschapelijke activiteit in case of mac
    _handle_mac_information(doc, inschrijving)

    _handle_onderneming(doc, inschrijving)


def inschrijving_from_hrdataselectie(
        ds_record: DataSelectie,
        bag_item: Nummeraanduiding) -> Inschrijving:
    """
    Create inschrijving document dataselectie json data.
    """

    inschrijving = ds_record.api_json
    _id = inschrijving.get('id') or inschrijving['vestigingsnummer']
    dataset = inschrijving['dataset']
    doc = Inschrijving(_id=f"{dataset}{_id}")
    doc.dataset = dataset
    doc.bag_numid = ds_record.bag_numid

    # Working with the json
    doc.vestiging_id = inschrijving.get('vestigingsnummer', '')

    _handle_ves_fields(doc, inschrijving)
    _handle_mac_fields(doc, inschrijving)

    add_adres_to_doc(doc, inschrijving)
    add_sbi_to_doc(doc, inschrijving)

    if bag_item:
        add_bag_info(doc, bag_item)

    return doc
