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

DA="/data/docker_archive"
DR="10.27.134.6:5000/crft"

#regexp="((.+)\/)+(.+)"
regexp2="#(.)+"


regexp3="(.*)-override"
#regexp1="(.*\/)(.*)"
regexp0="Loaded image: (.*)"

regexp1="(.+)_(.+).tar"



set -e
#set -x

while IFS='' read -r line || [[ -n "$line" ]]; do
    if [ ! -z "$line" ]; then	# не пустая строка
        if ! [[ $line =~ $regexp2 ]]; then  # не комментарий
            echo -n "$line ->"
            if [[ $line =~ $regexp1 ]]; then
                name=${BASH_REMATCH[1]}
                #echo "name "$name
                tag=${BASH_REMATCH[2]}
                echo " $DR/$name:$tag"
                docker run --rm -v=$DA:/mnt quay.io/skopeo/stable:v1.2.3 copy --dest-tls-verify=false --dest-creds svc-crft:23Wesdxc% docker-archive:/mnt/$line docker://$DR/$name:$tag
              else
                echo "error file name $line"
            fi

	    #docker load -i $DA/$line
#	    REZ=$(docker load -i $DA/$line)
#	    if [[ $REZ =~ $regexp0 ]]; then  # Загрузили
#		echo "OK!"
#	    fi
	fi
    fi
done < "$1"


