from datasets.brk import models

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
