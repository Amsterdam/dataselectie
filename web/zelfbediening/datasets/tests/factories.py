import random
import string

import factory
import faker
from django.contrib.gis.geos import Point
from factory import fuzzy

from datasets.bag import models

faker_instance = faker.Factory.create(locale='nl_NL')


# Creating a Point
class FuzzyPoint(fuzzy.BaseFuzzyAttribute):

    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0), random.uniform(-90.0, 90.0))


class EigendomsverhoudingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Eigendomsverhouding

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class RedenAfvoerFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.RedenAfvoer

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class RedenOpvoerFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.RedenOpvoer

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class FinancieringswijzeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Financieringswijze

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class GebruikFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gebruik

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class LiggingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Ligging

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class StatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Status

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyInteger(low=44444, high=54444, step=1)
    code = fuzzy.FuzzyText(length=4)
    naam = 'Amsterdam'


class BuurtcombinatieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurtcombinatie
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=2)
    vollcode = fuzzy.FuzzyText(length=3)


class StadsdeelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Stadsdeel
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class BuurtFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurt
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    stadsdeel = factory.SubFactory(StadsdeelFactory)
    buurtcombinatie = factory.SubFactory(BuurtcombinatieFactory)


class LigplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Ligplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = id
    buurt = factory.SubFactory(BuurtFactory)


class StandplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Standplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = id
    buurt = factory.SubFactory(BuurtFactory)


class VerblijfsobjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Verblijfsobject

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    reden_afvoer = factory.SubFactory(RedenAfvoerFactory)
    reden_opvoer = factory.SubFactory(RedenOpvoerFactory)
    buurt = factory.SubFactory(BuurtFactory)


class WoonplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Woonplaats
        django_get_or_create = ('landelijk_id',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=4, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class OpenbareRuimteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OpenbareRuimte
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    code = fuzzy.FuzzyText(length=5, chars=string.digits)
    woonplaats = factory.SubFactory(WoonplaatsFactory)
    naam = factory.LazyAttribute(lambda o: faker_instance.street_name())
    # @TODO make it an optional value
    type = '01'  # weg


class NummeraanduidingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Nummeraanduiding

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    huisnummer = factory.LazyAttribute(lambda o: int(faker_instance.building_number()))
    openbare_ruimte = factory.SubFactory(OpenbareRuimteFactory)
    verblijfsobject = factory.SubFactory(VerblijfsobjectFactory)
    type = '01'  # default verblijfsobject
    postcode = '1000AN'  # default postcode..

    _openbare_ruimte_naam = factory.LazyAttribute(lambda o: o.openbare_ruimte.naam)


class GrootstedelijkGebiedFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Grootstedelijkgebied

    naam = fuzzy.FuzzyText(length=50)


class UnescoFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Unesco

    naam = fuzzy.FuzzyText(length=50)


class GebiedsgerichtwerkenFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gebiedsgerichtwerken
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=4)
    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=4)
    stadsdeel = factory.SubFactory(StadsdeelFactory)
