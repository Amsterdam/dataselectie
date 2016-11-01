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

dc run --rm importer

# create the new elastic indexes
dc up importer_el1 importer_el2 importer_el3
# wait until all building is done
docker wait jenkins_importer_el1_1 jenkins_importer_el2_1 jenkins_importer_el3_1

dc run --rm el-backup
dc down 
