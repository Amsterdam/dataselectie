#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

python manage.py elastic_indices bkr --partial=1/1 --build

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
