#!/bin/bash

set -u   # crash on missing env variables
set -e   # stop on any error


curl -s -v -f -XPUT http://elasticsearch:9200/_snapshot/backup -H 'Content-Type: application/json' -d '
{
  "type": "fs",
  "settings": {
      "location": "/tmp/backups" }
}'

curl -s -v -f -XPUT http://elasticsearch:9200/_snapshot/backup/ds_hr_index?wait_for_completion=true -H 'Content-Type: application/json' -d '
{ "indices": "ds_hr_index" }'

