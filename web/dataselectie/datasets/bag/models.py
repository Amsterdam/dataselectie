from __future__ import annotations

from typing import Union, Optional

from django.contrib.gis.db import models as geo
from django.contrib.gis.geos import Point, Polygon
from django.contrib.postgres.fields import ArrayField
from django.db import models

from datasets.generic import model_mixins as mixins


class Gemeente(mixins.GeldigheidMixin, mixins.ImportStatusMixin, models.Model):
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=40)
    verzorgingsgebied = models.NullBooleanField(default=None)
    vervallen = models.NullBooleanField(default=None)

    class Meta(object):
        managed = False
        verbose_name = "Gemeente"
        verbose_name_plural = "Gemeentes"

    def __str__(self) -> str:
        return self.naam


class Woonplaats(
        mixins.GeldigheidMixin,
        mixins.ImportStatusMixin,
        mixins.DocumentStatusMixin, models.Model):

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=80)
    vervallen = models.NullBooleanField(default=None)
    gemeente = models.ForeignKey(Gemeente, related_name='woonplaatsen', on_delete=models.CASCADE)

    class Meta(object):
        managed = False
        verbose_name = "Woonplaats"
        verbose_name_plural = "Woonplaatsen"

    def __str__(self) -> str:
        return self.naam


class Hoofdklasse(mixins.ImportStatusMixin, models.Model):
    """
    De hoofdklasse is een abstracte klasse waar sommige andere
    gebiedsklassen, zoals stadsdeel en buurt, van afstammen.
    Deze afstammelingen erven alle kenmerken over van deze hoofdklasse.
    Het kenmerk 'diva_id' komt bijvoorbeeld voor
    bij alle gebieden.
    """

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    class Meta(object):
        managed = False
        abstract = True


class Stadsdeel(mixins.GeldigheidMixin, Hoofdklasse):
    """
    Door de Amsterdamse gemeenteraad vastgestelde begrenzing van
    een stadsdeel, ressorterend onder een stadsdeelbestuur.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/stadsdeel/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.NullBooleanField(default=None)
    ingang_cyclus = models.DateField(null=True)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    gemeente = models.ForeignKey(Gemeente, related_name='stadsdelen', on_delete=models.CASCADE)

    class Meta(object):
        managed = False
        verbose_name = "Stadsdeel"
        verbose_name_plural = "Stadsdelen"

    def __str__(self) -> str:
        return self.naam


class Buurt(mixins.GeldigheidMixin, Hoofdklasse):
    """
    Een aaneengesloten gedeelte van een buurt, waarvan de grenzen
    zo veel mogelijk gebaseerd zijn op topografische elementen.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurt/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    vollcode = models.CharField(max_length=4)
    naam = models.CharField(max_length=40)
    vervallen = models.NullBooleanField(default=None)
    ingang_cyclus = models.DateField(null=True)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    stadsdeel = models.ForeignKey(
        Stadsdeel, related_name='buurten', on_delete=models.CASCADE)

    buurtcombinatie = models.ForeignKey(
        'Buurtcombinatie', related_name='buurten',
        null=True, on_delete=models.CASCADE)

    gebiedsgerichtwerken = models.ForeignKey(
        'Gebiedsgerichtwerken', related_name='buurten',
        null=True, on_delete=models.CASCADE)

    class Meta:
        managed = False
        verbose_name = "Buurt"
        verbose_name_plural = "Buurten"
        ordering = ('vollcode',)

    def __str__(self):
        return "{} ({})".format(self.naam, self.vollcode)

    @property
    def _gemeente(self):
        return self.stadsdeel.gemeente


