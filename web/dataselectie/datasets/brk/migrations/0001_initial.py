# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-26 13:54
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aantekening',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Adres',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('openbareruimte_naam', models.CharField(max_length=80, null=True)),
                ('huisnummer', models.IntegerField(null=True)),
                ('huisletter', models.CharField(max_length=1, null=True)),
                ('toevoeging', models.CharField(max_length=4, null=True)),
                ('postcode', models.CharField(max_length=6, null=True)),
                ('woonplaats', models.CharField(max_length=80, null=True)),
                ('postbus_nummer', models.IntegerField(null=True)),
                ('postbus_postcode', models.CharField(max_length=50, null=True)),
                ('postbus_woonplaats', models.CharField(max_length=80, null=True)),
                ('buitenland_adres', models.CharField(max_length=100, null=True)),
                ('buitenland_woonplaats', models.CharField(max_length=100, null=True)),
                ('buitenland_regio', models.CharField(max_length=100, null=True)),
                ('buitenland_naam', models.CharField(max_length=100, null=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='APerceelGPerceelRelatie',
            fields=[
                ('id', models.CharField(max_length=121, primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Eigenaar',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('type', models.SmallIntegerField(choices=[(0, 'Natuurlijk persoon'), (1, 'Niet-natuurlijk persoon')])),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('voornamen', models.CharField(max_length=200, null=True)),
                ('voorvoegsels', models.CharField(max_length=10, null=True)),
                ('naam', models.CharField(max_length=200, null=True)),
                ('bs', models.CharField(max_length=90, null=True)),
                ('geboortedatum', models.CharField(max_length=50, null=True)),
                ('geboorteplaats', models.CharField(max_length=80, null=True)),
                ('overlijdensdatum', models.CharField(max_length=50, null=True)),
                ('partner_voornamen', models.CharField(max_length=200, null=True)),
                ('partner_voorvoegsels', models.CharField(max_length=10, null=True)),
                ('partner_naam', models.CharField(max_length=200, null=True)),
                ('rsin', models.CharField(max_length=80, null=True)),
                ('kvknummer', models.CharField(max_length=8, null=True)),
                ('statutaire_naam', models.CharField(max_length=200, null=True)),
                ('statutaire_zetel', models.CharField(max_length=24, null=True)),
                ('bron', models.SmallIntegerField(choices=[(0, 'Basisregistraties'), (1, 'Kadaster')])),
            ],
            options={
                'verbose_name': 'Kadastraal subject',
                'verbose_name_plural': 'Kadastrale subjecten',
                'permissions': (('view_sensitive_details', 'Kan privacy-gevoelige data inzien'),),
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EigenaarCategorie',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('categorie', models.CharField(max_length=100)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EigendomBuurt',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EigendomGGW',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EigendomStadsdeel',
            fields=[
                ('row_number', models.BigIntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EigendomWijk',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Gemeente',
            fields=[
                ('gemeente', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Gemeente',
                'verbose_name_plural': 'Gemeentes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraalObject',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('aanduiding', models.CharField(max_length=17)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('perceelnummer', models.IntegerField()),
                ('indexletter', models.CharField(max_length=1)),
                ('indexnummer', models.IntegerField()),
                ('grootte', models.IntegerField(null=True)),
                ('koopsom', models.IntegerField(null=True)),
                ('koopsom_valuta_code', models.CharField(max_length=50, null=True)),
                ('koopjaar', models.CharField(max_length=15, null=True)),
                ('meer_objecten', models.NullBooleanField(default=None)),
                ('register9_tekst', models.TextField()),
                ('status_code', models.CharField(max_length=50)),
                ('toestandsdatum', models.DateField(null=True)),
                ('voorlopige_kadastrale_grens', models.NullBooleanField(default=None)),
                ('in_onderzoek', models.TextField(null=True)),
                ('poly_geom', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
                ('point_geom', django.contrib.gis.db.models.fields.PointField(null=True, srid=28992)),
            ],
            options={
                'ordering': ('kadastrale_gemeente__id', 'sectie', 'perceelnummer', '-indexletter', 'indexnummer'),
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraalObjectVerblijfsobjectRelatie',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraleGemeente',
            fields=[
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('naam', models.CharField(max_length=100)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Kadastrale Gemeente',
                'verbose_name_plural': 'Kadastrale Gemeentes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraleSectie',
            fields=[
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('sectie', models.CharField(max_length=2)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Kadastrale Sectie',
                'verbose_name_plural': 'Kadastrale Secties',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ZakelijkRecht',
            fields=[
                ('id', models.CharField(max_length=183, primary_key=True, serialize=False)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('zrt_id', models.CharField(max_length=60)),
                ('aard_zakelijk_recht_akr', models.CharField(max_length=3, null=True)),
                ('teller', models.IntegerField(null=True)),
                ('noemer', models.IntegerField(null=True)),
                ('kadastraal_object_status', models.CharField(max_length=50)),
                ('_kadastraal_subject_naam', models.CharField(max_length=200)),
                ('_kadastraal_object_aanduiding', models.CharField(max_length=100)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ZakelijkRechtVerblijfsobjectRelatie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AanduidingNaam',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AardAantekening',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AardZakelijkRecht',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AppartementsrechtsSplitsType',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Beschikkingsbevoegdheid',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CultuurCodeBebouwd',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CultuurCodeOnbebouwd',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Geslacht',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rechtsvorm',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SoortGrootte',
            fields=[
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Eigendom',
            fields=[
                ('zakelijk_recht', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='brk.ZakelijkRecht')),
                ('aard_zakelijk_recht_akr', models.CharField(max_length=3, null=True)),
                ('grondeigenaar', models.BooleanField()),
                ('aanschrijfbaar', models.BooleanField()),
                ('appartementeigenaar', models.BooleanField()),
            ],
            options={
                'managed': False,
            },
        ),
    ]
