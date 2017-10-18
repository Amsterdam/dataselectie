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

dc exec --rm importer bash /app/docker-wait.sh

dc exec -T database update-table.sh handelsregister hr_dataselectie public dataselectie

#dc exec --rm importer python manage.py migrate contenttypes
#dc exec --rm importer python manage.py elastic_indices --recreate


dc exec --rm importer python manage.py elastic_indices hr --partial=1/3 --build &
dc exec --rm importer python manage.py elastic_indices hr --partial=2/3 --build &
dc exec --rm importer python manage.py elastic_indices hr --partial=3/3 --build

FAIL=0

for job in `jobs -p`
do
	echo $job
	wait $job || let "FAIL+=1"
done

echo $FAIL

if [ "$FAIL" == "0" ];
then
    echo "YAY!"
else
    echo "FAIL! ($FAIL)"
    echo 'Elastic Import Error. 1 or more workers failed'
    exit 1
fi

dc run --rm el-backup curl -X PUT http://el:9200/_snapshot/backup -d '{ \"type\": \"fs\", \"settings\": { \"location\": \"/tmp/backups\" }}'
dc run --rm el_backup curl -X PUT http://el:9200/_snapshot/backup/ds_hr_index?wait_for_completion=true -d '{ \"indices\": \"ds_hr_index\" }'
dc run --rm el_backup chmod -R 777 /tmp/backups

dc down
