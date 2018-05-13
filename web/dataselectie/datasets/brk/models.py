import uuid

from django.contrib.gis.db import models as geo
from django.db import models

from datasets.bag import models as bag
from datasets.generic import kadaster


class Gemeente(models.Model):
    gemeente = models.CharField(max_length=50, primary_key=True)

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.Manager()

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gemeente"
        verbose_name_plural = "Gemeentes"
        managed = False

    def __str__(self):
        return "{}".format(self.gemeente)


class KadastraleGemeente(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    naam = models.CharField(max_length=100)
    gemeente = models.ForeignKey(
        Gemeente, related_name="kadastrale_gemeentes",
        on_delete=models.CASCADE)

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.Manager()

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kadastrale Gemeente"
        verbose_name_plural = "Kadastrale Gemeentes"
        managed = False

    def __str__(self):
        return "{}".format(self.id)


class KadastraleSectie(models.Model):
    id = models.CharField(max_length=200, primary_key=True)

    sectie = models.CharField(max_length=2)

    kadastrale_gemeente = models.ForeignKey(
        KadastraleGemeente, related_name="secties",
        on_delete=models.CASCADE
    )

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.Manager()

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kadastrale Sectie"
        verbose_name_plural = "Kadastrale Secties"
        managed = False

    def __str__(self):
        return "{}".format(self.id)


class KadasterCodeOmschrijving(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    omschrijving = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class Beschikkingsbevoegdheid(KadasterCodeOmschrijving):
    pass


class Geslacht(KadasterCodeOmschrijving):
    pass


class AanduidingNaam(KadasterCodeOmschrijving):
    pass


class Land(KadasterCodeOmschrijving):
    pass


class Rechtsvorm(KadasterCodeOmschrijving):
    pass


class Adres(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    openbareruimte_naam = models.CharField(max_length=80, null=True)
    huisnummer = models.IntegerField(null=True)
    huisletter = models.CharField(max_length=1, null=True)
    toevoeging = models.CharField(max_length=4, null=True)
    postcode = models.CharField(max_length=6, null=True)
    woonplaats = models.CharField(max_length=80, null=True)

    postbus_nummer = models.IntegerField(null=True)
    postbus_postcode = models.CharField(max_length=50, null=True)
    postbus_woonplaats = models.CharField(max_length=80, null=True)

    buitenland_adres = models.CharField(max_length=100, null=True)
    buitenland_woonplaats = models.CharField(max_length=100, null=True)
    buitenland_regio = models.CharField(max_length=100, null=True)
    buitenland_naam = models.CharField(max_length=100, null=True)
    buitenland_land = models.ForeignKey(
        Land, null=True, on_delete=models.CASCADE)

    class Meta:
        managed = False


class EigenaarCategorie(models.Model):
    id = models.IntegerField(primary_key=True)
    categorie = models.CharField(max_length=100)

    class Meta:
        managed = False


class Eigenaar(models.Model):
    """
    Een Eigenaar / Kadastraal Subject is een persoon die
    in de kadastrale registratie voorkomt.
    Het betreft hier zowel natuurlijk- als niet natuurlijk personen.

    https://www.amsterdam.nl/stelselpedia/brk-index/catalog-brk-levering/kadastraal-subject/
    """
    SUBJECT_TYPE_NATUURLIJK = 0
    SUBJECT_TYPE_NIET_NATUURLIJK = 1
    SUBJECT_TYPE_CHOICES = (
        (SUBJECT_TYPE_NATUURLIJK, "Natuurlijk persoon"),
        (SUBJECT_TYPE_NIET_NATUURLIJK, "Niet-natuurlijk persoon"),
    )

    BRON_REGISTRATIE = 0
    BRON_KADASTER = 1
    BRON_CHOICES = (
        (BRON_REGISTRATIE, "Basisregistraties"),
        (BRON_KADASTER, "Kadaster"),
    )

    id = models.CharField(max_length=60, primary_key=True)
    type = models.SmallIntegerField(choices=SUBJECT_TYPE_CHOICES)
    beschikkingsbevoegdheid = models.ForeignKey(
        Beschikkingsbevoegdheid, null=True, on_delete=models.CASCADE
    )
    eigenaar_categorie = models.ForeignKey(
        EigenaarCategorie, db_column='cat_id', on_delete=models.CASCADE
    )

    date_modified = models.DateTimeField(auto_now=True)

    voornamen = models.CharField(max_length=200, null=True)
    voorvoegsels = models.CharField(max_length=10, null=True)
    naam = models.CharField(max_length=200, null=True)
    geslacht = models.ForeignKey(Geslacht, null=True, on_delete=models.CASCADE)
    aanduiding_naam = models.ForeignKey(
        AanduidingNaam, null=True, on_delete=models.CASCADE)
    geboortedatum = models.CharField(
        max_length=50, null=True)  # kadaster-data kan onvolledig zijn
    geboorteplaats = models.CharField(max_length=80, null=True)
    geboorteland = models.ForeignKey(
        Land, null=True, related_name='+', on_delete=models.CASCADE)
    overlijdensdatum = models.CharField(
        max_length=50, null=True)  # kadaster-data kan onvolledig zijn

    partner_voornamen = models.CharField(max_length=200, null=True)
    partner_voorvoegsels = models.CharField(max_length=10, null=True)
    partner_naam = models.CharField(max_length=200, null=True)

    land_waarnaar_vertrokken = models.ForeignKey(
        Land, null=True, related_name='+',
        on_delete=models.CASCADE
    )

    rsin = models.CharField(max_length=80, null=True)
    kvknummer = models.CharField(max_length=8, null=True)
    rechtsvorm = models.ForeignKey(
        Rechtsvorm, null=True, on_delete=models.CASCADE)
    statutaire_naam = models.CharField(max_length=200, null=True)
    statutaire_zetel = models.CharField(max_length=24, null=True)

    bron = models.SmallIntegerField(choices=BRON_CHOICES)
    woonadres = models.ForeignKey(
        Adres, null=True, related_name="+", on_delete=models.CASCADE)
    postadres = models.ForeignKey(
        Adres, null=True, related_name="+", on_delete=models.CASCADE)

    class Meta:
        managed = False
        verbose_name = "Kadastraal subject"
        verbose_name_plural = "Kadastrale subjecten"
        index_together = (
            ('naam', 'statutaire_naam'),
        )

        permissions = (
            ('view_sensitive_details', 'Kan privacy-gevoelige data inzien'),
        )

    def __str__(self):
        return self.volledige_naam()

    def is_natuurlijk_persoon(self):
        return not self.statutaire_naam

    def volledige_naam(self):
        if self.statutaire_naam:
            return self.statutaire_naam

        return " ".join([part for part in (self.voornamen,
                                           self.voorvoegsels,
                                           self.naam) if part])


class SoortGrootte(KadasterCodeOmschrijving):
    pass


class CultuurCodeOnbebouwd(KadasterCodeOmschrijving):
    pass


class CultuurCodeBebouwd(KadasterCodeOmschrijving):
    pass


class APerceelGPerceelRelatie(models.Model):
    id = models.CharField(max_length=121, primary_key=True)

    a_perceel = models.ForeignKey(
        'KadastraalObject', related_name='g_perceel_relaties',
        on_delete=models.CASCADE
    )

    g_perceel = models.ForeignKey(
        'KadastraalObject', related_name='a_perceel_relaties',
        on_delete=models.CASCADE
    )

    class Meta:
        managed = False


class KadastraalObject(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    aanduiding = models.CharField(max_length=17)

    kadastrale_gemeente = models.ForeignKey(
        KadastraleGemeente, related_name="kadastrale_objecten",
        on_delete=models.CASCADE
    )

    sectie = models.ForeignKey(
        KadastraleSectie, related_name="kadastrale_objecten",
        on_delete=models.CASCADE
    )

    date_modified = models.DateTimeField(auto_now=True)

    perceelnummer = models.IntegerField()
    indexletter = models.CharField(max_length=1)
    indexnummer = models.IntegerField()
    soort_grootte = models.ForeignKey(
        SoortGrootte, null=True, on_delete=models.CASCADE)
    grootte = models.IntegerField(null=True)
    koopsom = models.IntegerField(null=True)
    koopsom_valuta_code = models.CharField(max_length=50, null=True)
    koopjaar = models.CharField(max_length=15, null=True)
    meer_objecten = models.NullBooleanField(default=None)
    cultuurcode_onbebouwd = models.ForeignKey(
        CultuurCodeOnbebouwd, null=True, on_delete=models.CASCADE)
    cultuurcode_bebouwd = models.ForeignKey(
        CultuurCodeBebouwd, null=True, on_delete=models.CASCADE)

    register9_tekst = models.TextField()
    status_code = models.CharField(max_length=50)
    toestandsdatum = models.DateField(null=True)
    voorlopige_kadastrale_grens = models.NullBooleanField(default=None)
    in_onderzoek = models.TextField(null=True)

    poly_geom = geo.MultiPolygonField(srid=28992, null=True)
    point_geom = geo.PointField(srid=28992, null=True)

    voornaamste_gerechtigde = models.ForeignKey(
        Eigenaar, null=True, on_delete=models.CASCADE)

    verblijfsobjecten = models.ManyToManyField(
        bag.Verblijfsobject,
        through='KadastraalObjectVerblijfsobjectRelatie',
        related_name="kadastrale_objecten")

    g_percelen = models.ManyToManyField(
        'KadastraalObject',
        through=APerceelGPerceelRelatie,
        through_fields=('a_perceel', 'g_perceel'),
        related_name="a_percelen")

    buurten = models.ManyToManyField(
        bag.Buurt,
        through='EigendomBuurt',
        through_fields=('kadastraal_object', 'buurt'),
        related_name="eigendommen")

    wijken = models.ManyToManyField(
        bag.Buurtcombinatie,
        through='EigendomWijk',
        through_fields=('kadastraal_object', 'buurt_combi'),
        related_name="eigendommen")

    ggws = models.ManyToManyField(
        bag.Gebiedsgerichtwerken,
        through='EigendomGGW',
        through_fields=('kadastraal_object', 'ggw'),
        related_name="eigendommen")

    stadsdelen = models.ManyToManyField(
        bag.Stadsdeel,
        through='EigendomStadsdeel',
        through_fields=('kadastraal_object', 'stadsdeel'),
        related_name="eigendommen")

    objects = geo.Manager()

    class Meta:
        managed = False
        ordering = (
            'kadastrale_gemeente__id', 'sectie', 'perceelnummer',
            '-indexletter', 'indexnummer')

    def __str__(self):
        return self.get_aanduiding_spaties()

    def get_aanduiding_spaties(self):
        return kadaster.get_aanduiding_spaties(
            self.kadastrale_gemeente.id, self.sectie.sectie,
            self.perceelnummer, self.indexletter, self.indexnummer
        )


class KadastraalObjectVerblijfsobjectRelatie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    kadastraal_object = models.ForeignKey(
        KadastraalObject, on_delete=models.CASCADE)
    verblijfsobject = models.ForeignKey(
        bag.Verblijfsobject, null=True, on_delete=models.CASCADE)

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False


class AardZakelijkRecht(KadasterCodeOmschrijving):
    pass


class AppartementsrechtsSplitsType(KadasterCodeOmschrijving):
    pass


class ZakelijkRecht(models.Model):
    id = models.CharField(max_length=183, primary_key=True)

    date_modified = models.DateTimeField(auto_now=True)

    zrt_id = models.CharField(max_length=60)
    aard_zakelijk_recht = models.ForeignKey(
        AardZakelijkRecht, null=True, on_delete=models.CASCADE)
    aard_zakelijk_recht_akr = models.CharField(max_length=3, null=True)

    ontstaan_uit = models.ForeignKey(
        Eigenaar, null=True, related_name="ontstaan_uit_set",
        on_delete=models.CASCADE,
    )
    betrokken_bij = models.ForeignKey(
        Eigenaar, null=True, related_name="betrokken_bij_set",
        on_delete=models.CASCADE
    )

    teller = models.IntegerField(null=True)
    noemer = models.IntegerField(null=True)

    kadastraal_object = models.ForeignKey(
        KadastraalObject, related_name="rechten",
        on_delete=models.CASCADE
    )

    kadastraal_subject = models.ForeignKey(
        Eigenaar, related_name="rechten",
        on_delete=models.CASCADE, db_column='kadastraal_subject_id'
    )

    kadastraal_object_status = models.CharField(max_length=50)

    app_rechtsplitstype = models.ForeignKey(
        AppartementsrechtsSplitsType, null=True,
        on_delete=models.CASCADE
    )

    verblijfsobjecten = models.ManyToManyField(
        bag.Verblijfsobject,
        through='ZakelijkRechtVerblijfsobjectRelatie',
        related_name="rechten")

    _kadastraal_subject_naam = models.CharField(max_length=200)
    _kadastraal_object_aanduiding = models.CharField(max_length=100)

    class Meta:
        managed = False
        index_together = (
            ('aard_zakelijk_recht', '_kadastraal_subject_naam'),
        )

    def __str__(self):
        return self.directional_name()

    def directional_name(self, direction='subject'):
        omschrijving = ''
        if self.aard_zakelijk_recht:
            omschrijving = self.aard_zakelijk_recht.omschrijving

        aandeel = ''
        if self.teller is not None and self.noemer is not None:
            aandeel = '({}/{})'.format(self.teller, self.noemer)

        if direction == 'object':
            return "{} - {} {}".format(
                self.kadastraal_object.aanduiding, omschrijving, aandeel)

        return "{} - {} {}".format(
            self._kadastraal_subject_naam, omschrijving, aandeel)


class Eigendom(models.Model):
    zakelijk_recht = models.OneToOneField(
        ZakelijkRecht,
        db_column='id',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='eigendom'
    )

    kadastraal_subject = models.ForeignKey(
        Eigenaar,
        on_delete=models.CASCADE, db_column='kadastraal_subject_id'
    )

    kadastraal_object = models.ForeignKey(
        KadastraalObject,
        on_delete=models.CASCADE,
        related_name="eigendommen"
    )
    aard_zakelijk_recht_akr = models.CharField(max_length=3, null=True)

    eigenaar_categorie = models.ForeignKey(
        EigenaarCategorie, db_column='cat_id', on_delete=models.CASCADE
    )
    grondeigenaar = models.BooleanField()
    aanschrijfbaar = models.BooleanField()
    appartementeigenaar = models.BooleanField()

    class Meta:
        verbose_name = "Eigendom"
        verbose_name_plural = "Eigendommen"
        managed = False


class EigendomBuurt(models.Model):
    id = models.IntegerField(primary_key=True)

    kadastraal_object = models.ForeignKey(
        KadastraalObject,
        on_delete=models.CASCADE,
    )

    buurt = models.ForeignKey(
        bag.Buurt, on_delete=models.CASCADE
    )

    class Meta:
        managed = False


class EigendomWijk(models.Model):
    id = models.IntegerField(primary_key=True)

    kadastraal_object = models.ForeignKey(
        KadastraalObject,
        on_delete=models.CASCADE,
    )

    buurt_combi = models.ForeignKey(
        bag.Buurtcombinatie, on_delete=models.CASCADE
    )

    class Meta:
        managed = False


class EigendomGGW(models.Model):
    id = models.IntegerField(primary_key=True)

    kadastraal_object = models.ForeignKey(
        KadastraalObject,
        on_delete=models.CASCADE,
    )

    ggw = models.ForeignKey(
        bag.Gebiedsgerichtwerken, on_delete=models.CASCADE
    )

    class Meta:
        managed = False


class EigendomStadsdeel(models.Model):
    id = models.IntegerField(primary_key=True)

    kadastraal_object = models.ForeignKey(
        KadastraalObject,
        on_delete=models.CASCADE,
    )

    stadsdeel = models.ForeignKey(
        bag.Stadsdeel, on_delete=models.CASCADE
    )

    class Meta:
        managed = False


class ZakelijkRechtVerblijfsobjectRelatie(models.Model):
    zakelijk_recht = models.ForeignKey(
        ZakelijkRecht, on_delete=models.CASCADE
    )

    verblijfsobject = models.ForeignKey(
        bag.Verblijfsobject, on_delete=models.CASCADE
    )

    class Meta:
        managed = False


class AardAantekening(KadasterCodeOmschrijving):
    pass


class Aantekening(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    aard_aantekening = models.ForeignKey(
        AardAantekening, on_delete=models.CASCADE)
    omschrijving = models.TextField()

    date_modified = models.DateTimeField(auto_now=True)

    kadastraal_object = models.ForeignKey(
        KadastraalObject, null=True, related_name="aantekeningen",
        on_delete=models.CASCADE
    )

    opgelegd_door = models.ForeignKey(
        Eigenaar, null=True, related_name="aantekeningen",
        on_delete=models.CASCADE
    )

    class Meta:
        managed = False

    def __str__(self):
        if self.aard_aantekening.omschrijving:
            return self.aard_aantekening.omschrijving
        return self.id
