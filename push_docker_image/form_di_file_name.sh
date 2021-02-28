#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Usage: $0 file"
  exit 1
fi

set -e
#set -x

line=$1

regexp="((.+)\/)+(.+)"

if [[ $line =~ $regexp ]]; then
    name=${BASH_REMATCH[3]}
else
    name=$line
fi
# Change " to -
name="${name/:/-}"
echo $name.tar.gz
exit 0