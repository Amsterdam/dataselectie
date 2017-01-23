# Python
import rapidjson
# Packages
from django.http import HttpResponse
# Project
from datasets.bag import models
from datasets.bag.queries import meta_q
from datasets.generic.view_mixins import CSVExportView
from datasets.generic.view_mixins import GeoLocationSearchView
from datasets.generic.view_mixins import TableSearchView

BAG_APIFIELDS = [
    'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
    'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
    'stadsdeel_naam', 'stadsdeel_code', 'postcode',
    'woonplaats', '_openbare_ruimte_naam', 'naam']


# TODO naam moet eruit, maar wel als zoekcriteria aanwezig blijven!


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
    geo_fields = {
        'shape': ['centroid', 'geo_polygon'],
    }


class BagGeoLocationSearch(BagBase, GeoLocationSearchView):
    def elastic_query(self, query):
        return meta_q(query, False, False)

    sorts = ['_openbare_ruimte_naam', 'huisnummer', 'huisletter',
             'huisnummer_toevoeging']


class BagSearch(BagBase, TableSearchView):
    def elastic_query(self, query):
        return meta_q(query)

    def update_context_data(self, context):
        # Adding the buurtcombinatie, ggw, stadsdeel info to the result
        for i in range(len(context['object_list'])):
            # Making sure all the data is in string form
            context['object_list'][i].update(
                {k: self._stringify_item_value(v) for k, v in
                 context['object_list'][i].items() if not isinstance(v, str)}
            )
            # Adding the extra context
            context['object_list'][i].update(self.extra_context_data['items'][
                                                 context['object_list'][i]['id']])
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
    headers = ('_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging',
               'postcode', 'gemeente', 'stadsdeel_naam', 'stadsdeel_code', 'ggw_naam', 'ggw_code',
               'buurtcombinatie_naam', 'buurtcombinatie_code', 'buurt_naam',
               'buurt_code', 'bouwblok', 'geometrie_rd_x', 'geometrie_rd_y',
               'geometrie_wgs_lat', 'geometrie_wgs_lon', 'hoofdadres',
               'gebruiksdoel_omschrijving', 'gebruik', 'oppervlakte', 'type_desc', 'status',
               'openabre_ruimte_landelijk_id', 'panden', 'verblijfsobject', 'ligplaats', 'standplaats',
               'landelijk_id')
    pretty_headers = ('Naam openbare ruimte', 'Huisnummer', 'Huisletter', 'Huisnummertoevoeging',
                      'Postcode', 'Woonplaats', 'Naam stadsdeel', 'Code stadsdeel', 'Naam gebiedsgerichtwerkengebied',
                      'Code gebiedsgerichtwerkengebied', 'Naam buurtcombinatie', 'Code buurtcombinatie', 'Naam buurt',
                      'Code buurt', 'Code bouwblok', 'X-coordinaat (RD)', 'Y-coordinaat (RD)',
                      'Latitude (WGS84)', 'Longitude (WGS84)', 'Indicatie hoofdadres', 'Gebruiksdoel',
                      'Feitelijk gebruik', 'Oppervlakte (m2)', 'Objecttype',
                      'Verblijfsobjectstatus', 'Openbareruimte-identificatie', 'Pandidentificatie',
                      'Verblijfsobjectidentificatie', 'Ligplaatsidentificatie', 'Standplaatsidentificatie',
                      'Nummeraanduidingidentificatie')

    def elastic_query(self, query):
        return meta_q(query, add_aggs=False)

    @staticmethod
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
                'geometrie_wgs_lat': ('{:.7f}'.format(geom_wgs[1])).replace('.', ','),
                'geometrie_wgs_lon': ('{:.7f}'.format(geom_wgs[0])).replace('.', ',')
            }
        return res

    def _convert_to_dicts(self, qs):
        """
        Overwriting the default conversion so that location data
        can be retrieved through the adresseerbaar_object
        and convert to wgs84
        """
        data = []
        for item in qs:
            dict_item = self._model_to_dict(item)
            # BAG Specific updates.
            # ------------------------
            # Adding geometry
            dict_item.update(self.create_geometry_dict(item))
            try:
                dict_item['hoofdadres'] = 'Ja' if dict_item['hoofdadres'] else 'Nee'
            except:
                pass
            # Saving the dict
            data.append(dict_item)
        return data

    def paginate(self, offset, q):
        if 'size' in q:
            del (q['size'])
        return q
