# Zelfbediening
De zelfbediening service maak het mogelijk om collecties te selecteren uit de datapunt data.

## Gebruik doelen
Via [Atlas](http://atlas.amsterdam.nl) is het mogelijk om met enkel object te werken. Echter is er binnen gemeente Amsterdam ook een behoefte om een collectie te kunnen selecteren (b.v. een alles nummeraanduidingen binnen een buurtcombinatie) om mee te werken. De zelfbediening is de interface voor dat behoefte. Het is ook een andere manier om de data die via Atlas beschikbaar is te vertonen in een tabel format i.p.v op een kaart.
 
## Technische beschrijving
De zelfbediening service is een indexeren en zoeken service boven op data van andere services. Het maakt gebruik van de data in andere services om ze in een andere manier te bieden.

### Project setup
De zelfbediening gebruikt data van de andere services en heeft daarom geen eigen import process. Zelfbediening maakt wel een eigen indices in elastic.

Op dit moment wordt de DB van de bag project gebruikt, omdat daar zit alle data. Die moet ook via docker compose starten 

### Lokaal setup
Hoe het in elkaar krijgen
 
 
 ## Links
 - [Dokuwiki documentatie](https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:datapunt:zelfbedieningsconfluence)
 - [API endpoint](https://api.datapunt.amsterdam.nl)
