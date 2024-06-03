#!/bin/bash

HOST='http://10.80.252.20:3000'
DASH_DIR=/data/minio/grafana/prod_dtln

# Declare a list with the api keys using as a prefix the organization name plus "_" character
declare -a StringArray=("main_eyJrIjoiN1QzVkFTOVpxcnByS3BpcWZJWGViT3JKMU9nNlJDR08iLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjF9" "admin-dtln_eyJrIjoiOTBUTExDYXJSZzZqOEY5TXhyZHdYMndUY091azF2SlQiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjJ9" "svoe-dtln_eyJrIjoiRmpxaEs2dEozSkR6a3VnMDNobWE0VUZTZzBqMG5tNFUiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjR9" "cos-dtln_eyJrIjoiR1pGWGxxUERXN2VXVGZHT1hCZVdrb1dTc0R1WlI4RXYiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjN9" "digital-back_eyJrIjoiV0dPclV5QlNrb1QzdUxHTGhEaEc3aDNhaENpT1liSWUiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjV9" "ndbo-dtln_eyJrIjoiQjVnQTdUN3BSUjcwaDJ5MnZBMEJXaEFVS1FESzVlRlciLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjZ9" "dit-dtln_eyJrIjoiVUZxeE96ZnJWNklpT2RkOGsxbWV3WWUzZnRJdG5KN1UiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjh9" "lt-dtln_eyJrIjoiS2hPY2tpUVFjc3hNMEFlQWhWQU5WOHkzRlZFc1RUcGEiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjd9")

# Iterate through api keys:
for API_KEY in "${StringArray[@]}"; do
    ORG=$(echo $API_KEY | cut -d "_" -f1) # Name of the organization based on the prefix
    KEY=$(echo $API_KEY | cut -d "_" -f2) # API Key for that organization after removing the prefix

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
