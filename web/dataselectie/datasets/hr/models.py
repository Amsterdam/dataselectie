from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

class HandelsRegister(models.Model):

    class Meta(object):
        # managed = False
        verbose_name = "Handelsregister dataselectie"
        verbose_name_plural = "Handelsregister dataselecties"
        ordering = ('id',)

    id = models.CharField(
        max_length = 20,
        primary_key=True)

    api_json = JSONField()
