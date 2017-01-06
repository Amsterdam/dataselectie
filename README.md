# dataselectie
De dataselectie service maak het mogelijk om collecties te selecteren uit de datapunt data.

## Gebruik doelen
Via [Atlas](http://atlas.amsterdam.nl) is het mogelijk om met enkel object te werken. Echter is er binnen gemeente Amsterdam 
ook een behoefte om een collectie te kunnen selecteren (b.v. een alles nummeraanduidingen binnen een buurtcombinatie) om 
mee te werken. De dataselectie is de interface voor dat behoefte. Het is ook een andere manier om de data die via Atlas beschikbaar 
is te vertonen in een tabel format i.p.v op een kaart.

## Technische beschrijving
De dataselectie service is een indexeren en zoeken service boven op data van andere services. Het maakt gebruik van de 
data in andere services om ze in een andere manier te bieden.

Voor hr wordt gebruik gemaakt van brondata gegenereerd in hr, waarbij de index in dataselectie is opgenomen. De koppeling is gerealiseerd 
door een tabel met als id vestiging_id en de api-json die gepresenteerd moet worden.

### Project setup
De dataselectie gebruikt data van de andere services en heeft daarom geen eigen import process. dataselectie maakt 
wel een eigen indices in elastic.

Op dit moment wordt de DB van de bag project gebruikt, omdat daar zit alle data. Die moet ook via docker compose starten

### Lokaal setup
Lokale setup voor dataselectie

`Let op dat dat er voldoende geheugen gealloceerd is voor elasticsearch docker (min. 4GB)`

```
$ docker-compose up -d
$ docker-compose exec database_BAG update-db.sh atlas
$ docker-compose exec database_HR update-db.sh handelsregister
$ docker-compose exec database_dataselectie python manage.py migrate
$ docker-compose exec elasticsearch update-el.sh atlas bag brk nummeraanduiding
$ docker-compose exec elasticsearch update-el.sh ds_bag ds_bag
```

`Indien je zelf de index van scratch wilt bouwen kan dat als volgt. Let op dat dit ruim twee uur in beslag neemt`
```
$ docker-compose exec -T dataselectie python manage.py elastic_indices --build
```

 ## Links
 - [Dokuwiki documentatie](https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:datapunt:dataselectiesconfluence)
 - [API endpoint](https://api.datapunt.amsterdam.nl)
