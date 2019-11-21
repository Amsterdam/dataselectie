#!/bin/bash

DIR="$(dirname $0)"

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
	docker-compose -p dataselectie -f ${DIR}/docker-compose.yml $*
}

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*
}

dc pull

dc build --pull

dc up -d database

source ${DIR}/collect-tables.sh

for tablename in "${bag_tables[@]}"
do
dc exec -T database update-table.sh bag_v11 $tablename public dataselectie
done

dc exec -T database update-table.sh handelsregister hr_dataselectie public dataselectie

dc run --rm importer

dc exec importer bash -c "/app/docker-wait.sh \ && python manage.py elastic_indices bag --partial=1/3 --build" &
dc exec importer bash -c "python manage.py elastic_indices bag --partial=2/3 --build" &
dc exec importer bash -c "python manage.py elastic_indices bag --partial=3/3 --build"

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

dc run --rm el-backup
dc down