class Bouwblok(mixins.GeldigheidMixin, Hoofdklasse):
    """
    Een bouwblok is het kleinst mogelijk afgrensbare gebied, in
    zijn geheel tot een buurt behorend, dat geheel of
    grotendeels door bestaande of aan te leggen wegen en/of
    waterlopen is of zal zijn ingesloten en waarop tenminste
    één gebouw staat.

    https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/bouwblok/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)  # Bouwbloknummer
    buurt = models.ForeignKey(Buurt, related_name='bouwblokken', null=True, on_delete=models.CASCADE)
    ingang_cyclus = models.DateField(null=True)

    class Meta(object):
        managed = False
        verbose_name = "Bouwblok"
        verbose_name_plural = "Bouwblokken"
        ordering = ('code',)

    def __str__(self) -> str:
        return "{}".format(self.code)

    @property
    def _buurtcombinatie(self) -> models.Model:
        return self.buurt.buurtcombinatie if self.buurt else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None


class OpenbareRuimte(mixins.GeldigheidMixin,
                     mixins.ImportStatusMixin,
                     mixins.DocumentStatusMixin,
                     models.Model):
    """
    Een OPENBARE RUIMTE is een door het bevoegde gemeentelijke orgaan als
    zodanig aangewezen en van een naam voorziene
    buitenruimte die binnen één woonplaats is gelegen.

    Als openbare ruimte worden onder meer aangemerkt weg, water,
    terrein, spoorbaan en landschappelijk gebied.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-3/
    """
    TYPE_WEG = '01'
    TYPE_WATER = '02'
    TYPE_SPOORBAAN = '03'
    TYPE_TERREIN = '04'
    TYPE_KUNSTWERK = '05'
    TYPE_LANDSCHAPPELIJK_GEBIED = '06'
    TYPE_ADMINISTRATIEF_GEBIED = '07'

    TYPE_CHOICES = (
        (TYPE_WEG, 'Weg'),
        (TYPE_WATER, 'Water'),
        (TYPE_SPOORBAAN, 'Spoorbaan'),
        (TYPE_TERREIN, 'Terrein'),
        (TYPE_KUNSTWERK, 'Kunstwerk'),
        (TYPE_LANDSCHAPPELIJK_GEBIED, 'Landschappelijk gebied'),
        (TYPE_ADMINISTRATIEF_GEBIED, 'Administratief gebied'),
    )

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    type = models.CharField(max_length=2, null=True, choices=TYPE_CHOICES)
    naam = models.CharField(max_length=150)
    naam_nen = models.CharField(max_length=24)
    vervallen = models.NullBooleanField(default=None)
    # bron = models.ForeignKey(Bron, null=True)
    status = models.CharField(max_length=150)
    woonplaats = models.ForeignKey(Woonplaats, related_name="openbare_ruimtes", on_delete=models.CASCADE)
    geometrie = geo.MultiPolygonField(null=True, srid=28992)
    omschrijving = models.TextField(null=True)

    class Meta(object):
        managed = False
        verbose_name = "Openbare Ruimte"
        verbose_name_plural = "Openbare Ruimtes"
        ordering = ('naam', 'id')

    def __str__(self):
        return self.naam

    def dict_for_index(self, deep=True):
        """
        Converts the object into a dict to be indexed
        default is to also convert foreign key objects

        If deep is set to false, it will not add foreign key objects
        but instead add their ids
        """
        dct = {}
        for field in self._meta.fields:
            if field.get_internal_type() == 'ForeignKey':
                if deep:
                    pass
                else:
                    dct[field.name] = getattr(
                        self, '{}_id'.format(field.name), None)
            else:
                dct[field.name] = getattr(self, field.name, '')
        return dct


class Gebiedsgerichtwerken(mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM', 'CODE', 'STADSDEEL',
     'INGSDATUM', 'EINDDATUM', 'DOCNR', 'DOCDATUM']
    """

    id = models.CharField(max_length=4, primary_key=True)
    code = models.CharField(max_length=4)
    naam = models.CharField(max_length=100)
    stadsdeel = models.ForeignKey(
        Stadsdeel, related_name='gebiedsgerichtwerken', on_delete=models.CASCADE)

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    class Meta(object):
        managed = False
        verbose_name = "Gebiedsgerichtwerken"
        verbose_name_plural = "Gebiedsgerichtwerken"
        ordering = ('code',)

    def __str__(self):
        return "{} ({})".format(self.naam, self.code)


