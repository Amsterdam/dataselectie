import random
import string

from factory import DjangoModelFactory, fuzzy
from factory.declarations import SubFactory, LazyAttribute
from faker import Factory
from django.contrib.gis.geos import Point

from datasets.bag import models

faker_instance = Factory.create(locale='nl_NL')


# Creating a Point
class FuzzyPoint(fuzzy.BaseFuzzyAttribute):
    def fuzz(self):
        return Point(
            random.uniform(-180.0, 180.0), random.uniform(-90.0, 90.0))


class EigendomsverhoudingFactory(DjangoModelFactory):
    class Meta:
        model = models.Eigendomsverhouding

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class RedenAfvoerFactory(DjangoModelFactory):
    class Meta:
        model = models.RedenAfvoer

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class RedenOpvoerFactory(DjangoModelFactory):
    class Meta:
        model = models.RedenOpvoer

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class FinancieringswijzeFactory(DjangoModelFactory):
    class Meta:
        model = models.Financieringswijze

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class GebruikFactory(DjangoModelFactory):
    class Meta:
        model = models.Gebruik

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)

class LiggingFactory(DjangoModelFactory):
    class Meta:
        model = models.Ligging

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class StatusFactory(DjangoModelFactory):
    class Meta:
        model = models.Status

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class GemeenteFactory(DjangoModelFactory):
    class Meta:
        model = models.Gemeente
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyInteger(low=1, high=994444)
    code = fuzzy.FuzzyText(length=4)
    naam = 'Amsterdam'


class BuurtcombinatieFactory(DjangoModelFactory):
    class Meta:
        model = models.Buurtcombinatie
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=2)
    vollcode = fuzzy.FuzzyText(length=3)


class StadsdeelFactory(DjangoModelFactory):
    class Meta:
        model = models.Stadsdeel
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    gemeente = SubFactory(GemeenteFactory)


class BuurtFactory(DjangoModelFactory):
    class Meta:
        model = models.Buurt
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    stadsdeel = SubFactory(StadsdeelFactory)
    buurtcombinatie = SubFactory(BuurtcombinatieFactory)


class LigplaatsFactory(DjangoModelFactory):
    class Meta:
        model = models.Ligplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = id
    buurt = SubFactory(BuurtFactory)


class StandplaatsFactory(DjangoModelFactory):
    class Meta:
        model = models.Standplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = id
    buurt = SubFactory(BuurtFactory)


class VerblijfsobjectFactory(DjangoModelFactory):
    class Meta:
        model = models.Verblijfsobject

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    reden_afvoer = SubFactory(RedenAfvoerFactory)
    reden_opvoer = SubFactory(RedenOpvoerFactory)
    buurt = SubFactory(BuurtFactory)


class WoonplaatsFactory(DjangoModelFactory):
    class Meta:
        model = models.Woonplaats
        django_get_or_create = ('landelijk_id',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=4, chars=string.digits)
    gemeente = SubFactory(GemeenteFactory)


class OpenbareRuimteFactory(DjangoModelFactory):
    class Meta:
        model = models.OpenbareRuimte
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    code = fuzzy.FuzzyText(length=5, chars=string.digits)
    woonplaats = SubFactory(WoonplaatsFactory)
    naam = LazyAttribute(lambda o: faker_instance.street_name())
    # @TODO make it an optional value
    type = '01'  # weg


class NummeraanduidingFactory(DjangoModelFactory):
    class Meta:
        model = models.Nummeraanduiding

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    huisnummer = LazyAttribute(
        lambda o: int(faker_instance.building_number()))
    openbare_ruimte = SubFactory(OpenbareRuimteFactory)
    verblijfsobject = SubFactory(VerblijfsobjectFactory)
    type = '01'  # default verblijfsobject
    postcode = '1000AN'  # default postcode..

    _openbare_ruimte_naam = LazyAttribute(
        lambda o: o.openbare_ruimte.naam)


class GrootstedelijkGebiedFactory(DjangoModelFactory):
    class Meta:
        model = models.Grootstedelijkgebied

    naam = fuzzy.FuzzyText(length=50)


class UnescoFactory(DjangoModelFactory):
    class Meta:
        model = models.Unesco

    naam = fuzzy.FuzzyText(length=50)


class GebiedsgerichtwerkenFactory(DjangoModelFactory):
    class Meta:
        model = models.Gebiedsgerichtwerken
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=4)
    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=4)
    stadsdeel = SubFactory(StadsdeelFactory)
