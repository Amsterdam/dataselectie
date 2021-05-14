import authorization_levels
from django.contrib.gis.db.models import Union, Extent
from django.contrib.gis.geos import Polygon
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.db import connection
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN

from datasets.brk import models, geo_models, filters, serializers
from datasets.brk.queries import meta_q
from datasets.generic.views_mixins import CSVExportView, stringify_item_value
from datasets.generic.views_mixins import TableSearchView

SRID_WSG84 = 4326
SRID_RD = 28992


def make_gebieden_lookup():
    """
    Create a dictionary that contains for each combination of gebied_type and value combination of other gebied types
    and values that are allowed/present in the data.

    For example

    { "stadsdeel_naam":
        { "Noord": {
            "stadsdeel_naam":{ "Noord" },
            "ggw_naam": {"Oost", "Dod-Noord", "West"}
            "buurtcombinatie_naam": {...},
            "buurt_naam": {...},
        ...
        },
      "ggw_naam": {
        "Oost", {
            "stadsdeel_naam": { "Noord"},
            ...

    This can be used to filter aggregates with allowed values for request parameters
    :return lookup_default_dict:
    """
    lookup = dict()
    sql = '''
    select s.naam as stadsdeel_naam, ggw.naam as ggw_naam, bc.naam as buurtcombinatie_naam, b.naam as buurt_naam
from bag_buurt b
full outer join bag_gebiedsgerichtwerken ggw on ggw.id = b.gebiedsgerichtwerken_id
full outer join bag_buurtcombinatie bc on bc.id = b.buurtcombinatie_id
full join bag_stadsdeel s on s.id = b.stadsdeel_id
union select '' as stadsdeel_naam, '' as ggw_naam, '' as buurtcombinatie_naam, '' as buurt_naam
    '''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        for row in cursor.fetchall():
            drow = {
                'stadsdeel_naam': row[0],
                'ggw_naam': row[1],
                'buurtcombinatie_naam': row[2],
                'buurt_naam': row[3]
            }
            for key1, value1 in drow.items():
                for key2, value2 in drow.items():
                    if value1 is not None and value2 is not None:
                        if key1 not in lookup:
                            lookup[key1] = dict()
                        if value1 not in lookup[key1]:
                            lookup[key1][value1] = dict()
                        if key2 in lookup[key1][value1]:
                            lookup[key1][value1][key2].add(value2)
                        else:
                            lookup[key1][value1][key2] = {value2}
    return lookup


class BrkBase(object):
    """
    Base class mixin for data settings
    """
    model = models.KadastraalObject
    index = 'DS_BRK_INDEX'
    db = 'brk'
    q_func = meta_q
    keywords = [
        'eigenaar_type',
        'eigenaar_categorie_id', 'eigenaar_cat',
        'buurt_naam', 'buurt_code', 'buurtcombinatie_naam',
        'buurtcombinatie_code', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code',
        'openbare_ruimte_naam', 'postcode'
    ]
    geo_fields = [
        {'query_param': 'shape',
         'es_doc_field': 'geometrie',
         'es_query_type': 'geo_shape'}
    ]
    keyword_mapping = {
    }
    raw_fields = []


class BrkAggBase(BrkBase):
    """
    Base class for searching with aggregations. This class adds
    the custom_aggs method to postprocess aggregations
    """

    gebieden_lookup = None

    @staticmethod
    def get_gebieden_lookup():
        """
        Do make_gebieden_lookup only once.
        Keep in class variable BrkAggBase.gebieden_lookup
        :return:
        """
        if BrkAggBase.gebieden_lookup is None:
            if BrkAggBase.gebieden_lookup is None:
                BrkAggBase.gebieden_lookup = make_gebieden_lookup()
        return BrkAggBase.gebieden_lookup

    def custom_aggs(self, elastic_data, request):
        """
        Do custom filtering on aggs. If we have parameters for gebieden
        we filter out aggregate buckets that are not related to the gebieden
        """
        filter_params = {'stadsdeel_naam', 'ggw_naam', 'buurtcombinatie_naam', 'buurt_naam'}

        query_params = request.GET
        query_filter_params = filter_params.intersection(set(query_params))

        if not query_filter_params:
            return

        lookup = self.get_gebieden_lookup()

        aggs_list = elastic_data['aggs_list']

        # loop over all filter_aggregations
        for key, value in aggs_list.items():
            if key not in filter_params:
                continue

            allowed_key_values = None
            for qfp_key in query_filter_params:
                qfp_value = query_params[qfp_key]
                if qfp_key in lookup and qfp_value in lookup[qfp_key] and key in lookup[qfp_key][qfp_value]:
                    if allowed_key_values is None:
                        allowed_key_values = lookup[qfp_key][qfp_value][key]
                    else:
                        allowed_key_values = allowed_key_values.intersection(lookup[qfp_key][qfp_value][key])
                else:
                    allowed_key_values = set()

            bucketlist = value['buckets']
            newbucket = []
            for bucketitem in bucketlist:
                if bucketitem['key'] not in allowed_key_values:
                    continue
                newbucket.append(bucketitem)

            # replace bucket list with cleaned up version
            value['doc_count'] = len(newbucket)
            value['buckets'] = newbucket


