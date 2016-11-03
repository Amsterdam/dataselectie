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
dc exec -T database_BAG dropdb --if-exists -U postgres atlas
dc exec -T database_BAG createuser -U postgres atlas
dc exec -T database_BAG pg_restore --if-exists -j 4 -c -C -d postgres -U postgres /mnt/dumps/bag.dump

dc run --rm importer
dc run --rm el-backup
dc down 
