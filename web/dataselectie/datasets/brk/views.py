from datasets.brk import models
from datasets.bag.queries import meta_q

from datasets.generic.views_mixins import CSVExportView
from datasets.generic.views_mixins import GeoLocationSearchView
from datasets.generic.views_mixins import TableSearchView


class BrkBase(object):
    """
    Base class mixing for data settings
    """
    model = models.KadastraalObject
    index = 'DS_BRK_INDEX'
    db = 'brk'
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


class BrkGeoLocationSearch(BrkBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, False)


class BrkSearch(BrkBase, TableSearchView):
    def elastic_query(self, query):
        return meta_q(query)


class BrkCSV(BrkBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    fields_and_headers = (
        ('_openbare_ruimte_naam', 'Naam openbare ruimte'),
        ('huisnummer', 'Huisnummer'),
        ('huisletter', 'Huisletter'),
        ('huisnummer_toevoeging', 'Huisnummertoevoeging'),
        ('postcode', 'Postcode'),
        ('gemeente', 'Woonplaats'),
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
        ('hoofdadres', 'Indicatie hoofdadres'),
        ('gebruiksdoelen', 'Gebruiksdoelen'),
        ('gebruik', 'Feitelijk gebruik'),
        ('oppervlakte', 'Oppervlakte (m2)'),
        ('type_desc', 'Objecttype'),
        ('status', 'Verblijfsobjectstatus'),
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
        # create_geometry_dict(item)
        return item

    def paginate(self, offset, q):
        if 'size' in q:
            del (q['size'])
        return q
