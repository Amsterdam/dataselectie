from datasets.brk import geo_models

from rest_framework import serializers
from rest_framework_gis import fields


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


