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
