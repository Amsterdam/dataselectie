#!/bin/bash

DIR="$(dirname $0)"

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
	docker-compose -p ds -f ${DIR}/docker-compose.yml $*
}

# remove old stuff.
dc down
dc rm -f

dc pull
dc build

rm -rf ${DIR}/backups/
mkdir -p ${DIR}/backups/elasticsearch

#dc build --pull
#
dc up -d database elasticsearch
dc run --rm importer bash /app/docker-wait.sh

#
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
	echo $tablename
	dc exec -T database update-table.sh bag $tablename public dataselectie
done

#
dc run --rm importer python manage.py import --bagdbindexes
dc run --rm importer python manage.py import --bagdbconstraints

dc run --rm importer python manage.py migrate contenttypes
dc run --rm importer python manage.py elastic_indices --recreate

# import..indexes.
dc run --rm importer bash docker-index-bag.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc run importer /app/elk-bag-backup.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups
