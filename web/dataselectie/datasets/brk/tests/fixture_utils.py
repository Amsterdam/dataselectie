import logging

from datasets.brk import models
from django.db import connection
from django.contrib.gis.geos import Polygon, Point
from datasets.brk import geo_models
from datasets.brk.management import brk_batch_sql
from .fixtures_geometrie import perceel_geometrie

log = logging.getLogger(__name__)

SRID_WSG84 = 4326
SRID_RD = 28992


def create_kadastraal_object():
    """
    depends on kadastrale gemeente / kadastrale sectie
    :return: A list of kot fixtures
    """
    return [
        models.KadastraalObject.objects.get_or_create(
            id='KOT132',
            aanduiding='ABC',
            kadastrale_gemeente_id='AX001',
            sectie_id='G3',
            perceelnummer=12,
            indexletter='B',
            indexnummer=23,
            soort_grootte_id='SBCD',
            register9_tekst='12345789',
            status_code='X3'
    )]


def create_eigendom():
    """
    depends on kadastraal object and categroie fixtures
    :return: a list of eigendom objects
    """
    create_eigenaar_categorie()
    create_kadastraal_object()
    return [
        models.Eigendom.objects.get_or_create(
            zakelijk_recht_id='ZAK01',
            kadastraal_subject_id='SUBJ_ID',
            kadastraal_object_id='KOT132',
            eigenaar_categorie_id=3,
            grondeigenaar=True,
            aanschrijfbaar=False,
            appartementeigenaar=False
        )
    ]


def create_eigenaar_categorie():
    return [
        models.EigenaarCategorie.objects.get_or_create(
            id=3,
            categorie='De staat',
        )
    ]


def create_geo_tables():
    with connection.cursor() as c:
        for sql_command in brk_batch_sql.dataselection_sql_commands \
                           + brk_batch_sql.mapselection_sql_commands:
            c.execute(sql_command)


def create_appartementen():
    return [
        geo_models.Appartementen.objects.get_or_create(
            id=1,
            cat_id=3,
            geometrie=Point(4.895, 52.368, srid=SRID_WSG84),
        )
    ]


def create_eigenpercelen():
    return [
        geo_models.EigenPerceel.objects.get_or_create(
            id=1,
            cat_id=3,
            geometrie=perceel_geometrie[1],
        ),
    ]


def create_eigenperceelgroepen():
    objects = []
    id = 0

    for category in [3, 99]:
        for eigendom_cat in [1, 9]:
            for gebied in [('buurt', '20'), ('wijk', '3630012052036'),
                           ('ggw', 'DX01'), ('stadsdeel', '03630000000018')]:
                id += 1
                objects.append(
                    geo_models.EigenPerceelGroep.objects.get_or_create(
                        id=id,
                        cat_id=category,
                        eigendom_cat=eigendom_cat,
                        gebied=gebied[0],
                        gebied_id=gebied[1],
                        geometrie=perceel_geometrie[1],
                    )
                )

    return objects


def create_niet_eigenpercelen():
    return [
        geo_models.NietEigenPerceel.objects.get_or_create(
            id=1,
            cat_id=3,
            geometrie=perceel_geometrie[2],
        )
    ]


def create_niet_eigenperceelgroepen():
    objects = []
    id = 0

    for category in [3, 99]:
        for eigendom_cat in [3, 9]:
            for gebied in [('buurt', '20'), ('wijk', '3630012052036'),
                           ('ggw', 'DX01'), ('stadsdeel', '03630000000018')]:
                id += 1
                objects.append(
                    geo_models.NietEigenPerceelGroep.objects.get_or_create(
                        id=id,
                        cat_id=category,
                        eigendom_cat=eigendom_cat,
                        gebied=gebied[0],
                        gebied_id=gebied[1],
                        geometrie=perceel_geometrie[2],
                    )
                )

    return objects


def create_geo_data():
    create_appartementen()
    create_eigenpercelen()
    create_eigenperceelgroepen()
    create_niet_eigenpercelen()
    create_niet_eigenperceelgroepen()


def get_bbox():
    #   Left, top, right, bottom
    #       code expects WSG84, if it is easier in the frontend this can change to RD
    return '4.894825,52.370680,4.898945,52.367797'