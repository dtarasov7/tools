#!/bin/bash

HOST='http://10.:3000'
DASH_DIR=/data/minio/grafana/prod_dtln

# Declare a list with the api keys using as a prefix the organization name plus "_" character
declare -a StringArray=("" "" "" "" )

# Iterate through api keys:
for PI_KEY in "${StringArray[@]}"; do
    ORG=$(echo $PI_KEY | cut -d "_" -f1) # Name of the organization based on the prefix
    KEY=$(echo $PI_KEY | cut -d "_" -f2) # API Key for that organization after removing the prefix

    # Iterate through dashboards using the current API Key
    for dashboard_uid in $(curl -sS -H "Authorization: Bearer $KEY" $HOST/api/search\?query\=\& | jq -r '.[] | select( .type | contains("dash-db")) | .uid'); do
        url=`echo $HOST/api/dashboards/uid/$dashboard_uid | tr -d '\r'`
        dashboard_json=$(curl -sS -H "Authorization: Bearer $KEY" $url)
        dashboard_title=$(echo $dashboard_json | jq -r '.dashboard | .title' | sed -r 's/[ \/]+/_/g' )
        dashboard_version=$(echo $dashboard_json | jq -r '.dashboard | .version')
        folder_title="$(echo $dashboard_json | jq -r '.meta | .folderTitle')"

        # You can export the files like this to keep them organized by organization:
        mkdir -p "$DASH_DIR/$ORG/$folder_title/dashboards_$ORG"
        echo $dashboard_json | jq -r {meta:.meta}+.dashboard  > $DASH_DIR/$ORG/$folder_title/dashboards_$ORG/${dashboard_title}_v${dashboard_version}.json
    done
done