class Grootstedelijkgebied(mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM']
    """

    id = models.SlugField(max_length=100, primary_key=True)
    naam = models.CharField(max_length=100)
    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    class Meta(object):
        managed = False
        verbose_name = "Grootstedelijkgebied"
        verbose_name_plural = "Grootstedelijke gebieden"

    def __str__(self):
        return "{}".format(self.naam)


class Nummeraanduiding(mixins.GeldigheidMixin,
                       mixins.ImportStatusMixin, mixins.DocumentStatusMixin,
                       models.Model):
    """
    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door
    het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject,
    standplaats of ligplaats.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/
    """

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

    id = models.CharField(max_length=16, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    huisnummer = models.IntegerField(db_index=True)
    huisletter = models.CharField(max_length=1, null=True)
    huisnummer_toevoeging = models.CharField(max_length=4, null=True, db_index=True)
    postcode = models.CharField(max_length=6, null=True, db_index=True)
    type = models.CharField(max_length=2, null=True, choices=OBJECT_TYPE_CHOICES)
    vervallen = models.NullBooleanField(default=None)
    # bron = models.ForeignKey(Bron, null=True)
    status = models.CharField(max_length=150, null=True)
    openbare_ruimte = models.ForeignKey(OpenbareRuimte, related_name='adressen', on_delete=models.CASCADE)

    ligplaats = models.ForeignKey(
        'Ligplaats', null=True, related_name='adressen', on_delete=models.CASCADE)
    standplaats = models.ForeignKey(
        'Standplaats', null=True, related_name='adressen', on_delete=models.CASCADE)

    verblijfsobject = models.ForeignKey(
        'Verblijfsobject', null=True, related_name='adressen', on_delete=models.CASCADE)

    type_adres = models.TextField(null=True)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, null=True)

    class Meta(object):
        managed = False
        verbose_name = "Nummeraanduiding"
        verbose_name_plural = "Nummeraanduidingen"
        ordering = (
            '_openbare_ruimte_naam', 'huisnummer',
            'huisletter', 'huisnummer_toevoeging')
        index_together = (
            ('_openbare_ruimte_naam', 'huisnummer',
             'huisletter', 'huisnummer_toevoeging')
        )

    def __str__(self):
        return self.adres()

    def adres(self):
        return '%s %s' % (
            self._openbare_ruimte_naam, self._display_toevoeging())

    def dict_for_index(self, deep=True):
        """
        Converts the object into a dict to be indexed
        default is to also convert foreign key objects

        If deep is set to false, it will not add foreign key objects
        but instead add their ids
        """
        dct = {
            'postcode': "{} {}".format(
                self.postcode, self.toevoeging),
            'huisnummer': self.huisnummer,
        }
        if deep:
            # Creating a deep copy
            dct.update({
                'straatnaam': self.openbare_ruimte.naam,
                'straatnaam_nen': self.openbare_ruimte.naam_nen,
            })
        else:
            dct.update({
                'openbaar_ruimte': self.openbaar_ruimte_id
            })
        return dct

    def _display_toevoeging(self):

        toevoegingen = []

        toevoeging = self.huisnummer_toevoeging

        if self.huisnummer:
            toevoegingen.append(str(self.huisnummer))

        if self.huisletter:
            toevoegingen.append(str(self.huisletter))

        if toevoeging:
            toevoegingen.append('-%s' % toevoeging)
        return "".join(toevoegingen)

    @property
    def toevoeging(self):
        """Toevoeging samen voeging.

        Toevoeing represents the total added string to
        a street/openbareruimte name.
        """

        toevoegingen = []

        toevoeging = self.huisnummer_toevoeging

        if self.huisnummer:
            toevoegingen.append(str(self.huisnummer))

        if self.huisletter:
            toevoegingen.append(str(self.huisletter))

        def addnumber(lastdigits, split_tv):
            digits = "".join(lastdigits)
            if digits:
                split_tv.append(digits)

        if toevoeging:
            tv = str(toevoeging)
            split_tv = []
            lastdigits = []
            prev = ""

            for c in tv:
                if c.isdigit():
                    lastdigits.append(c)
                    continue
                else:
                    addnumber(lastdigits, split_tv)
                    lastdigits = []
                    split_tv.append(c)

            # add left-over digits if any.
            addnumber(lastdigits, split_tv)

            # create the toevoeging
            toevoegingen.extend(split_tv)

        return ' '.join(toevoegingen)

    @property
    def adresseerbaar_object(self) -> Union[Ligplaats, Standplaats, Verblijfsobject]:
        return self.ligplaats or self.standplaats or self.verblijfsobject

    @property
    def vbo_status(self) -> Optional[str]:
        a = self.adresseerbaar_object
        return a.status if a else None

    @property
    def buurt(self) -> Optional[Buurt]:
        a = self.adresseerbaar_object
        return a.buurt if a else None

    @property
    def _geometrie(self) -> Optional[Union[Polygon, Point]]:
        a = self.adresseerbaar_object
        return a.geometrie if a else None

    @property
    def stadsdeel(self) -> Optional[Stadsdeel]:
        b = self.buurt
        return b.stadsdeel if b else None

    @property
    def woonplaats(self) -> Optional[Woonplaats]:
        o = self.openbare_ruimte
        return o.woonplaats if o else None

    @property
    def buurtcombinatie(self) -> Optional[Buurtcombinatie]:
        b = self.buurt
        return b.buurtcombinatie if b else None

    @property
    def bouwblok(self) -> Optional[Bouwblok]:
        return self.verblijfsobject.bouwblok if self.verblijfsobject else None

    @property
    def gemeente(self) -> Optional[Gemeente]:
        s = self.stadsdeel
        return s.gemeente if s else None

    @property
    def gebiedsgerichtwerken(self) -> Optional[Gebiedsgerichtwerken]:
        a = self.adresseerbaar_object
        return a._gebiedsgerichtwerken if a else None

    @property
    def grootstedelijkgebied(self) -> Optional[Grootstedelijkgebied]:
        a = self.adresseerbaar_object
        return a._grootstedelijkgebied if a else None


class AdresseerbaarObjectMixin(object):
    @property
    def hoofdadres(self):
        # noinspection PyUnresolvedReferences
        candidates = [a for a in self.adressen.all() if a.type_adres == 'Hoofdadres']
        return candidates[0] if candidates else None

    @property
    def nevenadressen(self):
        # noinspection PyUnresolvedReferences
        return [a for a in self.adressen.all() if not a.type_adres == 'Hoofdadres']

    def __str__(self):
        # Fetch once as this evaluates an 1..M relation:
        hoofdadres = self.hoofdadres
        if hoofdadres:
            return hoofdadres.adres()
        return "adres onbekend"


class Ligplaats(mixins.GeldigheidMixin,
                mixins.ImportStatusMixin,
                mixins.DocumentStatusMixin,
                AdresseerbaarObjectMixin,
                models.Model):
    """
    Een LIGPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig
    aangewezen plaats in het water al dan niet aangevuld met een op de
    oever aanwezig terrein of een gedeelte daarvan, die bestemd is voor
    het permanent afmeren van een voor woon-, bedrijfsmatige of
    recreatieve doeleinden geschikt vaartuig.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-1/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    vervallen = models.NullBooleanField(default=None)
    status = models.CharField(max_length=150)
    buurt = models.ForeignKey(
        Buurt, null=True, related_name='ligplaatsen',
        on_delete=models.CASCADE
    )

    _gebiedsgerichtwerken = models.ForeignKey(
        Gebiedsgerichtwerken, related_name='ligplaatsen', null=True,
        on_delete=models.CASCADE
    )

    _grootstedelijkgebied = models.ForeignKey(
        Grootstedelijkgebied, related_name='ligplaatsen', null=True,
        on_delete=models.CASCADE
    )

    geometrie = geo.PolygonField(null=True, srid=28992)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, null=True)
    _huisnummer = models.IntegerField(null=True)
    _huisletter = models.CharField(max_length=1, null=True)
    _huisnummer_toevoeging = models.CharField(max_length=4, null=True)

    class Meta(object):
        managed = False
        verbose_name = "Ligplaats"
        verbose_name_plural = "Ligplaatsen"
        ordering = (
            '_openbare_ruimte_naam', '_huisnummer',
            '_huisletter', '_huisnummer_toevoeging')

        index_together = [
            ('_openbare_ruimte_naam', '_huisnummer',
             '_huisletter', '_huisnummer_toevoeging')
        ]

    def __str__(self):

        result = '{} {}'.format(self._openbare_ruimte_naam, self._huisnummer)
        if self._huisletter:
            result += self._huisletter
        if self._huisnummer_toevoeging:
            result += ' ' + self._huisnummer_toevoeging
        return result

    @property
    def _buurtcombinatie(self):
        return self.buurt.buurtcombinatie if self.buurt else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None

    @property
    def _woonplaats(self):
        return self.hoofdadres.woonplaats if self.hoofdadres else None


