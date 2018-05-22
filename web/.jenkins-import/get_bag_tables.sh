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
	"brk_adres"
	"brk_eigendom"
	"brk_eigenaar"
	"brk_eigenaarcategorie"
	"brk_gemeente"
	"brk_kadastercodeomschrijving"
	"brk_kadastraalobject"
	"brk_kadastraalobjectverblijfsobjectrelatie"
	"brk_kadastralegemeente"
	"brk_kadastralesectie"
	"brk_zakelijkrecht"
	"brk_zakelijkrechtverblijfsobjectrelatie"
	"brk_eigendom"
	"brk_eigenaar"
	"brk_eigenaarcategorie"
)


for tablename in "${bag_tables[@]}"
do
	echo recreate $tablename
	dc exec -T database update-table.sh bag $tablename public dataselectie
done

