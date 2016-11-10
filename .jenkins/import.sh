#!/bin/sh

DIR="$(dirname $0)"

dc() {
	docker-compose -p dataselectie -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc build --pull
dc up -d database_BAG
sleep 10 # waiting for postgres to start
dc exec -T database_BAG update-db.sh atlas
#dc exec -T database_BAG pg_restore -j 4 -c --if-exists -d atlas -U postgres /tmp/import/bag.dump
#dc exec -T database_BAG pg_restore -j 4 -t bag_buurt -t bag_buurtcombinatie  -t bag_gebiedsgerichtwerken -t bag_gebruik -t bag_gemeente -t bag_grootstedelijkgebied -t bag_ligplaats -t bag_nummeraanduiding -t bag_openbareruimte -t bag_pand -t bag_stadsdeel -t bag_standplaats  -t bag_verblijfsobject -t bag_verblijfsobjectpandrelatie -t bag_woonplaats -c --if-exists -d atlas -U postgres /tmp/import/bag.dump

# clear elastic indices and recreate
dc run --rm importer
# create the new elastic indexes
dc up importer_el1 importer_el2 importer_el3
# wait until all building is done
docker wait jenkins_importer_el1_1 jenkins_importer_el2_1 jenkins_importer_el3_1

# run the backup shizzle
dc run --rm el-backup
dc down 
