import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appartementen',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('plot', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('aantal', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Appartementen',
                'verbose_name_plural': 'AppartementenGroepen',
                'db_table': 'geo_brk_eigendom_point_index',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EigenPerceel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'verbose_name': 'EigenPerceel',
                'verbose_name_plural': 'EigenPercelen',
                'db_table': 'geo_brk_eigendom_poly',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EigenPerceelGroep',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('eigendom_cat', models.IntegerField()),
                ('gebied', models.CharField(max_length=255)),
                ('gebied_id', models.CharField(max_length=255, null=True)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'verbose_name': 'EigenPerceelGroep',
                'verbose_name_plural': 'EigenPerceelGroepen',
                'db_table': 'geo_brk_eigendom_poly_index',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NietEigenPerceel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'verbose_name': 'NietEigenPerceel',
                'verbose_name_plural': 'NietEigenPercelen',
                'db_table': 'geo_brk_niet_eigendom_poly',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NietEigenPerceelGroep',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('eigendom_cat', models.IntegerField()),
                ('gebied', models.CharField(max_length=255)),
                ('gebied_id', models.CharField(max_length=255, null=True)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'verbose_name': 'NietEigenPerceelGroep',
                'verbose_name_plural': 'NietEigenPercelenGroepen',
                'db_table': 'geo_brk_niet_eigendom_poly_index',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='eigendom',
            options={'managed': False, 'verbose_name': 'Eigendom', 'verbose_name_plural': 'Eigendommen'},
        ),
    ]
