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


class MutatieGebruikerMixin(models.Model):
    mutatie_gebruiker = models.CharField(max_length=30, null=True)  # type: str

    class Meta(object):
        abstract = True


class CodeOmschrijvingMixin(models.Model):
    code = models.CharField(max_length=4, primary_key=True)  # type: str
    omschrijving = models.CharField(max_length=150, null=True)  # type: str

    class Meta(object):
        abstract = True

    def __str__(self) -> str:
        return "{}: {}".format(self.code, self.omschrijving)


class JSONinputMixin(models.Model):
    id = models.CharField(
        max_length=20,
        primary_key=True)
    api_json = JSONField()

    class Meta(object):
        abstract = True
