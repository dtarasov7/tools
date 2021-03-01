#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Usage: $0 file"
  exit 1
fi

set -e
#set -x

regexp="((.+)\/)+(.+)"
regexp3="(.+):(.+)"
regexp2="^#"

while IFS='' read -r line || [[ -n "$line" ]]; do
    # НЕ Пустая строка
    if [ ! -z "$line" ]; then	             # НЕ Пустая строка
        if ! [[ $line =~ $regexp2 ]]; then   # НЕ Закоментированая строка
            if [[ $line =~ $regexp3 ]]; then  # есть имя репозитория
		name=${BASH_REMATCH[1]}
		ver=${BASH_REMATCH[2]}
                if [[ $name =~ $regexp ]]; then  # есть имя репозитория
                    dname=${BASH_REMATCH[3]}
                else
    	    	    dname=$line
    		fi
            fi
            echo "image $name:$ver       filename $dname-$ver.log ..."
	    ./run_trivy_docker_image_silent.sh "$name:$ver" >$dname-$ver.log
        fi
    fi
done < "$1"


