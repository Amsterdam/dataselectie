#!/bin/bash

DIR="$(dirname $0)"

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
	docker-compose -p ds_bag -f ${DIR}/docker-compose.yml $*
}

# remove old stuff.
dc down
dc rm -f

dc pull
dc build

rm -rf ${DIR}/backups/
mkdir -p ${DIR}/backups/elasticsearch

source ${DIR}/get_bag_tables.sh

#dc build --pull
#
dc up -d database elasticsearch
dc run --rm importer bash /app/docker-wait.sh

#
dc run --rm importer python manage.py migrate contenttypes
dc run --rm importer python manage.py elastic_indices --recreate

# create dataselectie BAG indexes

dc run --rm importer bash docker-index-bag.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc run importer /app/elk-bag-backup.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups
