#!/bin/bash
## Delete <none> containers
none=$(docker images | grep '<none>' | wc -l)
if [ "$none" -eq "0" ]; then
   echo "# <none> containers not found"
   exit;
else
   echo "# Deleting <none> containers"
   docker rmi -f $(docker images | grep '<none>')
fi
