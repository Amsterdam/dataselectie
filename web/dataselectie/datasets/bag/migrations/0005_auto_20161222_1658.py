# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-22 16:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0004_merge_20161219_1336'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'verbose_name': 'Status', 'verbose_name_plural': 'Status'},
        ),
    ]