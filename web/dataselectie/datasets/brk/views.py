from django.contrib.gis.db.models import Collect
from django.contrib.gis.geos import Polygon
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_gis import fields
from rest_framework_gis.filters import GeometryFilter
from rest_framework_gis.filterset import GeoFilterSet

from datasets.bag import models as bag_models
from datasets.bag.queries import meta_q
from datasets.brk import geo_models
from datasets.brk import models
from datasets.generic.views_mixins import CSVExportView
from datasets.generic.views_mixins import TableSearchView

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
        'buurt_naam', 'buurt_code', 'buurtcombinatie_code',
        'buurtcombinatie_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code', 'postcode', 'woonplaats',
        '_openbare_ruimte_naam', 'openbare_ruimte'
    ]
    keyword_mapping = {
        'openbare_ruimte': 'naam',
    }
    raw_fields = []


class BrkGeoFilter(GeoFilterSet):
    location = GeometryFilter(name='geometrie', lookup_expr='intersects')
    bbox = filters.CharFilter(method='filter_bbox')
    categorie = filters.NumberFilter(method='filter_categorie')

    buurt = filters.CharFilter(method='filter_gebied')
    wijk = filters.CharFilter(method='filter_gebied')
    ggw = filters.CharFilter(method='filter_gebied')
    stadsdeel = filters.CharFilter(method='filter_gebied')

    class Meta:
        fields = ('categorie', 'location', 'bbox', 'buurt', 'wijk', 'ggw', 'stadsdeel')

    def filter_categorie(self, queryset, name, value):
        if value is not None:
            queryset = queryset.filter(cat_id=value)
        return queryset

    def filter_bbox(self, queryset, name, value):
        if value:
            try:
                points = (float(n) for n in value.split(','))
                box = Polygon.from_bbox(points)
                box.srid = SRID_WSG84
                box.transform(SRID_RD)
                return queryset.filter(geometrie__intersects=box)
            except ValueError:
                    pass

        return queryset

    def filter_gebied(self, queryset, name, value):
        # get applicable model for parameter-name:
        gebiedsmodel = {"wijk": bag_models.Buurtcombinatie, "ggw": bag_models.Gebiedsgerichtwerken,
                        "stadsdeel": bag_models.Stadsdeel, "buurt": bag_models.Buurt}[name]
        try:
            gebied = gebiedsmodel.objects.get(pk=value)
            return queryset.filter(geometrie__intersects=gebied.geometrie)
        except gebiedsmodel.DoesNotExist:
            return queryset


class AppartementenFilter(BrkGeoFilter):
    class Meta(BrkGeoFilter.Meta):
        model = geo_models.Appartementen


class EigenPerceelFilter(BrkGeoFilter):
    class Meta(BrkGeoFilter.Meta):
        model = geo_models.EigenPerceel


class NietEigenPerceelFilter(BrkGeoFilter):
    class Meta(BrkGeoFilter.Meta):
        model = geo_models.NietEigenPerceel


class BrkAppartementenSerializer(serializers.Serializer):
    aantal = serializers.IntegerField()
    geometrie = fields.GeometryField()

    class Meta:
        model = geo_models.Appartementen
        inlcude_fields = ('aantal', 'geometrie')


class BrkGeoLocationSerializer(serializers.Serializer):
    appartementen = BrkAppartementenSerializer(many=True)
    eigenpercelen = fields.GeometryField()
    niet_eigenpercelen = fields.GeometryField()

    class Meta:
        inlcude_fields = ('appartementen', 'eigenpercelen', 'niet_eigenpercelen')


class BrkGeoLocationSearch(BrkBase, generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        zoom = self.request.query_params.get('zoom')
        try:
            zoom = int(zoom)
            if zoom > 12 and zoom < 17:
                # Todo: gaurd against omitting bbox, or having too large a bbox
                return self.get_zoomed_in()
        except:
            pass

        return self.get_zoomed_out()

    def get_zoomed_in(self):
        self.filter_class = AppartementenFilter
        appartementen = self.filter_queryset(geo_models.Appartementen.objects).all()

        self.filter_class = EigenPerceelFilter
        queryset = self.filter_queryset(geo_models.EigenPerceel.objects)
        eigenpercelen = queryset.aggregate(geom=Collect('geometrie'))

        self.filter_class = NietEigenPerceelFilter
        queryset = self.filter_queryset(geo_models.NietEigenPerceel.objects)
        niet_eigenpercelen = queryset.aggregate(geom=Collect('geometrie'))

        output = {"appartementen": appartementen,
                  "eigenpercelen": eigenpercelen['geom'],
                  "niet_eigenpercelen": niet_eigenpercelen['geom']}
        serialize = BrkGeoLocationSerializer(output)

        return Response(serialize.data)

    def get_zoomed_out(self):
        return Response([])


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
