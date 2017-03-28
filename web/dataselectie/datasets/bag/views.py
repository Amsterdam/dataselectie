# Packages
from django.contrib.gis.geos import GEOSGeometry

from datasets.bag import models
from datasets.bag.queries import meta_q
from datasets.generic.views_mixins import CSVExportView, GeoLocationSearchView, \
    TableSearchView


def create_geometry_dict(item):
    """
    Creates a geometry dict that can be used to add
    geometry information to the result set

    Returns a dict with geometry information if one
    can be created. If not, an empty dict is returned
    """
    res = {}
    try:
        geom_wgs = GEOSGeometry(
            f"POINT ({item['centroid'][0]} {item['centroid'][1]}) ", srid=4326)
    except AttributeError:
        geom_wgs = None
    if geom_wgs:
        # Convert to wgs
        geom = geom_wgs.transform(28992, clone=True).coords
        geom_wgs = geom_wgs.coords
        res = {
            'geometrie_rd_x': int(geom[0]),
            'geometrie_rd_y': int(geom[1]),
            'geometrie_wgs_lat': (
                '{:.7f}'.format(geom_wgs[1], 7)).replace('.', ','),
            'geometrie_wgs_lon': (
                '{:.7f}'.format(geom_wgs[0], 7)).replace('.', ',')
        }
        item.update(res)


class BagBase(object):
    """
    Base class mixing for data settings
    """
    model = models.Nummeraanduiding
    index = 'DS_INDEX'
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
    raw_fields = ['naam', '_openbare_ruimte_naam']


class BagGeoLocationSearch(BagBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, False)


class BagSearch(BagBase, TableSearchView):
    def elastic_query(self, query):
        return meta_q(query)


class BagCSV(BagBase, CSVExportView):
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
        ('buurtcombinatie_naam', 'Naam buurtcombinatie'),
        ('buurtcombinatie_code', 'Code buurtcombinatie'),
        ('buurt_naam', 'Naam buurt'),
        ('buurt_code', 'Code buurt'),
        ('bouwblok', 'Code bouwblok'),
        ('geometrie_rd_x', 'X-coordinaat (RD)'),
        ('geometrie_rd_y', 'Y-coordinaat (RD)'),
        ('geometrie_wgs_lat', 'Latitude (WGS84)'),
        ('geometrie_wgs_lon', 'Longitude (WGS84)'),
        ('hoofdadres', 'Indicatie hoofdadres'),
        ('gebruiksdoel_omschrijving', 'Gebruiksdoel'),
        ('gebruik', 'Feitelijk gebruik'),
        ('oppervlakte', 'Oppervlakte (m2)'),
        ('type_desc', 'Objecttype'),
        ('status', 'Verblijfsobjectstatus'),
        ('openbare_ruimte_landelijk_id',
         'Openbareruimte-identificatie'),
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
