import json

from django.contrib.gis.geos import Polygon
from django_filters import rest_framework as filters
from rest_framework_gis.filters import GeometryFilter
from rest_framework_gis.filterset import GeoFilterSet

from datasets.bag import models as bag_models
from datasets.brk import geo_models

SRID_WSG84 = 4326
SRID_RD = 28992


class BrkGeoFilter(GeoFilterSet):
    shape = filters.CharFilter(method='filter_shape')
    bbox = filters.CharFilter(method='filter_bbox')
    categorie = filters.NumberFilter(method='filter_categorie')
    eigenaar = filters.NumberFilter(method='filter_eigenaar')

    buurt = filters.CharFilter(method='filter_gebied')
    wijk = filters.CharFilter(method='filter_gebied')
    ggw = filters.CharFilter(method='filter_gebied')
    stadsdeel = filters.CharFilter(method='filter_gebied')

    class Meta:
        fields = ('categorie', 'eigenaar', 'bbox',
                  'buurt', 'wijk', 'ggw', 'stadsdeel', 'shape')

    def filter_bbox(self, queryset, name, value):
        if value:
            bbox = json.loads(value)
            points = (bbox['_southWest']['lng'], bbox['_northEast']['lat'],
                      bbox['_northEast']['lng'], bbox['_southWest']['lat'])
            box = Polygon.from_bbox(points)
            box.srid = SRID_WSG84
            box.transform(SRID_RD)
            return queryset.filter(geometrie__intersects=box)

        return queryset

    def filter_shape(self, queryset, name, value):
        if value:
            return queryset.filter(geometrie__intersects=value)

        return queryset

    def filter_categorie(self, queryset, name, value):
        if value is not None:
            queryset = queryset.filter(cat_id=value)
        return queryset

    def filter_eigenaar(self, queryset, name, value):
        eigenaarfilter = {
            1: lambda qs: qs.filter(kadastraal_object__eigendom__grondeigenaar=True),
            2: lambda qs: qs.filter(kadastraal_object__eigendom__aanschrijfbaar=True),
            3: lambda qs: qs.filter(kadastraal_object__eigendom__appartementeigenaar=True),
        }
        if value is not None and value in eigenaarfilter:
            queryset = eigenaarfilter[value](queryset).distinct()
        return queryset

    def filter_gebied(self, queryset, name, value):
        # get applicable model for parameter-name:
        gebiedsmodellen = {"wijk": bag_models.Buurtcombinatie,
                           "ggw": bag_models.Gebiedsgerichtwerken,
                           "stadsdeel": bag_models.Stadsdeel,
                           "buurt": bag_models.Buurt}
        if name in gebiedsmodellen:
            gebiedsmodel = gebiedsmodellen[name]
            try:
                gebied = gebiedsmodel.objects.get(pk=value)
                return queryset.filter(geometrie__intersects=gebied.geometrie)
            except gebiedsmodel.DoesNotExist:
                pass

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


class BrkGroepGeoFilter(BrkGeoFilter):
    eigenaar = filters.NumberFilter(method='filter_eigenaar')

    buurt = filters.CharFilter(method='filter_gebied')
    wijk = filters.CharFilter(method='filter_gebied')
    ggw = filters.CharFilter(method='filter_gebied')
    stadsdeel = filters.CharFilter(method='filter_gebied')

    zoom = filters.NumberFilter(method='filter_geen_gebied')

    class Meta:
        fields = ('categorie', 'eigenaar', 'bbox', 'buurt',
                  'wijk', 'ggw', 'stadsdeel', 'zoom')

    def filter_eigenaar(self, queryset, name, value):
        if value:
            queryset = queryset.filter(eigendom_cat=value)
        return queryset

    def filter_gebied(self, queryset, name, value):
        if name and value:
            queryset = queryset.filter(gebied=name, gebied_id=value)
        return queryset

    def filter_geen_gebied(self, queryset, name, value):
        # maps zoomlevels on to meaningfull geographical generalisations:
        filter_gebied = {8: 'stadsdeel', 9: 'ggw', 10: 'wijk', 11: 'buurt', 12: 'buurt'}
        return queryset.filter(gebied=filter_gebied[value])


class EigenPerceelGroepFilter(BrkGroepGeoFilter):
    class Meta(BrkGeoFilter.Meta):
        model = geo_models.EigenPerceelGroep


class NietEigenPerceelGroepFilter(BrkGroepGeoFilter):
    class Meta(BrkGeoFilter.Meta):
        model = geo_models.NietEigenPerceelGroep


filter_class = {
    geo_models.NietEigenPerceel: NietEigenPerceelFilter,
    geo_models.EigenPerceel: EigenPerceelFilter,
    geo_models.Appartementen: AppartementenFilter,
    geo_models.EigenPerceelGroep: EigenPerceelGroepFilter,
    geo_models.NietEigenPerceelGroep: NietEigenPerceelGroepFilter
}