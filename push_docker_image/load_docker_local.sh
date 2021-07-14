#!/bin/bash
#
# Загружаем локально докер контейнеры из tar.gz архивов, расположеных в /data/docker_archive
# список загружаемых архивов передается через файл, который указывается в качестве первого аргумента
# В списке имна архивов без директории
#
if [ $# -lt 1 ]
then
  echo "Usage: $0 файл_со_списком_apхивов"
  exit 1
fi

DA=/data/docker_archive

#regexp0="Loaded image: (.*)"
#regexp="((.+)\/)+(.+)"
regexp2="#(.)+"

set -e
#set -x

while IFS='' read -r line || [[ -n "$line" ]]; do
    if [ ! -z "$line" ]; then	# не пустая строка
        echo -n "$line"
        if ! [[ $line =~ $regexp2 ]]; then  # не комментарий
	    docker load -i $DA/$line
#	    REZ=$(docker load -i $DA/$line)
#	    if [[ $REZ =~ $regexp0 ]]; then  # Загрузили
#		echo "OK!"
#	    fi
	fi
    fi
done < "$1"

