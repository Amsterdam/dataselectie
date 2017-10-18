#!/bin/bash

DIR="$(dirname $0)"

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
	docker-compose -p ds -f ${DIR}/docker-compose.yml $*
}


dc pull

#rm -rf ${DIR}/backups
#mkdir -p ${DIR}/backups

dc build --pull

dc up -d database elasticsearch

dc run --rm importer bash /app/docker-wait.sh

#dc exec -T database update-table.sh handelsregister hr_dataselectie public dataselectie

#dc run --rm importer python manage.py migrate contenttypes
#dc run --rm importer python manage.py elastic_indices --recreate

dc run --rm importer /app/docker-index-hr.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc run --rm importer /app/elk-hr-backup.sh

dc run --rm elasticsearch chmod -R 777 /tmp/backups

dc down
