# Packages
from datasets.bag import models
from datasets.bag.queries import meta_q

from datasets.generic.views_mixins import CSVExportView, create_geometry_dict
from datasets.generic.views_mixins import GeoLocationSearchView
from datasets.generic.views_mixins import TableSearchView


class BagBase(object):
    """
    Base class mixing for data settings
    """
    model = models.Nummeraanduiding
    index = 'DS_BAG_INDEX'
    db = 'bag'
    q_func = meta_q
    keywords = [
        'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
        'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code', 'postcode', 'woonplaats',
        '_openbare_ruimte_naam', 'openbare_ruimte'
    ]
    keyword_mapping = {
        'openbare_ruimte': 'naam',
    }
    raw_fields = []


class BagGeoLocationSearch(BagBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, False)


class BagSearch(BagBase, TableSearchView):
    def elastic_query(self, query):
        return meta_q(query)


class BagCSV(BagBase, CSVExportView):
    """
    Output CSV
    """
    fields_and_headers = (
        # Map the ES fields from Nummeraanduiding to labels
        ('_openbare_ruimte_naam', 'Naam openbare ruimte'),
        ('huisnummer', 'Huisnummer'),
        ('huisletter', 'Huisletter'),
        ('huisnummer_toevoeging', 'Huisnummertoevoeging'),
        ('postcode', 'Postcode'),
        ('woonplaats', 'Woonplaats'),
        ('stadsdeel_naam', 'Naam stadsdeel'),
        ('stadsdeel_code', 'Code stadsdeel'),
        ('ggw_naam', 'Naam gebiedsgerichtwerkengebied'),
        ('ggw_code', 'Code gebiedsgerichtwerkengebied'),
        ('buurtcombinatie_naam', 'Naam Wijk'),
        ('buurtcombinatie_code', 'Code Wijk'),
        ('buurt_naam', 'Naam buurt'),
        ('buurt_code', 'Code buurt'),
        ('bouwblok', 'Code bouwblok'),
        ('geometrie_rd_x', 'X-coordinaat (RD)'),
        ('geometrie_rd_y', 'Y-coordinaat (RD)'),
        ('geometrie_wgs_lat', 'Latitude (WGS84)'),
        ('geometrie_wgs_lon', 'Longitude (WGS84)'),
        ('type_adres', 'Type adres'),
        ('gebruiksdoel', 'Gebruiksdoel'),
        ('gebruiksdoel_woonfunctie', 'Gebruiksdoel woonfunctie'),
        ('gebruiksdoel_gezondheidszorgfunctie', 'Gebruiksdoel gezondheidszorgfunctie'),
        ('aantal_eenheden_complex', 'Aantal eenheden complex'),
        ('gebruik', 'Soort object (feitelijk gebruik)'),
        ('aantal_kamers', 'Aantal kamers'),
        ('toegang', 'Toegang'),
        ('verdieping_toegang', 'Verdieping toegang'),
        ('bouwlagen', 'Aantal bouwlagen'),
        ('hoogste_bouwlaag', 'Hoogste bouwlaag'),
        ('laagste_bouwlaag', 'Laagste bouwlaag'),
        ('oppervlakte', 'Oppervlakte (m2)'),
        ('bouwjaar', 'Oorspronkelijk bouwjaar'),
        ('pandnaam', "Naam pand"),
        ('type_woonobject', "Type woonobject"),
        ('ligging', "Ligging"),
        ('type_desc', 'Objecttype'),
        ('status', 'Verblijfsobjectstatus'),
        ('geconstateerd', 'Geconstateerd'),
        ('in_onderzoek', 'In Onderzoek'),
        ('openbare_ruimte_landelijk_id', 'Openbareruimte-identificatie'),
        ('panden', 'Pandidentificatie'),
        ('verblijfsobject', 'Verblijfsobjectidentificatie'),
        ('ligplaats', 'Ligplaatsidentificatie'),
        ('standplaats', 'Standplaatsidentificatie'),
        ('landelijk_id', 'Nummeraanduidingidentificatie')
    )

    field_names = [h[0] for h in fields_and_headers]
    csv_headers = [h[1] for h in fields_and_headers]

    def elastic_query(self, query):
        return meta_q(query, False, False)

    def item_data_update(self, item, request):
        create_geometry_dict(item)
        return item

    def paginate(self, offset, q):
        if 'size' in q:
            del (q['size'])
        return q
