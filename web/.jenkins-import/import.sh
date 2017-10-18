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


# trap 'dc kill ; dc rm -f' EXIT

#dc pull

#rm -rf ${DIR}/backups
#mkdir -p ${DIR}/backups

#dc build --pull

#dc up -d database

#sleep 5 # waiting for postgres to start

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
)

for tablename in "${bag_tables[@]}"
do
dc exec -T database update-table.sh bag $tablename public dataselectie
done

#
#dc exec -T database update-table.sh handelsregister hr_dataselectie public dataselectie
#
#dc run --rm importer
#

#dc run importer_el1
## create the new elastic indexes
#dc up importer_el1 importer_el2 importer_el3
## wait until all building is done
#import_status=`docker wait dataselectie_importer_el1_1 dataselectie_importer_el2_1 dataselectie_importer_el3_1`
#
## count the errors.
#import_error=`echo $import_status | grep -o "1" | wc -l`
#
#if (( $import_error > 0 ))
#then
#    echo 'Elastic Import Error. 1 or more workers failed'
#    exit 1
#fi
#
#dc run --rm el-backup
#dc down
