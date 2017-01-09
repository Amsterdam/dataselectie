
from .. import models
from . import fixture_utils


def dataselectiehrfactory(vbobj, from_nr, to_nr):
    hrs = []
    for json in fixture_utils.JSON[from_nr:to_nr]:
        id = json['vestigingsnummer']
        hrdoc = models.DataSelectie.objects.get_or_create(id=id, api_json = json,
                                                          bag_numid=vbobj.landelijk_id, bag_vbid = vbobj.openbare_ruimte_id)
        hrs.append(hrdoc)
    return hrs


def dataselectiesbicodefactory():
    hc = (
            ("22272_12", "handel, vervoer, opslag"),
            ("22273_12", "productie, installatie, reparatie"),
            ("22274_12", "bouw"),
            ("22275_12", "landbouw"),
            ("22276_12", "horeca"),
            ("22277_12", "informatie, telecommunicatie"),
            ("22278_12", "financiële dienstverlening,verhuur van roerend en onroerend goed"),
            ("22279_12", "zakelijke dienstverlening"),
            ("22280_12", "overheid, onderwijs, zorg"),
            ("22281_12", "cultuur, sport, recreatie"),
            ("22282_12", "persoonlijke dienstverlening"),
            ("22283_12", "overige niet hierboven genoemd")
    )
    for c,o in hc:
        m = models.CBS_sbi_hoofdcat(c, o)
        m.save()

    sc = (
        ("22272_12_22207_11", "detailhandel (verkoop aan consumenten, niet zelf vervaardigd)", "22272_12"),
        ("22272_12_22208_11", "handel en reparatie van auto s", "22272_12"),
        ("22272_12_22209_11", "groothandel (verkoop aan andere ondernemingen, niet zelf vervaardigd)", "22272_12"),
        ("22272_12_22210_11", "handelsbemiddeling (tussenpersoon, verkoopt niet zelf)", "22272_12"),
        ("22272_12_22211_11", "vervoer", "22272_12"),
        ("22272_12_22212_11", "opslag", "22272_12"),
        ("22272_12_22213_11", "dienstverlening vervoer", "22272_12"),
        ("22273_12_22214_11", "productie", "22273_12"),
        ("22273_12_22215_11", "installatie (geen bouw)", "22273_12"),
        ("22273_12_22216_11", "reparatie (geen bouw)", "22273_12"),
        ("22274_12_22217_11", "bouw/utiliteitsbouw algemeen", "22274_12"),
        ("22274_12_22218_11", "grond, water, wegenbouw", "22274_12"),
        ("22274_12_22219_11", "bouwinstallatie", "22274_12"),
        ("22274_12_22220_11", "afwerking van gebouwen", "22274_12"),
        ("22274_12_22221_11", "dak- en overige gespecialiseerde bouw", "22274_12"),
        ("22274_12_22222_11", "klussenbedrijf", "22274_12"),
        ("22274_12_22223_11", "bouw overig", "22274_12"),
        ("22275_12_22224_11", "teelt eenjarige gewassen", "22275_12"),
        ("22275_12_22225_11", "teelt meerjarige gewassen", "22275_12"),
        ("22275_12_22226_11", "teelt sierplanten", "22275_12"),
        ("22275_12_22227_11", "fokken, houden dieren", "22275_12"),
        ("22275_12_22228_11", "gemengd bedrijf", "22275_12"),
        ("22275_12_22229_11", "dienstverlening voor de land/tuinbouw", "22275_12"),
        ("22276_12_22230_11", "hotel-restaurant", "22276_12"),
        ("22276_12_22231_11", "hotel, pension", "22276_12"),
        ("22276_12_22232_11", "restaurant, café-restaurant", "22276_12"),
        ("22276_12_22233_11", "cafetaria, snackbar, ijssalon", "22276_12"),
        ("22276_12_22234_11", "café", "22276_12"),
        ("22276_12_22235_11", "kantine, catering", "22276_12"),
        ("22276_12_22236_11", "overig, te weten", "22276_12"),
        ("22277_12_22237_11", "uitgeverijen", "22277_12"),
        ("22277_12_22238_11", "activiteiten  op gebied van film, tv, radio, audio", "22277_12"),
        ("22277_12_22239_11", "telecommunicatie", "22277_12"),
        ("22277_12_22240_11", "activiteiten op het gebied van ict", "22277_12"),
        ("22278_12_22241_11", "financiële dienstverlening en verzekeringen", "22278_12"),
        ("22278_12_22242_11", "holdings", "22278_12"),
        ("22278_12_22243_11", "verhuur van- en beheer/handel in onroerend goed", "22278_12"),
        ("22278_12_22244_11", "verhuur van roerende goederen", "22278_12"),
        ("22279_12_22245_11", "public relationsbureaus", "22279_12"),
        ("22279_12_22246_11", "managementadvies, economisch advies", "22279_12"),
        ("22279_12_22247_11", "advocaten rechtskundige diensten, notarissen", "22279_12"),
        ("22279_12_22248_11", "accountancy, administratie", "22279_12"),
        ("22279_12_22249_11", "architecten", "22279_12"),
        ("22279_12_22250_11", "interieurarchitecten", "22279_12"),
        ("22279_12_22251_11", "technisch ontwerp, advies, keuring/research", "22279_12"),
        ("22279_12_22252_11", "arbeidsbemiddeling, uitzendbureaus, uitleenbureaus", "22279_12"),
        ("22279_12_22253_11", "reclame en marktonderzoek", "22279_12"),
        ("22279_12_22254_11", "design", "22279_12"),
        ("22279_12_22255_11", "overige zakelijke dienstverlening", "22279_12"),
        ("22280_12_22256_11", "overheid", "22280_12"),
        ("22280_12_22257_11", "onderwijs", "22280_12"),
        ("22280_12_22258_11", "gezondheids- en welzijnszorg", "22280_12"),
        ("22281_12_22259_11", "kunst", "22281_12"),
        ("22281_12_22260_11", "musea, bibliotheken, kunstuitleen", "22281_12"),
        ("22281_12_22261_11", "sport", "22281_12"),
        ("22281_12_22262_11", "recreatie", "22281_12"),
        ("22282_12_22263_11", "kappers", "22282_12"),
        ("22282_12_22264_11", "schoonheidsverzorging", "22282_12"),
        ("22282_12_22265_11", "sauna, solaria", "22282_12"),
        ("22282_12_22266_11", "uitvaart, crematoria", "22282_12"),
        ("22282_12_22267_11", "overige dienstverlening", "22282_12"),
        ("22283_12_22268_11", "belangenorganisaties", "22283_12"),
        ("22283_12_22269_11", "idieële organisaties", "22283_12"),
        ("22283_12_22270_11", "hobbyclubs", "22283_12"),
        ("22283_12_22271_11", "overige", "22283_12")
        )
    for c, o, r in sc:
        m = models.CBS_sbi_subcat(c, o, r)
        m.save()
