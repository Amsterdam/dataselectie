# Python
import datetime
# Package
from django.db import models
from django.contrib.postgres.fields import JSONField


class ImportStatusMixin(models.Model):
    date_modified = models.DateTimeField(auto_now=True)  # type: datetime.datetime

    class Meta(object):
        # type object
        abstract = True


class DocumentStatusMixin(models.Model):
    document_mutatie = models.DateField(null=True)  # type: datetime.date
    document_nummer = models.CharField(max_length=20, null=True)  # type: str

    class Meta(object):
        abstract = True


class GeldigheidMixin(models.Model):
    begin_geldigheid = models.DateField(null=True)  # type: datetime.date
    einde_geldigheid = models.DateField(null=True)  # type: datetime.date

    class Meta(object):
        abstract = True


class JSONinputMixin(models.Model):
    id = models.CharField(
        max_length=20,
        primary_key=True)
    api_json = JSONField()

    class Meta(object):
        abstract = True
