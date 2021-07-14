#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Usage: $0 file"
  exit 1
fi

#set -x


regexp3="(.*)-override"
regexp2="^#"
regexp1="(.*\/)(.*)"
regexp0="Loaded image: (.*)"

DR="10.27.134.6:5000/rshb"

set -e
set -x

REZ=$(docker load -i /data/archive/$1)

if [[ $REZ =~ $regexp0 ]]; then
  fullname=${BASH_REMATCH[1]}
  echo $fullname
  if [[ $fullname =~ $regexp1 ]]; then
    dname=${BASH_REMATCH[2]}
    echo $dname
    docker tag $fullname $DR/$dname
    docker push $DR/$dname
    docker image remove $DR/$dname
  else
    dname=$fullname
    echo $dname
    docker tag $fullname $DR/$dname
    docker push $DR/$dname
    docker image remove $DR/$dname
  fi

fi
                
#echo $REZ

