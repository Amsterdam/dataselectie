#!/bin/bash

set -u   # crash on missing env variables
set -e   # stop on any error

declare  -a bag_tables=(
	"bag_bouwblok"
	"bag_bron"
	"bag_buurt"
	"bag_buurtcombinatie"
	"bag_eigendomsverhouding"
	"bag_financieringswijze"
	"bag_gebiedsgerichtwerken"
	"bag_gebruik"
	"bag_gebruiksdoel"
	"bag_gemeente"
	"bag_grootstedelijkgebied"
	"bag_ligging"
	"bag_ligplaats"
	"bag_locatieingang"
	"bag_nummeraanduiding"
	"bag_openbareruimte"
	"bag_pand"
	"bag_redenafvoer"
	"bag_redenopvoer"
	"bag_stadsdeel"
	"bag_standplaats"
	"bag_status"
	"bag_toegang"
	"bag_unesco"
	"bag_verblijfsobject"
	"bag_verblijfsobjectpandrelatie"
	"bag_woonplaats"
	"brk_eigendommen"
	"brk_eigendommen_categorie"
	"brk_kadastraalobject"
	"brk_eigenaren"
	"brk_eigenaren_categorie"
	"brk_zakelijkrecht"
	"brk_zakelijkrechtverblijfsobjectrelatie"
)

for tablename in "${bag_tables[@]}"
do
	echo $tablename
	dc exec -T database update-table.sh bag $tablename public dataselectie
done

