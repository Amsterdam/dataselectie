import logging
import time
from datetime import datetime, date
from decimal import Decimal
from itertools import groupby

from django import db
from django.contrib.gis.geos.point import Point

from datasets.hr.views import build_sbi_filterkeys
from datasets.data.models import DataSelectie
from datasets.hr.models import BetrokkenPersonen
from datasets.hr.models import CBS_sbi_section
from datasets.hr.models import GeoVestigingen

log = logging.getLogger(__name__)


VESTIGING_FIELDS = (
    'vestigingsnummer', 'naam', 'hoofdvestiging',
    'locatie_type', 'geometrie')

BETROKKENEN_FIELDS = (
    'mac_naam', 'rol', 'naam', 'rechtsvorm', 'functietitel',
    'soortbevoegdheid', 'bevoegde_naam')

MAATSCHAPPELIJKE_ACT_FIELDS = (
    'kvk_nummer', 'datum_aanvang', 'datum_einde')

LOCATIE_BEZOEKADRES_FIELDS = (
    'volledig_adres', 'afgeschermd')
LOCATIE_POSTADRES_FIELDS = (
    'straat_huisnummer', 'huisletter', 'huisnummer', 'huisnummertoevoeging',
    'postcode', 'straatnaam', 'postbus_nummer', 'toevoegingadres',
    'volledig_adres', 'afgeschermd')

PROGRESSREPORT = 10         # report every xx seconds


def to_dict(data: object, fields: tuple, field_prefix=None) -> dict:
    result_dict = {}
    for f in fields:
        if field_prefix:
            f_to = field_prefix + '_' + f
        else:
            f_to = f
        if data:
            value = getattr(data, f)
            if isinstance(value, Point):
                value = [value.x, value.y]
            elif isinstance(value, Decimal):
                value = str(value)
            elif isinstance(value, datetime) or isinstance(value, date):
                value = value.isoformat()
        else:
            value = ''
        result_dict[f_to] = value

    return result_dict


def _build_joined_ds_table():
    """
    De dataselectie wordt in 2 stappen geschreven. Eerst wordt de api data
    opgebouwd en in een json met een key per vestiging_id weggeschreven.

    Vervolgens wordt in dataselectie deze file gelezen en worden de
    search keys opgenomen in elastic, waardoor die doorzoekbaar wordt
    in dataselectie.
    """

    with db.connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE data_dataselectie")

    sbi_values = build_sbi_filterkeys()

    betrokken_per_vestiging = (
        BetrokkenPersonen.objects.order_by('vestigingsnummer').iterator())

    # Indien geen betrokkenen -> resultaat is None
    try:
        betrokken = next(betrokken_per_vestiging)
    except StopIteration:
        betrokken = None

    totalrowcount = GeoVestigingen.objects.filter().count()

    log.info('START opbouw dataselectie api als json:  %s', totalrowcount)

    # groupby vestigings nummer
    by_vestiging = groupby(
        GeoVestigingen.objects.order_by('vestigingsnummer'),
        lambda row: row.vestigingsnummer
    )

    count = 1
    lastreport = time.time()

    for vestigingsnummer, vest_data in by_vestiging:

        count, lastreport = measure_progress(totalrowcount, count, lastreport)

        # verzamel gegevens per vestiging
        vst_sbi, vestiging_dict, naam, bag_vbid, bag_numid = per_vestiging(
            vestigingsnummer, vest_data, sbi_values)

        # save json in ds tabel
        betrokken = write_hr_dataselectie(
            vst_sbi, betrokken, vestiging_dict,
            vestigingsnummer, betrokken_per_vestiging,
            naam, bag_vbid, bag_numid)

    log.info('Opbouw dataselectie api als json VOLTOOID')


def per_vestiging(vestigingsnummer, vest_data, sbi_values):
    """
    Read data per vestiging and build dict (to be json) per
    vestiging
    """

    first = True
    vst_sbi = []
    vestiging_dict = {}
    sbi_repeat = None
    sbi_double_check = []

    for sbi_repeat in vest_data:

        if first:
            vestiging_dict = to_dict(sbi_repeat, VESTIGING_FIELDS)
            vestiging_dict = add_adressen_dict(vestiging_dict, sbi_repeat)
            vestiging_dict['sbi_codes'] = vst_sbi = []
            first = False

        if not sbi_repeat.sbi_code in sbi_double_check:
            sbi = sbi_values[sbi_repeat.sbi_code]
            sbi['vestigingsnummer'] = vestigingsnummer
            sbi['bedrijfsnaam'] = sbi_repeat.naam
            sbi_double_check.append(sbi_repeat.sbi_code)

            vst_sbi.append(sbi)

    return (
        vst_sbi, vestiging_dict, sbi_repeat.naam,
        sbi_repeat.bezoekadres.bag_vbid, sbi_repeat.bezoekadres.bag_numid)


