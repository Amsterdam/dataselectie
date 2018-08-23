import json
import logging

import factory
import faker
from django.contrib.gis.geos import MultiPolygon, Polygon, Point
from django.db import connection
from factory import fuzzy

from datasets.bag.tests.fixture_utils import create_stadsdeel_fixtures, create_gebiedsgericht_werken_fixtures
from datasets.brk import geo_models
from datasets.brk import models
from datasets.brk.management import brk_batch_sql
from datasets.brk.models import EigendomStadsdeel
from datasets.generic import kadaster
from .fixtures_geometrie import perceel_geometrie, appartement_plot, stadsdeel_noord_en_centrum_plot, \
    midden_op_het_ij_point

log = logging.getLogger(__name__)

SRID_WSG84 = 4326
SRID_RD = 28992

f = faker.Factory.create(locale='nl_NL')


def random_poly():
    return MultiPolygon(
        Polygon(
            ((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))))


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente
        django_get_or_create = ('gemeente',)

    gemeente = factory.LazyAttribute(lambda o: f.city())
    geometrie = random_poly()


class KadastraleGemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraleGemeente

    pk = fuzzy.FuzzyText(length=5)
    gemeente = factory.SubFactory(GemeenteFactory)
    geometrie = random_poly()


class KadastraleSectieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraleSectie

    pk = fuzzy.FuzzyText(length=60)
    sectie = fuzzy.FuzzyText(length=1)
    kadastrale_gemeente = factory.SubFactory(KadastraleGemeenteFactory)
    geometrie = random_poly()


class KadastraalObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.KadastraalObject

    pk = fuzzy.FuzzyText(length=60)
    aanduiding = factory.LazyAttribute(
        lambda obj: kadaster.get_aanduiding(
            obj.kadastrale_gemeente.id,
            obj.sectie.sectie,
            obj.perceelnummer,
            obj.indexletter,
            obj.indexnummer))

    kadastrale_gemeente = factory.SubFactory(KadastraleGemeenteFactory)
    sectie = factory.SubFactory(KadastraleSectieFactory)
    perceelnummer = fuzzy.FuzzyInteger(low=0, high=9999)
    indexletter = fuzzy.FuzzyChoice(choices=('A', 'G'))
    indexnummer = fuzzy.FuzzyInteger(low=0, high=9999)
    grootte = fuzzy.FuzzyInteger(low=10, high=1000)
    register9_tekst = fuzzy.FuzzyText(length=50)
    poly_geom = random_poly()


class AdresFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Adres

    pk = fuzzy.FuzzyText(length=32)
    openbareruimte_naam = fuzzy.FuzzyText(length=80)


# class NatuurlijkPersoonFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = models.KadastraalSubject
#
#     pk = fuzzy.FuzzyText(length=60)
#     type = models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK
#     bron = fuzzy.FuzzyChoice(
#         choices=(models.KadastraalSubject.BRON_KADASTER,
#                  models.KadastraalSubject.BRON_REGISTRATIE))
#     woonadres = factory.SubFactory(AdresFactory)
#     postadres = factory.SubFactory(AdresFactory)
#
#
# class NietNatuurlijkPersoonFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = models.KadastraalSubject
#
#     pk = fuzzy.FuzzyText(length=60)
#     type = models.KadastraalSubject.SUBJECT_TYPE_NIET_NATUURLIJK
#     bron = fuzzy.FuzzyChoice(choices=(
#         models.KadastraalSubject.BRON_KADASTER,
#         models.KadastraalSubject.BRON_REGISTRATIE))
#     woonadres = factory.SubFactory(AdresFactory)
#     postadres = factory.SubFactory(AdresFactory)


class EigenaarFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Eigenaar

    pk = fuzzy.FuzzyText(length=60)
    type = fuzzy.FuzzyChoice(
        choices=(models.Eigenaar.SUBJECT_TYPE_NATUURLIJK,
                 models.Eigenaar.SUBJECT_TYPE_NIET_NATUURLIJK))
    bron = fuzzy.FuzzyChoice(
        choices=(models.Eigenaar.BRON_KADASTER,
                 models.Eigenaar.BRON_REGISTRATIE))
    woonadres = factory.SubFactory(AdresFactory)
    postadres = factory.SubFactory(AdresFactory)


class AardZakelijkRechtFactory(factory.DjangoModelFactory):
    pk = fuzzy.FuzzyText(length=10)

    class Meta:
        model = models.AardZakelijkRecht


class ZakelijkRechtFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ZakelijkRecht

    pk = fuzzy.FuzzyText(length=60)
    kadastraal_object = factory.SubFactory(KadastraalObjectFactory)
    kadastraal_subject = factory.SubFactory(EigenaarFactory)

    _kadastraal_subject_naam = fuzzy.FuzzyText(length=50)
    kadastraal_object_status = fuzzy.FuzzyText(length=50)
    aard_zakelijk_recht = factory.SubFactory(AardZakelijkRechtFactory)


def create_eigendom_stadsdelen_objects(kadastraal_object):
    stadsdelen = create_stadsdeel_fixtures()
    eigendom_stadsdelen = []
    for stadsdeel in stadsdelen:
        eigendom_stadsdeel = EigendomStadsdeel.objects.get_or_create(
            kadastraal_object=kadastraal_object,
            stadsdeel=stadsdeel[0])
        # eigendom_stadsdeel[0].save()
        # eigendom_stadsdelen.append(eigendom_stadsdeel)
    return eigendom_stadsdelen


class EigendomStadsdeelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.EigendomStadsdeel


def create_kadastraal_object():
    """
    depends on kadastrale gemeente / kadastrale sectie
    :return: A list of kot fixtures
    """

    gemeente = GemeenteFactory(
        gemeente='SunCity',
    )

    kadastrale_gemeente = KadastraleGemeenteFactory(
        pk='AX001',
        gemeente=gemeente,
        naam='SunCity',
    )

    sectie = KadastraleSectieFactory(
        sectie='S'
    )

    kadastraal_object = KadastraalObjectFactory(
        kadastrale_gemeente=kadastrale_gemeente,
        perceelnummer=12,  # must be 5 long!
        indexletter='G',
        indexnummer=23,
        sectie=sectie,
        soort_grootte_id='SBCD',
        register9_tekst='12345789',
        status_code='X3',
        poly_geom=stadsdeel_noord_en_centrum_plot,
        point_geom=midden_op_het_ij_point
    )

    eigendom_stadsdelen = create_eigendom_stadsdelen_objects(kadastraal_object)

    return kadastraal_object


def create_eigendom():
    """
    depends on kadastraal object and categroie fixtures
    :return: a list of eigendom objects
    """
    create_eigenaar_categorie()
    kadastraal_object = create_kadastraal_object()
    kadastraal_subject = EigenaarFactory.create()
    zakelijkrecht = ZakelijkRechtFactory.create()

    return [

        models.Eigendom.objects.get_or_create(
            zakelijk_recht=zakelijkrecht,
            kadastraal_subject=kadastraal_subject,
            kadastraal_object=kadastraal_object,
            eigenaar_categorie_id=3,
            grondeigenaar=False,
            aanschrijfbaar=False,
            appartementeigenaar=True,
        )
    ]


def create_eigenaar_categorie():
    return [
        models.EigenaarCategorie.objects.get_or_create(
            id=1,
            categorie='Amsterdam',
        ),
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


def create_appartementen(kot):
    appartement_centroid = Point(4.895, 52.368, srid=SRID_WSG84)

    return [
        geo_models.Appartementen.objects.get_or_create(
            id=1,
            cat_id=3,
            eigendom_cat=3,
            kadastraal_object=kot,
            geometrie=appartement_centroid,
            plot=appartement_plot,
            aantal=2
        ),
        geo_models.Appartementen.objects.get_or_create(
            id=2,
            cat_id=3,
            eigendom_cat=9,
            kadastraal_object=kot,
            geometrie=appartement_centroid,
            plot=appartement_plot,
            aantal=2
        ),
        geo_models.Appartementen.objects.get_or_create(
            id=3,
            cat_id=99,
            eigendom_cat=3,
            kadastraal_object=kot,
            geometrie=appartement_centroid,
            plot=appartement_plot,
            aantal=2
        ),
        geo_models.Appartementen.objects.get_or_create(
            id=4,
            cat_id=99,
            eigendom_cat=9,
            kadastraal_object=kot,
            geometrie=appartement_centroid,
            plot=appartement_plot,
            aantal=2
        )

    ]


def create_eigenpercelen(kot):
    return [
        geo_models.EigenPerceel.objects.get_or_create(
            id=1,
            cat_id=3,
            eigendom_cat=1,
            kadastraal_object=kot,
            geometrie=perceel_geometrie[1],
        ),
        geo_models.EigenPerceel.objects.get_or_create(
            id=2,
            cat_id=3,
            eigendom_cat=9,
            kadastraal_object=kot,
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


def create_niet_eigenpercelen(kot):
    return [
        geo_models.NietEigenPerceel.objects.get_or_create(
            id=1,
            cat_id=3,
            eigendom_cat=3,
            kadastraal_object=kot,
            geometrie=appartement_plot,
        ),
        geo_models.NietEigenPerceel.objects.get_or_create(
            id=2,
            cat_id=3,
            eigendom_cat=9,
            kadastraal_object=kot,
            geometrie=appartement_plot,
        ),
        geo_models.NietEigenPerceel.objects.get_or_create(
            id=3,
            cat_id=99,
            eigendom_cat=3,
            kadastraal_object=kot,
            geometrie=appartement_plot,
        ),
        geo_models.NietEigenPerceel.objects.get_or_create(
            id=4,
            cat_id=99,
            eigendom_cat=9,
            kadastraal_object=kot,
            geometrie=appartement_plot,
        ),
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


def create_geo_data(kot):
    create_appartementen(kot)
    create_eigenpercelen(kot)
    create_eigenperceelgroepen()
    create_niet_eigenpercelen(kot)
    create_niet_eigenperceelgroepen()


def get_selection_shape():
    return '[[4.8923386,52.36911],[4.8948249,52.3692279],[4.8964193,52.3683213],' \
           '[4.8956741,52.3677415],[4.8940659,52.3672713],[4.8928666,52.3683111]]'


def get_bbox_leaflet():
    # get the leaflet-like LatLngBounds
    return json.dumps({
        '_northEast': {
            'lat': 52.37068,
            'lng': 4.894825
        },
        '_southWest': {
            'lat': 52.367797,
            'lng': 4.898945
        }
    })


def get_bbox():
    #   Left, top, right, bottom
    #       code expects WSG84, if it is easier in the frontend this can change to RD
    return '4.894825,52.370680,4.898945,52.367797'
