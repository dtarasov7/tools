#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Usage: $0 file"
  exit 1
fi

#set -x


regexp3="(.*)-override"
##regexp2="^#"
regexp1="(.*\/)(.*)"
regexp0="Loaded image: (.*)"

DR="10.27.134.6:5000/rshb"

set -e
set -x

regexp="((.+)\/)+(.+)"
regexp2="#(.)+"

while IFS='' read -r line || [[ -n "$line" ]]; do
    if [ ! -z "$line" ]; then
        echo "$line"
        if ! [[ $line =~ $regexp2 ]]; then
            if [[ $line =~ $regexp1 ]]; then
	        dname=${BASH_REMATCH[2]}
	        echo $dname
	      else
	        dname=$line
	        echo $dname
	    fi
            docker tag $line $DR/$dname
            docker push $DR/$dname
            docker image remove $DR/$dname

        fi
    fi
done < "$1"


