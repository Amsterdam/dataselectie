#!/bin/bash

DIR="$(dirname $0)"

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # show commands in log

dc() {
	docker-compose -p ds_brk -f ${DIR}/docker-compose.yml $*
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

# This is added because (for unknown reasons), Jenkins is configured
# to restore the postgres dump from this job into the dataselectie db
# in the Postgres cluster (and not from import-hr.sh). On Azure, we
# run indexing jobs that consume from this cluster and require the presence of the hr table.
dc exec -T database update-table.sh handelsregister hr_dataselectie public dataselectie

dc run --rm importer python manage.py migrate contenttypes

# create dataselectie BRK tables and views
dc run --rm importer python manage.py brk_tables_views --validate
dc exec -T database backup-db.sh dataselectie

dc run --rm database chmod -R 777 /tmp/backups

# create dataselectie BRK indexes
dc run --rm importer python manage.py elastic_indices --recreate brk

dc run --rm importer /app/docker-index-brk.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc run --rm importer /app/elk-brk-backup.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc down
