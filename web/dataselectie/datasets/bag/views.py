# Packages
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponse
# Project
from datasets.bag import models
from datasets.bag.queries import meta_q
from datasets.generic.views_mixins import CSVExportView, GeoLocationSearchView, TableSearchView


def create_geometry_dict(item):
    """
    Creates a geometry dict that can be used to add
    geometry information to the result set

    Returns a dict with geometry information if one
    can be created. If not, an empty dict is returned
    """
    res = {}
    try:
        geom_wgs = GEOSGeometry(f"POINT ({item['centroid'][0]} {item['centroid'][1]}) ", srid=4326)
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
        'buurt_naam', 'buurt_code', 'buurtcombinatie_code', 'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code', 'postcode', 'woonplaats', '_openbare_ruimte_naam', 'openbare_ruimte'
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
    hdrs = (('_openbare_ruimte_naam', True, 'Naam openbare ruimte', True),
            ('huisnummer', True, 'Huisnummer', True),
            ('huisletter', True, 'Huisletter', True),
            ('huisnummer_toevoeging', True, 'Huisnummertoevoeging', True),
            ('postcode', True, 'Postcode', True),
            ('gemeente', False, 'Woonplaats', True),
            ('stadsdeel_naam', False, 'Naam stadsdeel', True),
            ('stadsdeel_code', False, 'Code stadsdeel', True),
            ('ggw_naam', False, 'Naam gebiedsgerichtwerkengebied', True),
            ('ggw_code', False, 'Code gebiedsgerichtwerkengebied', True),
            ('buurtcombinatie_naam', True, 'Naam buurtcombinatie', True),
            ('buurtcombinatie_code', True, 'Code buurtcombinatie', True),
            ('buurt_naam', True, 'Naam buurt', True),
            ('buurt_code', True, 'Code buurt', True),
            ('bouwblok', True, 'Code bouwblok', True),
            ('geometrie_rd_x', True, 'X-coordinaat (RD)', True),
            ('geometrie_rd_y', True, 'Y-coordinaat (RD)', True),
            ('geometrie_wgs_lat', True, 'Latitude (WGS84)', True),
            ('geometrie_wgs_lon', True, 'Longitude (WGS84)', True),
            ('hoofdadres', True, 'Indicatie hoofdadres', True),
            ('gebruiksdoel_omschrijving', True, 'Gebruiksdoel', True),
            ('gebruik', True, 'Feitelijk gebruik', True),
            ('oppervlakte', True, 'Oppervlakte (m2)', True),
            ('type_desc', True, 'Objecttype', True),
            ('status', True, 'Verblijfsobjectstatus', True),
            ('openbare_ruimte_landelijk_id', True,
             'Openbareruimte-identificatie', True),
            ('panden', True, 'Pandidentificatie', True),
            ('verblijfsobject', True, 'Verblijfsobjectidentificatie', True),
            ('ligplaats', True, 'Ligplaatsidentificatie', True),
            ('standplaats', True, 'Standplaatsidentificatie', True),
            ('landelijk_id', True, 'Nummeraanduidingidentificatie', True))

    headers = [h[0] for h in hdrs if h[3]]
    pretty_headers = [h[2] for h in hdrs if h[3]]

    def elastic_query(self, query):
        return meta_q(query, False, False)

    def item_data_update(self, item):
        create_geometry_dict(item)

    def paginate(self, offset, q):
        if 'size' in q:
            del (q['size'])
        return q
