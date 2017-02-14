# import uuid

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

class CBS_sbi_section(models.Model):
    code = models.CharField(max_length=1, primary_key=True)
    title = models.CharField(max_length=255, blank=False, null=False)


class CBS_sbi_rootnode(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    section = models.ForeignKey(CBS_sbi_section, on_delete=models.CASCADE)


class CBS_sbicode(models.Model):
    sbi_code = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    root_node = models.ForeignKey(CBS_sbi_rootnode, on_delete=models.CASCADE)


class DataSelectie(models.Model):

    id = models.CharField(
        max_length=20,
        primary_key=True)

    bag_vbid = models.CharField(
        max_length=16, blank=True, null=True)

    bag_numid = models.CharField(
        max_length=16, db_index=True, blank=True, null=True)

    api_json = JSONField()
