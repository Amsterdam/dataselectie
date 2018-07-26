import json

from django.contrib.gis.geos import Polygon
from django_filters import rest_framework as filters
from rest_framework_gis.filterset import GeoFilterSet
from datasets.bag import models as bag_models
from datasets.brk import models, geo_models

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
            box = self._get_box(value)
            return queryset.filter(geometrie__intersects=box)
        return queryset

    def _get_box(self, value):
        bbox = json.loads(value)
        points = (bbox['_southWest']['lng'], bbox['_northEast']['lat'],
                  bbox['_northEast']['lng'], bbox['_southWest']['lat'])
        box = Polygon.from_bbox(points)
        box.srid = SRID_WSG84
        box.transform(SRID_RD)
        return box

    def filter_shape(self, queryset, name, value):
        if value:
            return queryset.filter(geometrie__intersects=value)
        return queryset

    def filter_categorie(self, queryset, name, value):
        if value is not None:
            queryset = queryset.filter(cat_id=value)
        return queryset

    def filter_eigenaar(self, queryset, name, value):
        if value:
            queryset = queryset.filter(eigendom_cat=value)
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
    shape = filters.CharFilter(method='filter_shape')
    bbox = filters.CharFilter(method='filter_bbox')

    class Meta(BrkGeoFilter.Meta):
        model = geo_models.Appartementen

    def filter_shape(self, queryset, name, value):
        if value:
            return queryset.filter(plot__intersects=value)
        return queryset

    def filter_bbox(self, queryset, name, value):
        if value:
            box = self._get_box(value)
            return queryset.filter(plot__intersects=box)
        return queryset


class EigenPerceelFilter(BrkGeoFilter):
    class Meta(BrkGeoFilter.Meta):
        model = geo_models.EigenPerceel


class NietEigenPerceelFilter(BrkGeoFilter):
    class Meta(BrkGeoFilter.Meta):
        model = geo_models.NietEigenPerceel


class BrkGroepGeoFilter(BrkGeoFilter):
    buurt = filters.CharFilter(method='filter_gebied')
    wijk = filters.CharFilter(method='filter_gebied')
    ggw = filters.CharFilter(method='filter_gebied')
    stadsdeel = filters.CharFilter(method='filter_gebied')

    zoom = filters.NumberFilter(method='filter_geen_gebied')

    class Meta:
        fields = ('categorie', 'eigenaar', 'bbox', 'buurt',
                  'wijk', 'ggw', 'stadsdeel', 'zoom')

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


def _prepare_queryparams_for_categorie(query_params):
    """Adds catch-all category if queryparam `category` is missing
        unless we only see 'appartementsrechten' """
    if 'categorie' not in query_params and query_params['eigenaar'] is not 3:
        query_params['categorie'] = 99


def _prepare_queryparams_for_eigenaar(query_params):
    """Adds catch-all category if queryparam `eigenaar` is missing """
    if 'eigenaar' not in query_params:
        query_params['eigenaar'] = 9


def _lookup_ids_queryparams(query_params):
    """Find, and add as queryparam, id's for gebieden en eigenaars """
    if 'eigenaar_cat' in query_params:
        categorie = models.EigenaarCategorie.objects.filter(categorie=query_params['eigenaar_cat'])[0]
        query_params['categorie'] = categorie.id
    if 'eigenaar_type' in query_params:
        eigenaar = {'Grondeigenaar': 1, 'Pandeigenaar': 2, 'Appartementseigenaar': 3}[query_params['eigenaar_type']]
        query_params['eigenaar'] = eigenaar

    if 'stadsdeel_naam' in query_params:
        stadsdeel = bag_models.Stadsdeel.objects.filter(naam=query_params['stadsdeel_naam'])[0]
        query_params['stadsdeel'] = stadsdeel.id
    if 'ggw_naam' in query_params:
        ggw = bag_models.Gebiedsgerichtwerken.objects.filter(naam=query_params['ggw_naam'])[0]
        query_params['ggw'] = ggw.id
    if 'buurtcombinatie_naam' in query_params:
        wijk = bag_models.Buurtcombinatie.objects.filter(naam=query_params['buurtcombinatie_naam'])[0]
        query_params['wijk'] = wijk.id
    if 'buurt_naam' in query_params:
        buurt = bag_models.Buurt.objects.filter(naam=query_params['buurt_naam'])[0]
        query_params['buurt'] = buurt.id


def _prepare_queryparams_for_group_filter(query_params):
    """Remove all but the smallest gebieden queryparam """
    _prepare_queryparams_for_categorie(query_params)

    # only filter on the most detailed level
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


def modify_queryparams_for_shape(query_params):
    """Translates queryaram `shape` to Polygon, or removes it. Also `zoom` param is modified """
    if 'shape' in query_params:
        points = json.loads(query_params['shape'])
        if len(points) > 2:
            # close ring and create Polygon
            polygon = Polygon(points+[points[0]])
            polygon.srid = SRID_WSG84
            query_params['shape'] = polygon

            zoom = int(query_params['zoom']) if 'zoom' in query_params else 0
            query_params['zoom'] = max(zoom, 12)
            if zoom < 13:
                return True
        else:
            query_params.pop('shape', None)

    return False


def modify_queryparams_for_detail(query_params):
    _lookup_ids_queryparams(query_params)
    _prepare_queryparams_for_eigenaar(query_params)
    _prepare_queryparams_for_categorie(query_params)


def modify_queryparams_for_overview(query_params):
    _lookup_ids_queryparams(query_params)
    _prepare_queryparams_for_eigenaar(query_params)
    _prepare_queryparams_for_group_filter(query_params)


def remove_bbox_and_zoom_for_extent(query_params):
    query_params.pop('bbox', None)
    query_params.pop('zoom', None)
