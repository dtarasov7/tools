#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Usage: $0 service"
  exit 1
fi

#docker-compose stop $1
#docker-compose kill $1
docker-compose rm -f -s $1
docker-compose up -d  $1