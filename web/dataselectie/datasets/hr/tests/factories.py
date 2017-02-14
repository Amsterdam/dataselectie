from datasets.hr.models import DataSelectie
from . import fixture_utils
from .. import models


def dataselectiehrfactory(vbobj, from_nr, to_nr):
    hrs = []
    for json in fixture_utils.JSON[from_nr:to_nr]:
        id = json['vestigingsnummer']
        hrdoc = DataSelectie.objects.get_or_create(
            id=id, api_json=json, bag_numid=vbobj.openbare_ruimte_id, bag_vbid=vbobj.landelijk_id)
        hrs.append(hrdoc)

def build_sbi_codes():
    hcat_rows = (
        ("F", "BOUWNIJVERHEID"),
        ("G", "GROOT- EN DETAILHANDEL, REPARATIE VAN AUTO’S"),
        ("H", "VERVOER EN OPSLAG")
    )

    for hcat_id, hcat_oms in hcat_rows:
        hcr = models.CBS_sbi_section(code=hcat_id, title=hcat_oms)
        hcr.save()

    subcat_rows = (
        ("42", "Grond-, water- en wegenbouw (geen grondverzet)", "F"),
        ("43", "Gespecialiseerde werkzaamheden in de bouw", "F"),
        ("45", "Handel in en reparatie van auto's, motorfietsen en aanhangers", "G"),
        ("46", "Groothandel en handelsbemiddeling (niet in auto's en motorfietsen)", "G"),
        ("47", "Detailhandel (niet in auto's)", "G")
    )

    for scat, scat_oms, hcat_id in subcat_rows:
        subcat = models.CBS_sbi_rootnode(
            code=scat, title=scat_oms, section_id=hcat_id)
        subcat.save()

    sbicode_rows = (
        ("421","Bouw van wegen, spoorwegen en kunstwerken","42","22274_12_22218_11"),
        ("4211","Wegenbouw en stratenmaken","42","22274_12_22218_11"),
        ("42111","Wegenbouw","42","22274_12_22218_11"),
        ("42112","Stratenmaken","42","22274_12_22218_11"),
        ("4212","Bouw van boven- en ondergrondse spoorwegen","42","22274_12_22218_11"),
        ("432",
        "Bouwinstallatie",
        "43",
        "22274_12_22219_11" ),
        ("4321",
        "Elektrotechnische bouwinstallatie",
        "43",
        "22274_12_22219_11" ),
        ("4322",
        "Loodgieters- en fitterswerk, installatie van sanitair en van verwarmings- en luchtbehandelingsapparatuur",
        "43",
        "22274_12_22219_11" ),
        ("43221",
        "Loodgieters- en fitterswerk, installatie van sanitair",
        "43",
        "22274_12_22219_11" ),
        ("43222",
        "Installatie van verwarmings- en luchtbehandelingsapparatuur",
        "43",
        "22274_12_22219_11"),
        ("451",
        "Handel in auto's en aanhangers, eventueel gecombineerd met reparatie",
        "45",
        "22272_12_22208_11" ),
        ("4511",
        "Handel in en reparatie van personenauto's en lichte bedrijfsauto's",
        "45",
        "22272_12_22208_11" ),
        ("45111",
        "Import van nieuwe personenauto’s en lichte bedrijfsauto's",
        "45",
        "22272_12_22208_11" ),
        ("45112",
        "Handel in en reparatie van personenauto’s en lichte bedrijfswagens (geen import van nieuwe)",
        "45",
        "22272_12_22208_11"),
        ("471",
        "Supermarkten, warenhuizen en dergelijke winkels met een algemeen assortiment",
        "47",
        "22272_12_22207_11" ),
        ("4711",
        "Supermarkten en dergelijke winkels met een algemeen assortiment voedings- en genotmiddelen",
        "47",
        "22272_12_22207_11" ),
        ("4719",
        "Warenhuizen en dergelijke winkels met een algemeen assortiment non-food",
        "47",
        "22272_12_22207_11" ),
        ("47191",
        "Warenhuizen",
        "47",
        "22272_12_22207_11" ),
        ("47192",
        "Winkels met een algemeen assortiment non-food (geen warenhuizen)",
        "47",
        "22272_12_22207_11")
    )
    for sbicode, sbi_oms, root_node_id, subcat_id in sbicode_rows:
        c = models.CBS_sbicode(sbi_code=sbicode, title=sbi_oms, root_node_id=root_node_id)
        c.save()
