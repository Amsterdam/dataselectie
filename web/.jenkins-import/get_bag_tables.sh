#!/bin/bash

set -u   # crash on missing env variables
set -e   # stop on any error



declare  -a bag_tables=(
	"bag_bouwblok"
	"bag_bron"
	"bag_buurt"
	"bag_buurtcombinatie"
	"bag_gebiedsgerichtwerken"
	"bag_gemeente"
	"bag_grootstedelijkgebied"
	"bag_ligplaats"
	"bag_nummeraanduiding"
	"bag_openbareruimte"
	"bag_pand"
	"bag_stadsdeel"
	"bag_standplaats"
	"bag_unesco"
	"bag_verblijfsobject"
	"bag_verblijfsobjectpandrelatie"
	"bag_woonplaats"
	"brk_aardzakelijkrecht"
	"brk_adres"
	"brk_cultuurcodebebouwd"
	"brk_cultuurcodeonbebouwd"
	"brk_eigendom"
	"brk_eigenaar"
	"brk_eigenaarcategorie"
	"brk_erfpacht"
	"brk_gemeente"
	"brk_geslacht"
	"brk_kadastercodeomschrijving"
	"brk_kadastraalobject"
	"brk_kadastraalobjectverblijfsobjectrelatie"
	"brk_kadastralegemeente"
	"brk_kadastralesectie"
	"brk_land"
	"brk_rechtsvorm"
	"brk_zakelijkrecht"
	"brk_zakelijkrechtverblijfsobjectrelatie"
	"brk_eigendom"
	"brk_eigenaar"
	"brk_eigenaarcategorie"
)


for tablename in "${bag_tables[@]}"
do
	echo recreate $tablename
	docker-compose exec -T database update-table.sh bag_v11 $tablename public dataselectie
done

