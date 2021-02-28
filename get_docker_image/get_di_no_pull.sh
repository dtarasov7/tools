#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Usage: $0 file"
  exit 1
fi

set -e
#set -x

regexp="((.+)\/)+(.+)"
regexp2="^#"

while IFS='' read -r line || [[ -n "$line" ]]; do
    # НЕ Пустая строка
    if [ ! -z "$line" ]; then
	# НЕ Закоментированая строка
        if ! [[ $line =~ $regexp2 ]]; then
    	    # Change " to -
            if [[ $line =~ $regexp ]]; then
                name=${BASH_REMATCH[3]}
                #docker save $line >$2/${BASH_REMATCH[3]}.tar
            else
                name=$line
                #docker save $line >2/$line.tar
            fi
#            echo "pull $line ..."
#    	    docker pull $line
    	    echo "save to tar.gz $name ..."
    	    name="${name/:/-}"
	    docker save $line | gzip > /opt/docker_archive/$name.tar.gz
	fi
    fi
done < "$1"


