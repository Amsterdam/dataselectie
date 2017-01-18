from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class DataSelectie(models.Model):

    id = models.CharField(
        max_length=20, primary_key=True)

    bag_numid = models.CharField(
        max_length=16, blank=True, null=True, db_index=True)

    bag_vbid = models.CharField(
        max_length=16, blank=True, null=True)

    api_json = JSONField()

    class Meta(object):
        managed = True
        verbose_name = "Handelsregister dataselectie"
        verbose_name_plural = "Handelsregister dataselecties"
        ordering = ('id',)


class CBS_sbi_hoofdcat(models.Model):
    hcat = models.CharField(max_length=20, primary_key=True)
    hoofdcategorie = models.CharField(max_length=140, blank=False, null=False)


class CBS_sbi_subcat(models.Model):
    scat = models.CharField(max_length=20, primary_key=True)
    subcategorie = models.CharField(max_length=140, blank=False, null=False)
    hcat = models.ForeignKey(CBS_sbi_hoofdcat, on_delete=models.CASCADE)


class CBS_sbicodes(models.Model):
    sbi_code = models.CharField(max_length=14, primary_key=True)
    sub_sub_categorie = models.CharField(
        max_length=140, blank=False, null=False)
    scat = models.ForeignKey(CBS_sbi_subcat, on_delete=models.CASCADE)
