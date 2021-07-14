#!/bin/bash
#set -x

if [ $# -lt 1 ]
then
  echo "Usage: $0 файл_со_списком_докер_образов"
  exit 1
fi

regexp3="(.*)-override"
regexp1="(.*\/)(.*)"
regexp0="Loaded image: (.*)"

DR="10.27.134.6:5000/crft"

set -e
set -x

regexp="((.+)\/)+(.+)"
regexp2="#(.)+"

while IFS='' read -r line || [[ -n "$line" ]]; do
    if [ ! -z "$line" ]; then
        echo "$line"
        if ! [[ $line =~ $regexp2 ]]; then
            docker image rm -f $line
        fi
    fi
done < "$1"


