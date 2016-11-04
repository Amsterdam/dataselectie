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
#dc exec -T database_BAG pg_restore -j 4 -c --if-exists -d postgres -U postgres /tmp/import/bag.dump

dc run --rm importer
dc run --rm el-backup
dc down 
