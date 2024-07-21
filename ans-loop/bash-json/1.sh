#!/bin/bash
#jq -r '.SITE_DATA | to_entries | .[] | .key + "=" + (.value | @sh)' 1.json
#set -x

eval "declare -A data=($(cat 1.json | jq -r '.SITE_DATA | to_entries | .[] | @sh "[\(.key)]=\(.value)"' ))"

#echo ${data[@]}

echo ${data[URL]}
echo ${data[AUTHOR]}
echo ${data[CREATED]}

##eval "$(jq -r '.SITE_DATA | to_entries | .[] | .key + "=" + (.value | @sh)' < 1.json)"

declare $(jq -r '.SITE_DATA | to_entries | .[] | "export \(.key)=\(.value)"' < 1.json)
echo ---------------------
echo $URL

