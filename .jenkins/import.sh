#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -p zelfbediening -f ${DIR}/docker-compose.yml $*
}

#trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc build
dc up -d database_BAG
dc exec -T database_BAG update-atlas.sh
dc run --rm importer
dc run --rm el-backup
dc down 