class Standplaats(mixins.GeldigheidMixin,
                  mixins.ImportStatusMixin,
                  mixins.DocumentStatusMixin,
                  AdresseerbaarObjectMixin,
                  models.Model):
    """
    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig
    aangewezen terrein of gedeelte daarvan dat bestemd is voor het permanent
    plaatsen van een niet direct en niet duurzaam met de aarde verbonden en
    voor woon-, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    vervallen = models.NullBooleanField(default=None)
    status = models.CharField(max_length=150)
    buurt = models.ForeignKey(
        Buurt, null=True, related_name='standplaatsen',
        on_delete=models.CASCADE
    )

    _gebiedsgerichtwerken = models.ForeignKey(
        Gebiedsgerichtwerken, related_name='standplaatsen', null=True,
        on_delete=models.CASCADE
    )

    _grootstedelijkgebied = models.ForeignKey(
        Grootstedelijkgebied, related_name='standplaatsen', null=True,
        on_delete=models.CASCADE
    )

    geometrie = geo.PolygonField(null=True, srid=28992)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, null=True)
    _huisnummer = models.IntegerField(null=True)
    _huisletter = models.CharField(max_length=1, null=True)
    _huisnummer_toevoeging = models.CharField(max_length=4, null=True)

    class Meta(object):
        managed = False
        verbose_name = "Standplaats"
        verbose_name_plural = "Standplaatsen"
        ordering = (
            '_openbare_ruimte_naam', '_huisnummer',
            '_huisletter', '_huisnummer_toevoeging')
        index_together = [
            ('_openbare_ruimte_naam', '_huisnummer',
             '_huisletter', '_huisnummer_toevoeging')
        ]

    def __str__(self):
        result = '{} {}'.format(self._openbare_ruimte_naam, self._huisnummer)
        if self._huisletter:
            result += self._huisletter
        if self._huisnummer_toevoeging:
            result += ' ' + self._huisnummer_toevoeging
        return result

    @property
    def _buurtcombinatie(self):
        return self.buurt.buurtcombinatie if self.buurt_id else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt_id else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None

    @property
    def _woonplaats(self):
        return self.hoofdadres.woonplaats if self.hoofdadres else None


class Verblijfsobject(mixins.GeldigheidMixin,
                      mixins.ImportStatusMixin,
                      mixins.DocumentStatusMixin,
                      AdresseerbaarObjectMixin,
                      models.Model):
    """
    Een VERBLIJFSOBJECT is de kleinste binnen één of meer panden gelegen en
    voor woon-, bedrijfsmatige, of recreatieve
    doeleinden geschikte eenheid van gebruik die ontsloten wordt via een eigen
    afsluitbare toegang vanaf de openbare weg, een erf of een gedeelde
    verkeersruimte, onderwerp kan zijn van goederenrechtelijke
    rechtshandelingen en in functioneel opzicht zelfstandig is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-0/
    """

    id = models.CharField(max_length=16, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    oppervlakte = models.PositiveIntegerField(null=True)
    verdieping_toegang = models.IntegerField(null=True)
    aantal_eenheden_complex = models.PositiveIntegerField(null=True)
    bouwlagen = models.PositiveIntegerField(null=True)
    hoogste_bouwlaag = models.IntegerField(null=True)
    laagste_bouwlaag = models.IntegerField(null=True)
    aantal_kamers = models.PositiveIntegerField(null=True)
    vervallen = models.PositiveIntegerField(default=False)
    reden_opvoer = models.TextField(null=True)
    reden_afvoer = models.TextField(null=True)
    eigendomsverhouding = models.TextField(null=True)
    gebruik = models.TextField(null=True)
    gebruiksdoel_woonfunctie = models.TextField(null=True)
    gebruiksdoel_gezondheidszorgfunctie = models.TextField(null=True)
    toegang = ArrayField(models.CharField(max_length=150))
    gebruiksdoel = ArrayField(models.TextField())
    status = models.CharField(max_length=150)
    buurt = models.ForeignKey(
        Buurt, null=True, related_name='verblijfsobjecten',
        on_delete=models.CASCADE
    )

    panden = models.ManyToManyField(
        'Pand', related_name='verblijfsobjecten',
        through='VerblijfsobjectPandRelatie')

    geometrie = geo.PointField(null=True, srid=28992)

    _gebiedsgerichtwerken = models.ForeignKey(
        Gebiedsgerichtwerken, related_name='adressen', null=True,
        on_delete=models.CASCADE
    )

    _grootstedelijkgebied = models.ForeignKey(
        Grootstedelijkgebied, related_name='adressen', null=True,
        on_delete=models.CASCADE
    )

    indicatie_geconstateerd = models.NullBooleanField(default=None)
    indicatie_in_onderzoek = models.NullBooleanField(default=None)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, db_index=True, null=True)
    _huisnummer = models.IntegerField(null=True, db_index=True)
    _huisletter = models.CharField(max_length=1, null=True)
    _huisnummer_toevoeging = models.CharField(max_length=4, null=True)

    class Meta(object):
        managed = False
        verbose_name = "Verblijfsobject"
        verbose_name_plural = "Verblijfsobjecten"
        ordering = (
            '_openbare_ruimte_naam', '_huisnummer',
            '_huisletter', '_huisnummer_toevoeging')
        index_together = [
            (
                '_openbare_ruimte_naam', '_huisnummer',
                '_huisletter', '_huisnummer_toevoeging')
        ]

    def __str__(self):
        result = '{} {}'.format(self._openbare_ruimte_naam, self._huisnummer)
        if self._huisletter:
            result += self._huisletter
        if self._huisnummer_toevoeging:
            result += '-' + self._huisnummer_toevoeging
        return result

    # store pand for bouwblok reference
    _pand = ...

    @property
    def willekeurig_pand(self):
        """
        Geeft het pand van dit verblijfsobject. Indien er meerdere
        panden zijn, wordt een willekeurig pand gekozen.
        """
        if self._pand is ...:
            try:
                # If there is a .prefetch_related() for panden, use that.
                # Otherwise, the attribute doesn't exist
                panden = self._prefetched_objects_cache['panden']
            except (AttributeError, LookupError):
                # Trying a query is less expensive then doing a .count()!
                panden = self.panden.select_related('bouwblok')

            try:
                self._pand = panden[0]
            except IndexError:
                self._pand = None

        return self._pand

    @property
    def bouwblok(self):
        if not self.willekeurig_pand:
            return None

        return self.willekeurig_pand.bouwblok

    @property
    def _buurtcombinatie(self):
        return self.buurt.buurtcombinatie if self.buurt_id else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt_id else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None

    @property
    def _woonplaats(self):
        return self.hoofdadres.woonplaats if self.hoofdadres else None


class Pand(
        mixins.GeldigheidMixin,
        mixins.ImportStatusMixin,
        mixins.DocumentStatusMixin,
        models.Model):
    """
    Een PAND is de kleinste bij de totstandkoming functioneel en
    bouwkundig-constructief zelfstandige eenheid die direct
    en duurzaam met de aarde is verbonden en betreedbaar en
    afsluitbaar is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/
    """

    id = models.CharField(max_length=16, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    bouwjaar = models.PositiveIntegerField(null=True)  # can be 1005 which means none!
    bouwlagen = models.PositiveIntegerField(null=True)
    laagste_bouwlaag = models.IntegerField(null=True)
    hoogste_bouwlaag = models.IntegerField(null=True)
    vervallen = models.NullBooleanField(default=None)
    status = models.CharField(max_length=150, null=True)

    bouwblok = models.ForeignKey(
        Bouwblok, null=True, related_name="panden", on_delete=models.CASCADE)

    geometrie = geo.PolygonField(null=True, srid=28992)

    pandnaam = models.CharField(max_length=250, null=True)  # e.g. "Centraal station"

    ligging = models.TextField(null=True)
    type_woonobject = models.CharField(max_length=25, null=True)

    class Meta(object):
        managed = False
        verbose_name = "Pand"
        verbose_name_plural = "Panden"

    def __str__(self):
        return "{}".format(self.landelijk_id)

    @property
    def _buurt(self):
        return self.bouwblok.buurt if self.bouwblok_id else None

    @property
    def _buurtcombinatie(self):
        return self._buurt.buurtcombinatie if self._buurt else None

    @property
    def _stadsdeel(self):
        return self._buurt.stadsdeel if self._buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None


class VerblijfsobjectPandRelatie(mixins.ImportStatusMixin, models.Model):
    id = models.CharField(max_length=29, primary_key=True)
    pand = models.ForeignKey(Pand, on_delete=models.CASCADE)
    verblijfsobject = models.ForeignKey(Verblijfsobject, on_delete=models.CASCADE)

    class Meta(object):
        managed = False
        verbose_name = "Verblijfsobject-Pand relatie"
        verbose_name_plural = "Verblijfsobject-Pand relaties"

    def __init__(self, *args, **kwargs):
        super(VerblijfsobjectPandRelatie, self).__init__(*args, **kwargs)

        if self.pand_id and self.verblijfsobject_id:
            self.id = '{pid}_{vid}'.format(pid=self.pand_id,
                                           vid=self.verblijfsobject_id)

    def __str__(self):
        return "Pand-Verblijfsobject({}-{})".format(
            self.pand_id, self.verblijfsobject_id)


class Buurtcombinatie(
        mixins.GeldigheidMixin, mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['ID', 'NAAM', 'CODE', 'VOLLCODE', 'DOCNR', 'DOCDATUM',
     'INGSDATUM', 'EINDDATUM']
    """

    id = models.CharField(max_length=14, primary_key=True)
    naam = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    vollcode = models.CharField(max_length=3)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    ingang_cyclus = models.DateField(null=True)

    stadsdeel = models.ForeignKey(
        Stadsdeel, null=True, related_name="buurtcombinaties",
        on_delete=models.CASCADE
    )

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    class Meta(object):
        managed = False
        verbose_name = "Buurtcombinatie"
        verbose_name_plural = "Buurtcombinaties"
        ordering = ('code',)

    def __str__(self):
        return "{} ({})".format(self.naam, self.code)

    def _gemeente(self):
        return self.stadsdeel.gemeente


