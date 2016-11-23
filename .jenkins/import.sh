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
dc exec -T database_HR update-db.sh handelsregister

dc run --rm importer

# create the new elastic indexes
dc up importer_el1 importer_el2 importer_el3
# wait until all building is done
import_status=`docker wait jenkins_importer_el1_1 jenkins_importer_el2_1 jenkins_importer_el3_1`

# count the errors.
import_error=`echo $import_status | grep -o "1" | wc -l`

if [ $import_error > 0 ]
then
    echo 'Elastic Import Error. 1 or more workers failed'
    exit -1
fi

dc run --rm el-backup
dc down
