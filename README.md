# dataselectie
De dataselectie service maak het mogelijk om collecties te selecteren uit de datapunt data.

## Gebruik doelen
Via [City Data](http://data.amsterdam.nl) is het mogelijk om met enkel object te werken. Echter is er binnen gemeente Amsterdam
ook een behoefte om een collectie te kunnen selecteren (b.v. een alles nummeraanduidingen binnen een buurtcombinatie) om
mee te werken. De dataselectie is de interface voor dat behoefte. Het is ook een andere manier om de data die via Atlas beschikbaar
is te vertonen in een tabel format i.p.v op een kaart.

## Technische beschrijving
De dataselectie service is een indexeren en zoeken service boven op data van andere services. Het maakt gebruik van de
data in andere services om ze in een andere manier te bieden.

Voor hr wordt gebruik gemaakt van brondata gegenereerd in hr, waarbij de index in dataselectie is opgenomen.
De koppeling is gerealiseerd door een tabel met als id vestiging_id en de api-json die gepresenteerd moet worden.
In elastic is een 1 op n opgenomen, waarbij er n vestigingen (hr) per locatie (bag) zijn opgenomen.
Omdat elastic alleen tellingen kan maken van parent naar child is de selectie in elastic en wordt teruggewerkt
naar vestigingen.

### Project setup
De dataselectie gebruikt data van de andere services en heeft geen eigen import process.
dataselectie maakt wel een eigen indices in elastic.

Op dit moment worden de bag en HR databases gebruikt, omdat daar de data is opgeslagen.
Die moet ook via docker compose starten.

### Lokaal setup
Lokale setup voor dataselectie

`Let op dat dat er voldoende geheugen gealloceerd is voor elasticsearch docker (min. 4GB)`

```
$ docker-compose up -d

$ docker-compose exec dataselectie python manage.py migrate
$ docker-compose exec database download-db.sh bag <your username>
$ ./prepare-local.sh

?? Misschien moeten hiervoor eerst de bag en brk tabellen verwijderd worden omdat ze zijn gecreeerd met foreign key
restricties in migrate??

$ docker-compose exec database update-table.sh handelsregister hr_dataselectie public dataselectie <your username>
$ docker-compose exec dataselectie python manage.py  brk_tables_views

$ docker-compose exec elasticsearch clean-el.sh
$ docker-compose exec elasticsearch update-el.sh bag <your username>
$ docker-compose exec elasticsearch update-el.sh ds_bag_index <your username>
$ docker-compose exec elasticsearch update-el.sh ds_hr_index <your username>
$ docker-compose exec elasticsearch update-el.sh ds_brk_index <your username>
```

Indien je zelf de index van scratch wilt bouwen kan dat als volgt. Let op dat dit ruim zes uur in beslag neemt

```
$ docker-compose exec -T dataselectie python manage.py elastic_indices --build
```

Testing with authorization. For BAG and HR we need scope HR/R and for BRK we need scope BRK_RSN (lees alle kadaster
data voor natuurlijke personen)

Tijdens ontwikkelen kan in settings.py ALWAYS_OK op LOCAL worden gezet. Maar om de authorisatie te testen kan
op localhost met het script web/dataselectie/test/localauth/mktoken_superemployee_local.py een token worden gemaakt om
in te loggen. Bijv.

```
token=`test/localauth/mktoken_superemployee_local.py`
curl -XGET -H "Authorization: Bearer ${token}" http://localhost:8000/dataselectie/brk/?stadsdeel_naam=Zuidoost
```

 ## Links
 - [Dokuwiki documentatie](https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:datapunt:dataselectiesconfluence)
 - [API endpoint](https://api.data.amsterdam.nl)