class Unesco(mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM']
    """

    id = models.SlugField(max_length=100, primary_key=True)
    naam = models.CharField(max_length=100)
    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    class Meta(object):
        managed = False
        verbose_name = "Unesco"
        verbose_name_plural = "Unesco"

    def __str__(self):
        return "{}".format(self.naam)


def prefetch_adresseerbaar_objects(relation=None):
    """
    Return all prefetch fields to index "NummerAanduiding.adresseerbaarobject.

    This expands to various things like "ligplaats", "standplaats" and "verblijfobject"
    because one of these is returned by `NummerAanduiding.adresseerbaar_object`.

    :param relation: This can be "nummeraanduiding" when the object is references by another.

    When the "relation=nummeraanduiding" is passed, the returned
    value resembles the following prefetch_related() list::

        [
            'nummeraanduiding',
            'nummeraanduiding__ligplaats',
            'nummeraanduiding__ligplaats__buurt',
            'nummeraanduiding__ligplaats__buurt__buurtcombinatie',
            'nummeraanduiding__ligplaats__buurt__stadsdeel',
            'nummeraanduiding__ligplaats___gebiedsgerichtwerken',
            'nummeraanduiding__ligplaats___grootstedelijkgebied',
            'nummeraanduiding__standplaats',
            'nummeraanduiding__standplaats__buurt',
            'nummeraanduiding__standplaats__buurt__buurtcombinatie',
            'nummeraanduiding__standplaats__buurt__stadsdeel',
            'nummeraanduiding__standplaats___gebiedsgerichtwerken',
            'nummeraanduiding__standplaats___grootstedelijkgebied',
            'nummeraanduiding__verblijfsobject',
            'nummeraanduiding__verblijfsobject__buurt',
            'nummeraanduiding__verblijfsobject__buurt__buurtcombinatie',
            'nummeraanduiding__verblijfsobject__buurt__stadsdeel',
            'nummeraanduiding__verblijfsobject___gebiedsgerichtwerken',
            'nummeraanduiding__verblijfsobject___grootstedelijkgebied',
        ]

    ...but without geometry fields querying using the django `Prefetch()` object.
    """
    # The Prefetch() objects further limit the results to avoid fetching unneeded geo data.
    prefetches = []
    for child_relation in ('standplaats', 'ligplaats', 'verblijfsobject'):
        prefix = f"{relation}__{child_relation}" if relation else child_relation
        prefetches.extend([
            f'{prefix}',
            f'{prefix}__buurt',
            models.Prefetch(
                f'{prefix}__buurt__buurtcombinatie',
                queryset=Buurtcombinatie.objects.defer('geometrie')
            ),
            f'{prefix}__buurt__stadsdeel',
            models.Prefetch(
                f'{prefix}___gebiedsgerichtwerken',
                queryset=Gebiedsgerichtwerken.objects.defer('geometrie'),
            ),
            models.Prefetch(
                f'{prefix}___grootstedelijkgebied',
                queryset=Grootstedelijkgebied.objects.defer('geometrie'),
            ),
        ])

    return prefetches
