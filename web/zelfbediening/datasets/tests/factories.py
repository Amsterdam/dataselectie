import string
import faker
import factory
import random
from factory import fuzzy
from django.contrib.gis.geos import Point
from datasets.bag import models


f = faker.Factory.create(locale='nl_NL')


# Creating a Point
class FuzzyPoint(fuzzy.BaseFuzzyAttribute):

    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0), random.uniform(-90.0, 90.0))


class NummeraanduidingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Nummeraanduiding


OBJECT_TYPE_VERBLIJFSOBJECT = '01'
OBJECT_TYPE_STANDPLAATS = '02'
OBJECT_TYPE_LIGPLAATS = '03'
OBJECT_TYPE_OVERIG_GEBOUWD = '04'
OBJECT_TYPE_OVERIG_TERREIN = '05'

OBJECT_TYPE_CHOICES = (
    (OBJECT_TYPE_VERBLIJFSOBJECT, 'Verblijfsobject'),
    (OBJECT_TYPE_STANDPLAATS, 'Standplaats'),
    (OBJECT_TYPE_LIGPLAATS, 'Ligplaats'),
    (OBJECT_TYPE_OVERIG_GEBOUWD, 'Overig gebouwd object'),
    (OBJECT_TYPE_OVERIG_TERREIN, 'Overig terrein'),
)

    id = fuzzy.FuzzyText(length=14)
    landelijk_id = fuzzy.FuzzyText(length=16)
    huisnummer = fuzzy.FuzzyInteger()
    huisletter = fuzzy.FuzzyText(length=1)
    huisnummer_toevoeging = fuzzy.FuzzyText(length=4)
    postcode = fuzzy.FuzzyText(length=6)
    type = fuzzy.FuzzyText(length=2, null=True, choices=OBJECT_TYPE_CHOICES)
    adres_nummer = models.CharField(max_length=10, null=True)
    vervallen = models.NullBooleanField(default=None)
    # bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    openbare_ruimte = models.ForeignKey(OpenbareRuimte, related_name='adressen')

    ligplaats = models.ForeignKey(
        'Ligplaats', null=True, related_name='adressen')
    standplaats = models.ForeignKey(
        'Standplaats', null=True, related_name='adressen')
    verblijfsobject = models.ForeignKey(
        'Verblijfsobject', null=True, related_name='adressen')

    hoofdadres = models.NullBooleanField(default=None)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, null=True)


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

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=4, chars=string.digits)


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
    naam = factory.LazyAttribute(lambda o: f.street_name())
    # @TODO make it an optional value
    type = '01'  # weg


class NummeraanduidingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Nummeraanduiding

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    huisnummer = factory.LazyAttribute(lambda o: int(f.building_number()))
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
