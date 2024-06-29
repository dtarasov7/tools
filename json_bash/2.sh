#!/bin/bash

typeset -A myarray

while IFS== read -r key value; do
    myarray["$key"]="$value"
done < <(jq -r '.SITE_DATA | to_entries | .[] | .key + "=" + .value ' 1.json)

# show the array definition
typeset -p myarray

# make use of the array variables
echo "URL = '${myarray[URL]}'"
echo "CREATED = '${myarray[CREATED]}'"
echo "AUTHOR = ${myarray[AUTHOR]}"

