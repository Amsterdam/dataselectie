from django.contrib.gis.db import models as geo
from django.db import models

from datasets.brk import models as brk


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
    geometrie = geo.PointField(srid=28992)

    class Meta:
        abstract = True


class Appartementen(BrkEigenaarGeoModel):
    aantal = models.IntegerField()

    class Meta:
        db_table = "geo_brk_eigendom_point"
        verbose_name = "Appartementen"
        verbose_name_plural = "AppartementenGroepen"
        managed = False


class EigenPerceel(BrkEigenaarGeoModel):
    class Meta:
        db_table = "geo_brk_eigendom_poly"
        verbose_name = "EigenPerceel"
        verbose_name_plural = "EigenPercelen"
        managed = False


class NietEigenPerceel(BrkEigenaarGeoModel):
    class Meta:
        db_table = "geo_brk_niet_eigendom_poly"
        verbose_name = "NietEigenPerceel"
        verbose_name_plural = "NietEigenPercelen"
        managed = False
