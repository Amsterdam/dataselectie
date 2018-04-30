import logging

from datasets.brk import models
from django.db import connection
from datasets.brk.management import brk_batch_sql

log = logging.getLogger(__name__)


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


def get_bbox():
    #   Left, top, right, bottom - code expects WSG84, if required this can change to RD
    return '4.894825,52.370680,4.898945,52.367797'