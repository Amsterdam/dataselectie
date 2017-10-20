#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error


python manage.py elastic_indices hr --partial=1/3000 --build &
python manage.py elastic_indices hr --partial=2/3000 --build &
python manage.py elastic_indices hr --partial=3/3000 --build

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
