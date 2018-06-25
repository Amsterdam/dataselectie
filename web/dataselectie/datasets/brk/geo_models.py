from django.contrib.gis.db import models as geo
from django.db import models

from datasets.brk import models as brk

SRID_WSG84 = 4326


class BrkEigenaarGeoModel(models.Model):
    id = models.IntegerField(primary_key=True)
    kadastraal_object = models.ForeignKey(
        brk.KadastraalObject,
        on_delete=models.CASCADE,
    )
    cat = models.ForeignKey(
        brk.EigenaarCategorie,
        on_delete=models.CASCADE,
    )
    geometrie = geo.PointField(srid=SRID_WSG84)

    class Meta:
        abstract = True


class Appartementen(BrkEigenaarGeoModel):
    aantal = models.IntegerField()
    plot = geo.MultiPolygonField(srid=SRID_WSG84)

    class Meta:
        db_table = "geo_brk_eigendom_point_index"
        verbose_name = "Appartementen"
        verbose_name_plural = "AppartementenGroepen"
        managed = False


class EigenPerceel(BrkEigenaarGeoModel):
    geometrie = geo.MultiPolygonField(srid=SRID_WSG84)
    class Meta:
        db_table = "geo_brk_eigendom_poly"
        verbose_name = "EigenPerceel"
        verbose_name_plural = "EigenPercelen"
        managed = False


class NietEigenPerceel(BrkEigenaarGeoModel):
    geometrie = geo.MultiPolygonField(srid=SRID_WSG84)
    class Meta:
        db_table = "geo_brk_niet_eigendom_poly"
        verbose_name = "NietEigenPerceel"
        verbose_name_plural = "NietEigenPercelen"
        managed = False


class BrkGegroepeerdGeoModel(models.Model):
    id = models.IntegerField(primary_key=True)

    cat = models.ForeignKey(
        brk.EigenaarCategorie,
        on_delete=models.CASCADE,
    )

    eigendom_cat = models.IntegerField()
    gebied = models.CharField(max_length=255)
    gebied_id = models.CharField(max_length=255, null=True)
    geometrie = geo.MultiPolygonField(srid=SRID_WSG84)

    class Meta:
        abstract = True


class EigenPerceelGroep(BrkGegroepeerdGeoModel):
    class Meta:
        db_table = "geo_brk_eigendom_poly_index"
        verbose_name = "EigenPerceelGroep"
        verbose_name_plural = "EigenPerceelGroepen"
        managed = False


class NietEigenPerceelGroep(BrkGegroepeerdGeoModel):
    class Meta:
        db_table = "geo_brk_niet_eigendom_poly_index"
        verbose_name = "NietEigenPerceelGroep"
        verbose_name_plural = "NietEigenPercelenGroepen"
        managed = False

