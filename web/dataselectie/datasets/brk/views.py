import authorization_levels
from rest_framework.status import HTTP_403_FORBIDDEN

from datasets.brk.queries import meta_q
from datasets.brk import models, geo_models, filters, serializers

from datasets.generic.views_mixins import CSVExportView
from datasets.generic.views_mixins import TableSearchView

from django.core.exceptions import PermissionDenied
from django.contrib.gis.db.models import Collect
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response


SRID_WSG84 = 4326
SRID_RD = 28992


class BrkBase(object):
    """
    Base class mixing for data settings
    """
    model = models.KadastraalObject
    index = 'DS_BRK_INDEX'
    db = 'brk'
    q_func = meta_q
    keywords = [
        'buurt_naam', 'buurt_code', 'wijk_code',
        'wijk_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code',
        'verblijfsobject_postcode', 'woonplaats',
        'verblijfsobject_openbare_ruimte_naam', 'eerste_adres'
    ]
    keyword_mapping = {
    }
    raw_fields = []


class BrkGeoLocationSearch(BrkBase, generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        if not request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            return Response(status=HTTP_403_FORBIDDEN)
        output = None
        zoom = self.request.query_params.get('zoom')
        try:
            zoom = int(zoom)
            if zoom > 12:
                if 'bbox' not in request.query_params:
                    return Response("Bounding box required at this zoomlevel",
                                    status=status.HTTP_400_BAD_REQUEST)
                # Todo: gaurd against having too large a bbox ?
                output = self.get_zoomed_in()
        except:
            pass

        if output is None:
            # make queryparams on underlying request-object mutable:
            request._request.GET = request.query_params.copy()
            # then change them, so that modifications can be accessed by the filter:
            self._prepare_queryparams_for_zoomed_out(request.query_params)
            output = self.get_zoomed_out()

        serialize = serializers.BrkGeoLocationSerializer(output)
        return Response(serialize.data)

    def _prepare_queryparams_for_zoomed_out(self, query_params):
        if 'eigenaar' not in query_params:
            query_params['eigenaar'] = 9
        if 'categorie' not in query_params:
            query_params['categorie'] = 99

        if 'buurt' in query_params:
            query_params.pop('wijk', None)
            query_params.pop('ggw', None)
            query_params.pop('stadsdeel', None)
        if 'wijk' in query_params:
            query_params.pop('ggw', None)
            query_params.pop('stadsdeel', None)
        if 'ggw' in query_params:
            query_params.pop('stadsdeel', None)

        if not any(key in query_params for key in ['buurt', 'wijk', 'ggw', 'stadsdeel']):
            try:
                zoom = int(query_params['zoom'])
            except:
                zoom = 0

            # keep zoom between 8 and 12
            query_params['zoom'] = max(8, min(zoom, 12))
        else:
            query_params['zoom'] = None

    def filter(self, model):
        self.filter_class = filters.filter_class[model]
        return self.filter_queryset(model.objects)

    def get_zoomed_in(self):
        appartementen = self.filter(geo_models.Appartementen).all()

        perceel_queryset = self.filter(geo_models.EigenPerceel)
        eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        perceel_queryset = self.filter(geo_models.NietEigenPerceel)
        niet_eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        return {"appartementen": appartementen,
                "eigenpercelen": eigenpercelen['geom'],
                "niet_eigenpercelen": niet_eigenpercelen['geom']}

    def get_zoomed_out(self):
        appartementen = []

        perceel_queryset = self.filter(geo_models.EigenPerceelGroep)
        eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        perceel_queryset = self.filter(geo_models.NietEigenPerceelGroep)
        niet_eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        return {"appartementen": appartementen,
                "eigenpercelen": eigenpercelen['geom'],
                "niet_eigenpercelen": niet_eigenpercelen['geom']}


class BrkSearch(BrkBase, TableSearchView):
    def handle_request(self, request, *args, **kwargs):
        if not request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            raise PermissionDenied("scope BRK/RSN required")
        return super().handle_request(request, *args, **kwargs)

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

    def handle_request(self, request, *args, **kwargs):
        if not request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            raise PermissionDenied("scope BRK/RSN required")
        return super().handle_request(request, *args, **kwargs)

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