def write_hr_dataselectie(
        vst_sbi, betrokken, vestiging_dict, vestigingsnummer,
        betrokken_per_vestiging, naam, bag_vbid, bag_numid):

    if len(vst_sbi):
        vestiging_dict, betrokken = add_betrokkenen_to_vestigingen(
                betrokken, vestiging_dict,
                vestigingsnummer, betrokken_per_vestiging)
    else:
        log.error('Vestiging %s %s zonder sbi code' % (vestigingsnummer, naam))

    if vestiging_dict and bag_numid:
        ds = DataSelectie(
            vestigingsnummer, bag_vbid, bag_numid, vestiging_dict)
        ds.save()
    return betrokken


def measure_progress(totalrowcount, count, lastreport):
    """
    Every PROGRESSREPORT timedelta print progres line
    """
    count += 1

    if time.time() - lastreport > PROGRESSREPORT:
        lastreport = time.time()
        pct_complete = str(int((count * 100) / totalrowcount)) + '%'

        log.info('Opbouw dataselectie %s voltooid, rownr %s',
                 pct_complete, count)

    return count, lastreport


def add_adressen_dict(vestiging_dict: dict, sbi_repeat) -> dict:
    """
    Voeg bezoek- en postadressen toe als dict aan resulterende json.
    bezoekadres en postadres zijn relaties van geolocatie, de gevonden rijen
    worden vertaald naar dict. De bezoekadres gegevens worden later in
    dataselectie uit Bag opgehaald. Postadres wordt wel volledig meegegeven
    """

    vestiging_dict.update(
        to_dict(
            sbi_repeat.bezoekadres, LOCATIE_BEZOEKADRES_FIELDS, 'bezoekadres'))

    vestiging_dict['bezoekadres_correctie'] = \
        correctie_address(sbi_repeat.bezoekadres)

    vestiging_dict.update(
        to_dict(
            sbi_repeat.postadres,
            LOCATIE_POSTADRES_FIELDS, 'postadres'))

    vestiging_dict['postadres_correctie'] = \
        correctie_address(sbi_repeat.postadres)

    if vestiging_dict['postadres_correctie'] == 'BAG':
        vestiging_dict.update(
            get_bag(
                sbi_repeat.postadres,
                LOCATIE_POSTADRES_FIELDS, 'postadres'))

    return vestiging_dict

def get_bag(postadres, pa_fields, prefix):
    return {}

def correctie_address(address):
    if address and address.correctie:
        return 'BAG'
    elif address.correctie is False:
        return 'ERR'
    else:
        return 'KVK'


def add_betrokkenen_to_vestigingen(
        betrokken, vestiging_dict, vestigingsnummer,
        betrokken_per_vestiging):
    """
    Voeg betrokkenen aan vestiging toe. Let op, dit is een balanceline
    verwerking. Om de snelheid hoog te houden lees ik de betrokkenen
    per vestiging in en verwerk ze voor de vestiging waar ik mee
    bezig ben. Vergelijkbaar met een join op SQL.
    De oplossing is gekozen vanwege complexiteit (en traagheid) van
    de resulterende join in SQL tegenover de snelheid van sequentiele
    verwerking
    """

    vestiging_dict['betrokkenen'] = vst_betr = []
    for field in MAATSCHAPPELIJKE_ACT_FIELDS:
        vestiging_dict[field] = None
    first = True

    while betrokken and betrokken.vestigingsnummer <= vestigingsnummer:
        if betrokken.vestigingsnummer == vestigingsnummer:
            vst_betr.append(to_dict(betrokken, BETROKKENEN_FIELDS))
            if first:
                mac_dict = to_dict(betrokken, MAATSCHAPPELIJKE_ACT_FIELDS)
                vestiging_dict.update(mac_dict)
                first = False
            
        if betrokken.vestigingsnummer <= vestigingsnummer:
            try:
                betrokken = next(betrokken_per_vestiging)
            except StopIteration:
                break

    return vestiging_dict, betrokken
