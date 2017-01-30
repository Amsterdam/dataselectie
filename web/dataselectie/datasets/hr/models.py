from django.contrib.gis.db import models


class CBS_sbi_hoofdcat(models.Model):
    hcat = models.CharField(max_length=20, primary_key=True)
    hoofdcategorie = models.CharField(max_length=140, blank=False, null=False)


class CBS_sbi_subcat(models.Model):
    scat = models.CharField(max_length=20, primary_key=True)
    subcategorie = models.CharField(max_length=140, blank=False, null=False)
    hcat = models.ForeignKey(CBS_sbi_hoofdcat, on_delete=models.CASCADE)


class CBS_sbicodes(models.Model):
    sbi_code = models.CharField(max_length=14, primary_key=True)
    sub_sub_categorie = models.CharField(
        max_length=140, blank=False, null=False)
    scat = models.ForeignKey(CBS_sbi_subcat, on_delete=models.CASCADE)


class GeoVestigingen(models.Model):
    """
    geo table of joined tables to make mapserver lightning speed
    """

    # NOTE merdere activiteiten per vestigings nummer mogelijk
    vestigingsnummer = models.CharField(
        max_length=12, db_index=True,
        help_text="Betreft het identificerende gegeven voor de Vestiging"
    )

    sbi_code_int = models.IntegerField(
        db_index=True,
        help_text="De codering van de activiteit conform de SBI2008"
    )

    sbi_code = models.CharField(
        db_index=True,
        max_length=5,
        help_text="De codering van de activiteit conform de SBI2008"
    )

    activiteitsomschrijving = models.TextField(
        blank=True, null=True,
        help_text="""
            De omschrijving van de activiteiten die de
            Vestiging of Rechtspersoon uitoefent"""
    )

    subtype = models.CharField(
        db_index=True,
        max_length=200, null=True, blank=True,
    )

    naam = models.CharField(
        max_length=200, null=True, blank=True,
    )

    uri = models.CharField(
        max_length=200, null=True, blank=True,
    )

    hoofdvestiging = models.BooleanField()

    locatie_type = models.CharField(
        max_length=1, blank=True, null=True,
        choices=[
            ('B', 'Bezoek'),
            ('P', 'Post'),
            ('V', 'Vestiging')])

    geometrie = models.PointField(srid=28992, blank=True, null=True)

    sbi_detail_group = models.CharField(
        db_index=True,
        max_length=200, null=True, blank=True,
        help_text="De codering van de activiteit conform de SBI2008"
    )

    postadres = models.ForeignKey(
        'Locatie', related_name="+", blank=True, null=True,
        help_text="postadres")

    bezoekadres = models.ForeignKey(
        'Locatie', related_name="+", blank=True, null=True,
        help_text="bezoekadres")

    bag_vbid = models.CharField(
        max_length=16, blank=True, null=True)

    # Indication if corrected by auto search
    correctie = models.NullBooleanField()


class Locatie(models.Model):
    """
    Locatie (LOC)

    Een Locatie is een aanwijsbare plek op aarde.
    """

    id = models.CharField(
        primary_key=True, max_length=18
    )
    volledig_adres = models.CharField(
        max_length=550, blank=True, null=True,
        help_text="Samengesteld adres "
    )
    toevoeging_adres = models.TextField(
        blank=True, null=True,
        help_text="Vrije tekst om een Adres nader aan te kunnen duiden"
    )
    afgeschermd = models.BooleanField(
        help_text="Geeft aan of het adres afgeschermd is of niet"
    )

    postbus_nummer = models.CharField(
        db_index=True,
        max_length=10, blank=True, null=True,
    )

    bag_numid = models.CharField(
        max_length=16, db_index=True, blank=True, null=True)

    bag_vbid = models.CharField(
        max_length=16, db_index=True, blank=True, null=True)

    bag_nummeraanduiding = models.URLField(
        max_length=200, blank=True, null=True,
        help_text="Link naar de BAG Nummeraanduiding"
    )
    bag_adresseerbaar_object = models.URLField(
        max_length=200, blank=True, null=True,
        help_text="Link naar het BAG Adresseerbaar object"
    )

    straat_huisnummer = models.CharField(max_length=220, blank=True, null=True)
    postcode_woonplaats = models.CharField(
        max_length=220, blank=True, null=True)
    regio = models.CharField(max_length=170, blank=True, null=True)
    land = models.CharField(max_length=50, blank=True, null=True)

    geometrie = models.PointField(srid=28992, blank=True, null=True)

    # locatie meuk die er nu wel is.
    straatnaam = models.CharField(
        db_index=True, max_length=100, blank=True, null=True)
    toevoegingadres = models.CharField(max_length=100, blank=True, null=True)
    huisletter = models.CharField(max_length=1, blank=True, null=True)

    huisnummer = models.DecimalField(
        db_index=True,
        max_digits=5, decimal_places=0, blank=True, null=True)

    huisnummertoevoeging = models.CharField(
        max_length=5, blank=True, null=True)

    postcode = models.CharField(
        db_index=True, max_length=6, blank=True, null=True)

    # plaats.
    plaats = models.CharField(
        db_index=True,
        max_length=100, blank=True, null=True)

    # Auto fix related

    # Indication if corrected by auto search
    correctie = models.NullBooleanField()
    # Last updated  (by search)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    # QS string used to fix the search data
    query_string = models.CharField(
        db_index=True,
        max_length=180, blank=True, null=True,
    )

    def __str__(self):
        return "{}".format(self.volledig_adres)


class BetrokkenPersonen(models.Model):
    class Meta:
        db_table = 'hr_betrokken_personen'
        managed = False

    mac_naam = models.CharField(
        max_length=600,
        help_text='Maatschappelijke activiteit naam')

    kvk_nummer = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        help_text="Kvk nummer"
    )

    vestiging_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Vestiging id"
    )

    vestigingsnummer = models.CharField(
        max_length=12, unique=True,
        help_text="Betreft het identificerende gegeven voor de Vestiging"
    )

    persoons_id = models.IntegerField(
        null=True)

    rol = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        help_text="Rol"
    )

    naam = models.CharField(
        max_length=600,
        blank=True,
        null=True,
        help_text="Persoonsnaam (handelsregister terminologie)"
    )

    rechtsvorm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Rechtsvorm"
    )

    functietitel = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Titel van de functionaris"
    )

    soortbevoegdheid = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Bevoegdheid van de functionaris"
    )

    bevoegde_naam = models.CharField(
        max_length=240,
        blank=True,
        null=True,
        help_text="Bevoegdheid van de functionaris"
    )

    datum_aanvang = models.DateField(
        max_length=8, blank=True, null=True,
        help_text="De datum van aanvang van de MaatschappelijkeActiviteit",
    )

    datum_einde = models.DateField(
        max_length=8, blank=True, null=True,
        help_text="""
            De datum van beëindiging van de MaatschappelijkeActiviteit""",
    )
