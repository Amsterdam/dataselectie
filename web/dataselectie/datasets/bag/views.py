# Python
import rapidjson

from django.http import HttpResponse

from datasets.bag import models
from datasets.bag.queries import meta_q
from datasets.generic.csvexportview import CSVExportView, model_to_dict
from datasets.generic.geolocationsearchview import GeoLocationSearchView
from datasets.generic.tablesearchview import TableSearchView
from datasets.generic.tablesearchview import stringify_item_value

# TODO naam moet eruit, maar wel als zoekcriteria aanwezig blijven!
BAG_APIFIELDS = [
    'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
    'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
    'stadsdeel_naam', 'stadsdeel_code', 'postcode',
    'woonplaats', '_openbare_ruimte_naam', 'naam']


def create_geometry_dict(db_item):
    """
    Creates a geometry dict that can be used to add
    geometry information to the result set

    Returns a dict with geometry information if one
    can be created. If not, an empty dict is returned
    """
    res = {}
    try:
        geom = db_item.adresseerbaar_object.geometrie.centroid
    except AttributeError:
        geom = None
    if geom:
        # Convert to wgs
        geom_wgs = geom.transform('wgs84', clone=True).coords
        geom = geom.coords
        res = {
            'geometrie_rd_x': int(geom[0]),
            'geometrie_rd_y': int(geom[1]),
            'geometrie_wgs_lat': (
                '{:.7f}'.format(round(geom_wgs[1], 7))).replace('.', ','),
            'geometrie_wgs_lon': (
                '{:.7f}'.format(round(geom_wgs[0], 7))).replace('.', ',')
        }
    return res


class BagBase(object):
    """
    Base class mixing for data settings
    """
    model = models.Nummeraanduiding
    index = 'DS_INDEX'
    db = 'bag'
    q_func = meta_q
    apifields = BAG_APIFIELDS
    keywords = BAG_APIFIELDS
    raw_fields = ['naam', '_openbare_ruimte_naam']

    sorts = ['_openbare_ruimte_naam', 'huisnummer', 'huisletter']
    el_sorts = sorts


class BagGeoLocationSearch(BagBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, False, False)


class BagSearch(BagBase, TableSearchView):
    def elastic_query(self, query):
        return meta_q(query)

    def update_context_data(self, context):
        # Adding the buurtcombinatie, ggw, stadsdeel info to the result
        for i in range(len(context['object_list'])):
            # Making sure all the data is in string form
            context['object_list'][i].update(
                {k: stringify_item_value(v) for k, v in
                 context['object_list'][i].items() if not isinstance(v, str)}
            )
            # Adding the extra context
            context['object_list'][i].update(self.extra_context_data['items']
                                             [context['object_list'][i]['id']])
        context['aggs_list'] = self.extra_context_data['aggs_list']
        context['total'] = self.extra_context_data['total']
        return context

    def Send_Response(self, resp, response_kwargs):
        return HttpResponse(
            rapidjson.dumps(resp),
            content_type='application/json',
            **response_kwargs
        )


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
            ('openabre_ruimte_landelijk_id', True,
             'Openbareruimte-identificatie', True),
            ('panden', True, 'Pandidentificatie', True),
            ('verblijfsobject', True, 'Verblijfsobjectidentificatie', True),
            ('ligplaats', True, 'Ligplaatsidentificatie', True),
            ('standplaats', True, 'Standplaatsidentificatie', True),
            ('landelijk_id', True, 'Nummeraanduidingidentificatie', True))

    headers = [h[0] for h in hdrs if h[3]]
    pretty_headers = [h[2] for h in hdrs if h[3]]

    def elastic_query(self, query):
        return meta_q(query, add_aggs=False)

    def _convert_to_dicts(self, qs):
        """
        Overwriting the default conversion so that location data
        can be retrieved through the adresseerbaar_object
        and convert to wgs84
        """
        data = []
        for item in qs:

            dict_item = model_to_dict(item)

            # BAG Specific updates.
            # ------------------------
            # Adding geometry

            dict_item['oppervlakte'] = None
            dict_item['gebruiksdoel_omschrijving'] = None
            dict_item['gebruik'] = None
            if item.verblijfsobject_id:
                dict_item['oppervlakte'] = item.verblijfsobject.oppervlakte
                dict_item['gebruiksdoel_omschrijving'] = \
                    item.verblijfsobject.gebruiksdoel_omschrijving
                dict_item['gebruik'] = item.verblijfsobject.gebruik
                dict_item['verblijfsobject'] = item.verblijfsobject.landelijk_id
            elif item.ligplaats_id:
                dict_item['ligplaats'] = item.ligplaats.landelijk_id
            elif item.standplaats_id:
                dict_item['standplaats'] = item.standplaats.landelijk_id
            dict_item.update(create_geometry_dict(item))
            if 'hoofdadres' in dict_item:
                dict_item['hoofdadres'] = 'Ja' if dict_item[
                    'hoofdadres'] else 'Nee'
            # Saving the dict
            data.append(dict_item)
        return data

    def paginate(self, offset, q):
        if 'size' in q:
            del (q['size'])
        return q
