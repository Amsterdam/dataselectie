from data.models import DataSelectie
from . import fixture_utils
from .. import models


def dataselectiehrfactory(vbobj, from_nr, to_nr):
    hrs = []
    for json in fixture_utils.JSON[from_nr:to_nr]:
        id = json['vestigingsnummer']
        hrdoc = DataSelectie.objects.get_or_create(
            id=id, api_json=json, bag_numid=vbobj.landelijk_id, bag_vbid=vbobj.openbare_ruimte_id)
        hrs.append(hrdoc)

    hcat_rows = (
        ("22272_12", "handel, vervoer, opslag"),
        ("22281_12", "cultuur, sport, recreatie"),
        ("22280_12", "Onderwijs")
    )

    for hcat_id, hcat_oms in hcat_rows:
        hcr = models.CBS_sbi_hoofdcat(hcat=hcat_id, hoofdcategorie=hcat_oms)
        hcr.save()

    subcat_rows = (
        ("22272_12_22209_11", "groothandel (verkoop aan andere ondernemingen, niet zelf vervaardigd)", "22272_12"),
        ("22281_12_22259_11", "kunst", "22281_12"),
        ("22281_12_22260_11", "musea, bibliotheken, kunstuitleen", "22281_12"),
        ("22281_12_22261_11", "sport", "22281_12"),
        ("22281_12_22262_11", "recreatie", "22281_12"),
        ("22280_12_22257_11", "onderwijs", "22280_12")
    )
    for scat, scat_oms, hcat_id in subcat_rows:
        subcat = models.CBS_sbi_subcat(
            scat=scat, subcategorie=scat_oms, hcat_id=hcat_id)
        subcat.save()

    sbicode_rows = (
        ("46211", "Groothandel in granen", "22272_12_22209_11"),
        ("46212", "Groothandel in zaden, pootgoed en peulvruchten", "22272_12_22209_11"),
        ("46213", "Groothandel in hooi, stro en ruwvoeder", "22272_12_22209_11"),
        ("46214", "Groothandel in meng- en krachtvoeder", "22272_12_22209_11"),
        ("46215", "Groothandel in veevoeder (geen ruw-, meng- en krachtvoeder)", "22272_12_22209_11"),
        ("46216", "Groothandel in ruwe plantaardige en dierlijke oliën en vetten en oliehoudende grondstoffen",
         "22272_12_22209_11"),
        ("46217", "Groothandel in ruwe tabak", "22272_12_22209_11"),
        ("46218", "Groothandel in akkerbouwproducten en veevoeder algemeen assortiment", "22272_12_22209_11"),
        ("46219", "Groothandel in overige akkerbouwproducten", "22272_12_22209_11"),
        ("4622", "Groothandel in bloemen en planten", "22272_12_22209_11"),
        ("9002", "Dienstverlening voor uitvoerende kunsten", "22281_12_22259_11"),
        ("9003", "Schrijven en overige scheppende kunsten", "22281_12_22259_11"),
        ("91019", "Overige culturele uitleencentra en openbare archieven", "22281_12_22260_11"),
        ("91021", "Musea", "22281_12_22260_11"),
        ("93125", "Paardensport en maneges", "22281_12_22261_11"),
        ("93126", "Wielersport", "22281_12_22261_11"),
        ("5530", "Kampeerterreinen", "22281_12_22262_11"),
        ("85314", "Brede scholengemeenschappen voor voortgezet onderwijs", "22280_12_22257_11")
    )
    for sbicode, sbi_oms, subcat_id in sbicode_rows:
        c = models.CBS_sbicodes(sbi_code=sbicode, sub_sub_categorie=sbi_oms, scat_id=subcat_id)
        c.save()
