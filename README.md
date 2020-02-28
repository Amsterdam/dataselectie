# dataselectie
De service Dataselectie maakt het mogelijk om collecties te selecteren uit de Datapunt data.

## Gebruik doelen
Via [Data en Informatie](http://data.amsterdam.nl) is het mogelijk om met een enkel object te werken. Echter is er binnen de gemeente Amsterdam
ook een behoefte om een collectie te kunnen selecteren (b.v. nummeraanduidingen binnen een buurtcombinatie) om
mee te werken. Dataselectie is de interface voor die behoefte. Het is ook een andere manier om de data die via Data en Informatie beschikbaar
is te vertonen in een tabel format i.p.v op een kaart.

## Technische beschrijving
De dataselectie service is een indexeren- en zoeken-service boven op data van andere services. Het maakt gebruik van de
data in andere services om ze in een andere manier te bieden.

Voor HR (Handelsregister) wordt gebruik gemaakt van brondata gegenereerd in HR, waarbij de index in Dataselectie is opgenomen.
De koppeling is gerealiseerd door een tabel met als id vestiging_id en de api-json die gepresenteerd moet worden.
In Elastic is een 1 op n opgenomen, waarbij er n vestigingen (HR) per locatie (BAG) zijn opgenomen.
Omdat elastic alleen tellingen kan maken van parent naar child is de selectie in elastic en wordt teruggewerkt
naar vestigingen.

### Project setup
Dataselectie gebruikt data van de andere services en heeft geen eigen import process.
Het maakt wel eigen indices in Elastic.

Op dit moment worden de BAG, HR en BRK databases gebruikt, omdat daar de data is opgeslagen.
Die moeten ook via docker compose starten.

### Lokaal setup
Lokale setup voor Dataselectie

`Let op dat dat er voldoende geheugen gealloceerd is voor elasticsearch docker (min. 4GB)`

```
$ docker-compose up -d

$ docker-compose exec database update-db.sh bag <your username>
$ docker-compose exec database update-db.sh dataselectie <your username>
$ docker-compose exec database update-table.sh handelsregister hr_dataselectie public dataselectie <your username>

$ docker-compose exec elasticsearch clean-el.sh
$ docker-compose exec elasticsearch update-el.sh bag <your username>
$ docker-compose exec elasticsearch update-el.sh ds_bag_index <your username>
$ docker-compose exec elasticsearch update-el.sh ds_hr_index <your username>
$ docker-compose exec elasticsearch update-el.sh ds_brk_index <your username>
```

Indien je zelf de index van scratch wilt bouwen kan dat als volgt. Let op dat dit ruim zes uur in beslag neemt

```
$ docker-compose exec -T dataselectie python manage.py elastic_indices --recreate
$ docker-compose exec -T dataselectie python manage.py elastic_indices --build
```

Je kan ook `--partial=1/1000` toevoegen om een partiële index te maken.

### API Authorizatie

Testing with authorization. For BAG and HR we need scope HR/R and for BRK we need scope BRK_RSN (lees alle kadaster
data voor natuurlijke personen)

Tijdens ontwikkelen kan in `settings.py` `ALWAYS_OK` op `LOCAL` worden gezet.

Om de authorisatie te testen kan op localhost met het script
`web/dataselectie/test/localauth/mktoken_superemployee_local.py`
een token worden gemaakt om in te loggen. Bijv.

```
token=`test/localauth/mktoken_superemployee_local.py`
curl -XGET -H "Authorization: Bearer ${token}" http://localhost:8000/dataselectie/brk/?stadsdeel_naam=Zuidoost
```

 ## Links
 - [Dokuwiki documentatie](https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:datapunt:dataselectiesconfluence)
 - [API endpoint](https://api.data.amsterdam.nl)
