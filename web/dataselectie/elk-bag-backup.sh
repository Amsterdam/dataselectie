#!/bin/bash

set -u   # crash on missing env variables
set -e   # stop on any error


curl -s -v -f -XPUT http://elasticsearch:9200/_snapshot/backup -d '
{
	"type": "fs",
  "settings": {
      "location": "/tmp/backups" }
}'

curl -s -v -f -XPUT http://elasticsearch:9200/_snapshot/backup/ds_bag_index?wait_for_completion=true -d '
{ "indices": "ds_bag_index" }'