class BrkGeoLocationSearch(BrkBase, generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        if not request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            return Response(status=HTTP_403_FORBIDDEN)

        # make queryparams on underlying request-object mutable:
        request._request.GET = request.query_params.copy()
        modify_for_shape = filters.modify_queryparams_for_shape(self.request.query_params)

        if 'zoom' in self.request.query_params:
            zoom = int(self.request.query_params.get('zoom'))
            if zoom > 12:
                if 'bbox' not in request.query_params:
                    return Response("Bounding box required at this zoomlevel",
                                    status=status.HTTP_400_BAD_REQUEST)
                serialize = serializers.BrkGeoLocationSerializer(self.get_zoomed_in())
                return Response(serialize.data)

        serialize = serializers.BrkGeoLocationSerializer(self.get_zoomed_out(modify_for_shape=modify_for_shape))
        return Response(serialize.data)

    def filter(self, model):
        self.filter_class = filters.filter_class[model]
        return self.filter_queryset(model.objects)

    def _extent(self, extents):
        union = None
        for extent in extents:
            if extent is not None:
                if union is None:
                    union = Polygon.from_bbox(extent)
                else:
                    union.union(Polygon.from_bbox(extent))

        return None if union is None else union.extent

    def _get_extent(self):
        filters.remove_bbox_and_zoom_for_extent(self.request.query_params)
        extents = []
        for geo_model in [geo_models.EigenPerceel, geo_models.NietEigenPerceel]:
            filtered_queryset = self.filter(geo_model)
            extents.append(filtered_queryset.aggregate(box=Extent('geometrie'))['box'])
        return self._extent(extents)

    def get_zoomed_in(self):
        # first peroform genaral modifications to queryparams
        filters.modify_queryparams_for_detail(self.request.query_params)

        perceel_queryset = self.filter(geo_models.EigenPerceel)
        eigenpercelen = perceel_queryset.aggregate(geom=Union('geometrie'))

        appartementen = self.filter(geo_models.Appartementen).all()
        perceel_queryset = self.filter(geo_models.NietEigenPerceel)
        niet_eigenpercelen = perceel_queryset.aggregate(geom=Union('geometrie'))

        extent = self._get_extent()

        return {"extent": extent,
                "appartementen": appartementen,
                "eigenpercelen": eigenpercelen['geom'],
                "niet_eigenpercelen": niet_eigenpercelen['geom']}

    def get_zoomed_out(self, modify_for_shape=False):
        if modify_for_shape:
            filters.modify_queryparams_for_detail(self.request.query_params)
            eigen_perceel_queryset = self.filter(geo_models.EigenPerceel)
            filters.modify_queryparams_for_overview(self.request.query_params)
            niet_eigen_perceel_queryset = self.filter(geo_models.NietEigenPerceelGroep)
        else:
            filters.modify_queryparams_for_overview(self.request.query_params)
            eigen_perceel_queryset = self.filter(geo_models.EigenPerceelGroep)
            niet_eigen_perceel_queryset = self.filter(geo_models.NietEigenPerceelGroep)

        appartementen = []
        eigenpercelen = eigen_perceel_queryset.aggregate(geom=Union('geometrie'))
        niet_eigenpercelen = niet_eigen_perceel_queryset.aggregate(geom=Union('geometrie'))
        extent = self._get_extent()

        return {"extent": extent,
                "appartementen": appartementen,
                "eigenpercelen": eigenpercelen['geom'],
                "niet_eigenpercelen": niet_eigenpercelen['geom']}


class BrkSearch(BrkAggBase, TableSearchView):
    def handle_request(self, request, *args, **kwargs):
        if not request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            raise PermissionDenied("scope BRK/RSN required")
        return super().handle_request(request, *args, **kwargs)

    def elastic_query(self, query):
        result = meta_q(query)
        result.update({
            "_source": {
                "exclude": ["adressen"]
            },
        })
        return result


class BrkKotSearch(BrkAggBase, TableSearchView):
    def handle_request(self, request, *args, **kwargs):
        if not request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            raise PermissionDenied("scope BRK/RSN required")
        return super().handle_request(request, *args, **kwargs)

    def load_from_elastic(self) -> dict:
        """
        Overwrite method of TableSearchView.load_from_elastic.
        This overwrite make the result of kadastraal ID's unique
        Due to that multiple addresses can be related to one kadastraal ID
        that causes the kadastraal ID to appear more than once.
        """
        # looking for a query
        query_string = self.request_parameters.get('query', None)

        # Building the query
        q = self.elastic_query(query_string)
        query = self.add_elastic_filters(q)

        # remove size and page filter
        # because after manipulating the result for unique kadastraal IDs
        # the returned rows must be restricted by the size and page paramaters
        # not before.
        param_size = query['size']
        offset = (int(self.request_parameters.get('page', 1)) - 1) * param_size
        param_size = param_size * int(self.request_parameters.get('page', 1)) if offset > 0 else param_size

        # reset orginal param values (the param_size and offset are used now)
        query['size'] = settings.MAX_SEARCH_ITEMS
        query['from'] = 0

        # Performing the search
        response = self.elastic.search(
            index=settings.ELASTIC_INDICES[self.index], body=query)

        # identify unique kadastraal objects
        kadastraal_unique_set = set()
        objects_to_delete_list = []
        for item in response['hits']['hits']:
            if item['_source']['kadastraal_object_id'] not in kadastraal_unique_set:
                kadastraal_unique_set.add(item['_source']['kadastraal_object_id'])
            else:
                objects_to_delete_list.append(item)

        # remove duplicate kadastraal objects
        for kadastraal_obj in objects_to_delete_list:
            response['hits']['hits'].remove(kadastraal_obj)

        elastic_data = {
            'aggs_list': self.process_aggs(response.get('aggregations', {})),
            'object_list': [

                            item['_source'] for item in
                            response['hits']['hits'][offset:param_size]

                            ],
            'object_count': response['hits']['total']}

        try:
            elastic_data.update(
                self.add_page_counters(int(elastic_data['object_count'])))
        except TypeError:
            # There is no definition for the preview size
            pass

        return elastic_data

    def elastic_query(self, query):
        result = meta_q(query)
        result.update({
            "_source": {
                "include": [
                    "kadastraal_object_id",
                    "aanduiding",
                    "eerste_adres",
                ]
            },
        })
        return result


class BrkCSV(BrkBase, CSVExportView):
    """
    Output CSV
    See https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    """
    fields_and_headers = (
        ('aanduiding', 'Kadastraal object'),
        ('kadastrale_gemeentecode', 'Kadastrale gemeentecode'),
        ('sectie', 'Sectie'),
        ('perceelnummer', 'Perceelnummer'),
        ('indexletter', 'Indexletter'),
        ('indexnummer', 'Indexnummer'),
        ('adressen', 'Adressen'),
        ('verblijfsobject_id', 'Verblijfsobjectidentificatie'),
        ('kadastrale_gemeentenaam', 'Kadastrale gemeente'),
        ('burgerlijke_gemeentenaam', 'Gemeente'),
        ('koopsom', 'Koopsom (euro)'),
        ('koopjaar', 'Koopjaar'),
        ('grootte', 'Grootte (m2)'),
        ('cultuurcode_bebouwd', 'Cultuur bebouwd'),
        ('cultuurcode_onbebouwd', 'Cultuur onbebouwd'),
        ('aard_zakelijk_recht', 'Aard zakelijk recht'),
        ('zakelijk_recht_aandeel', 'Aandeel zakelijk recht'),
        ('sjt_type', 'Type subject'),
        ('sjt_voornamen', 'Voornamen'),
        ('sjt_voorvoegsels', 'Voorvoegsels'),
        ('sjt_geslachtsnaam', 'Geslachtsnaam'),
        ('sjt_geboortedatum', 'Geboortedatum'),
        ('sjt_geboorteplaats', 'Geboorteplaats'),
        ('sjt_geboorteland_code', 'Geboorteland'),
        ('sjt_datum_overlijden', 'Datum van overlijden'),
        ('sjt_statutaire_naam', 'Statutaire naam'),
        ('sjt_statutaire_zetel', 'Statutaire zetel'),
        ('sjt_statutaire_rechtsvorm', 'Statutaire rechtsvorm'),
        ('sjt_kvknummer', 'KvK-nummer'),
        ('sjt_rsin', 'RSIN'),
        ('sjt_woonadres', 'Woonadres'),
        ('sjt_woonadres_buitenland', 'Woonadres buitenland'),
        ('sjt_postadres', 'Postadres'),
        ('sjt_postadres_postbus', 'Postadres postbus'),
        ('sjt_postadres_buitenland', 'Postadres buitenland'),
    )

    def handle_request(self, request, *args, **kwargs):
        if not request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            raise PermissionDenied("scope BRK/RSN required")
        return super().handle_request(request, *args, **kwargs)

    field_names = [h[0] for h in fields_and_headers]
    csv_headers = [h[1] for h in fields_and_headers]

    def elastic_query(self, query):
        result = meta_q(query, False, True)
        result.update({
            "_source": {
                "exclude": ["eerste_adres"]
            },
        })
        return result

    def item_data_update(self, item, request):
        # create_geometry_dict(item)
        return item

    def sanitize_fields(self, item, field_names):
        updates = {}
        for field_name in field_names:
            if field_name == 'zakelijk_recht_aandeel':
                zakelijk_recht_aandeel = stringify_item_value(item.get(field_name, None))
                updates[field_name] = '"{}"'.format(zakelijk_recht_aandeel) if zakelijk_recht_aandeel else ''
            elif field_name == 'sjt_postadres_postbus':
                value = stringify_item_value(item.get(field_name, None))
                if value and not value.lower().startswith('postbus'):
                    updates[field_name] = 'Postbus ' + value
            else:
                updates[field_name] = stringify_item_value(item.get(field_name, None))
        item.update(updates)

    def paginate(self, offset, q):
        if 'size' in q:
            del (q['size'])
        return q
