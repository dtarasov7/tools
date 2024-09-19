#!/bin/bash
if [ $# -lt 1 ]; then 
  echo usage $0 mask
  exit 0
fi
for d in $(docker image ls | grep $1 | awk '{print$1}' | sort | uniq )
do
   echo "# Deleting $d"
   docker rmi -f  $(docker images | grep $d | awk '{print$3}' | uniq | tail -n +5) #+6)
done
## Delete <none> containers
none=$(docker images | grep '<none>' | wc -l)
if [ "$none" -eq "0" ]; then
   echo "# <none> containers not found"
   exit;
else
   echo "# Deleting <none> containers"
   docker rmi -f $(docker images | grep '<none>')
fi
