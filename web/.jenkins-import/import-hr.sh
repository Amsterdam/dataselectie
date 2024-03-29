#!/bin/bash

DIR="$(dirname $0)"

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
	docker-compose -p ds_hr -f ${DIR}/docker-compose.yml $*
}

# remove old stuff.
trap 'dc kill ; dc rm -f -v' EXIT

dc rm -f

dc pull
dc build


rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

# Retry once when docker-compose pull fails due to network errors
dc pull database elasticsearch || dc pull database elasticsearch
dc up -d database elasticsearch
dc run --rm importer bash /app/docker-wait.sh

source ${DIR}/get_bag_tables.sh

dc run --rm importer python manage.py import --bagdbindexes
dc run --rm importer python manage.py import --bagdbconstraints

dc exec -T database update-table.sh handelsregister hr_dataselectie public dataselectie

dc run --rm importer python manage.py migrate contenttypes
dc run --rm importer python manage.py elastic_indices --recreate hr

# create dataselectie HR indexes

dc run --rm importer /app/docker-index-hr.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc run --rm importer /app/elk-hr-backup.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc down
