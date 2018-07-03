from collections import defaultdict

import authorization_levels
from rest_framework.status import HTTP_403_FORBIDDEN
from django.db import connection

from datasets.brk.queries import meta_q
from datasets.brk import models, geo_models, filters, serializers

from datasets.generic.views_mixins import CSVExportView, stringify_item_value
from datasets.generic.views_mixins import TableSearchView

from django.core.exceptions import PermissionDenied
from django.contrib.gis.db.models import Collect
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

SRID_WSG84 = 4326
SRID_RD = 28992


def rec_defaultdict():
    """
    Make a recursive defaultdict. You can do:
        x = rec_defaultdict()
        x['a']['b']['c']['d']=1
        print(x['a']['b']['c']['d'])
    :return recursice defaultdict:
    """
    return defaultdict(rec_defaultdict)


def make_gebieden_lookup():
    """
    Create a dictionary that contains for each combination of gebied_type and value combination sof other gebied types
    and values that are allowed/present in the data.

    For example

    { "stadsdeel_naam":
        { "Noord": {
            "stadsdeel_naam":{ "Noord" },
            "ggw_naam": {"Oost", "Dod-Noord", "West"}
            "wijk_naam": {...},
            "buurt_naam": {...},
        ...
        },
      "ggw_naam": {
        "Oost", {
            "stadsdeel_naam": { "Noord"},
            ...

    Thios can be used to filter aggregates with allowed values for request parameters
    :return lookup_default_dict:
    """
    lookup = rec_defaultdict()
    sql = '''
    select s.naam as stadsdeel_naam, ggw.naam as ggw_naam, bc.naam as wijk_naam , b.naam as buurt_naam 
from bag_buurt b
full outer join bag_gebiedsgerichtwerken ggw on ggw.id = gebiedsgerichtwerken_id
full outer join bag_buurtcombinatie bc on bc.id = b.buurtcombinatie_id
full join bag_stadsdeel s on s.id = b.stadsdeel_id
union select '' as stadsdeel_naam, '' as ggw_naam, '' as wijk_naam , '' as buurt_naam
    '''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        for row in cursor.fetchall():
            drow = {
                'stadsdeel_naam': row[0],
                'ggw_naam': row[1],
                'wijk_naam': row[2],
                'buurt_naam': row[3]
            }
            for key1, value1 in drow.items():
                for key2, value2 in drow.items():
                    if value1 is not None and value2 is not None:
                        if key1 in lookup and value1 in lookup[key1] and key2 in lookup[key1][value1]:
                            lookup[key1][value1][key2].add(value2)
                        else:
                            lookup[key1][value1][key2] = {value2}

    return lookup


class BrkBase(object):
    """
    Base class mixing for data settings
    """
    model = models.KadastraalObject
    index = 'DS_BRK_INDEX'
    db = 'brk'
    q_func = meta_q
    keywords = [
        'eigenaar_type',
        'eigenaar_categorie_id', 'eigenaar_cat',
        'buurt_naam', 'buurt_code', 'wijk_code',
        'wijk_naam', 'ggw_naam', 'ggw_code',
        'stadsdeel_naam', 'stadsdeel_code',
        'openbare_ruimte_naam', 'postcode'
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
        filter_params = {'stadsdeel_naam', 'ggw_naam', 'wijk_naam', 'buurt_naam'}

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
                if allowed_key_values is None:
                    allowed_key_values = lookup[qfp_key][qfp_value][key]
                else:
                    allowed_key_values = allowed_key_values.intersection(lookup[qfp_key][qfp_value][key])

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
        filters.modify_queryparams_for_shape(self.request.query_params)

        if 'zoom' in self.request.query_params:
            zoom = int(self.request.query_params.get('zoom'))
            if zoom > 12:
                if 'bbox' not in request.query_params:
                    return Response("Bounding box required at this zoomlevel",
                                    status=status.HTTP_400_BAD_REQUEST)
                serialize = serializers.BrkGeoLocationSerializer(self.get_zoomed_in())
                return Response(serialize.data)

        serialize = serializers.BrkGeoLocationSerializer(self.get_zoomed_out())
        return Response(serialize.data)

    def filter(self, model):
        self.filter_class = filters.filter_class[model]
        return self.filter_queryset(model.objects)

    def get_zoomed_in(self):
        # first peroform genaral modifications to queryparams
        filters.modify_queryparams_for_detail_eigen(self.request.query_params)

        #   eigenpercelen works with non-modified categorie ...
        perceel_queryset = self.filter(geo_models.EigenPerceel)
        eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        #   ... then appartementen en niet-eigenpercelen require modified categorie
        filters.modify_queryparams_for_detail_other(self.request.query_params)

        appartementen = self.filter(geo_models.Appartementen).all()
        perceel_queryset = self.filter(geo_models.NietEigenPerceel)
        niet_eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        return {"appartementen": appartementen,
                "eigenpercelen": eigenpercelen['geom'],
                "niet_eigenpercelen": niet_eigenpercelen['geom']}

    def get_zoomed_out(self):
        # first peroform genaral modifications to queryparams
        filters.modify_queryparams_for_overview(self.request.query_params)

        appartementen = []

        perceel_queryset = self.filter(geo_models.EigenPerceelGroep)
        eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        perceel_queryset = self.filter(geo_models.NietEigenPerceelGroep)
        niet_eigenpercelen = perceel_queryset.aggregate(geom=Collect('geometrie'))

        return {"appartementen": appartementen,
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
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"kadastraal_object_index": 0}}
                    ]
                }
            }
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
        ('kadastrale_gemeentenaam', 'Kadastrale gemeentenaam'),
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
        item.update(
            {field_name: stringify_item_value(item.get(field_name, None))
             for field_name in field_names})

    def paginate(self, offset, q):
        if 'size' in q:
            del (q['size'])
        return q
