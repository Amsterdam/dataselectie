#!/bin/bash

dc() {
	docker-compose -f $(dirname $0)/docker-compose.yml $*
}

source $(dirname $0)/web/.jenkins-import/get_bag_tables.sh
