import rapidjson

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

class DataSelectie(models.Model):

    id = models.CharField(
        max_length = 20,
        primary_key=True)

    bag_vbid = models.CharField(
        max_length=16, blank=True, null=True, db_index=True)

    api_json = JSONField()

    class Meta(object):
        managed = True
        verbose_name = "Handelsregister dataselectie"
        verbose_name_plural = "Handelsregister dataselecties"
        ordering = ('id',)


class DummyTabel(models.Model):

    id = models.IntegerField(serialize=True, primary_key=True)
    bla = models.CharField(
        max_length = 20)

    class Meta(object):
        managed = True
        verbose_name = "Dummy tabel"
        verbose_name_plural = "Dummy tabel"
        ordering = ('id',)
