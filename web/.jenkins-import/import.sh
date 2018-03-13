#!/bin/bash

DIR="$(dirname $0)"

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
	docker-compose -p dataselectie -f ${DIR}/docker-compose.yml $*
}

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*
}

dc pull

dc build --pull

dc up -d database

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
	"brk_kadastraalobject"
	"brk_kadastraalsubject"
	"brk_zakelijkrechtverblijfsobjectrelatie"
)

for tablename in "${bag_tables[@]}"
do
dc exec -T database update-table.sh bag $tablename public dataselectie
done

dc exec -T database update-table.sh handelsregister hr_dataselectie public dataselectie

dc run --rm importer

dc exec importer bash -c "/app/docker-wait.sh \ && python manage.py elastic_indices bag --partial=1/3 --build" &
dc exec importer bash -c "python manage.py elastic_indices bag --partial=2/3 --build" &
dc exec importer bash -c "python manage.py elastic_indices bag --partial=3/3 --build"

FAIL=0

for job in `jobs -p`
do
	echo $job
	wait $job || let "FAIL+=1"
done

echo $FAIL

if [ "$FAIL" == "0" ];
then
    echo "YAY!"
else
    echo "FAIL! ($FAIL)"
    echo 'Elastic Import Error. 1 or more workers failed'
    exit 1
fi

dc run --rm el-backup
dc down
