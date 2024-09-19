#!/bin/bash

set -x

url="https://10.80.:9200"
urlk="https://10.80.:5601"
auth="admin:x7"
name="datalab-varshb"

#echo "Создание пространства $name"
#curl -u $auth -k -X PUT $url/_opendistro/_security/api/tenants/$name -H 'Content-Type: application/json' -d '{"description": "Виртуальный помощник"}'
#echo ""

#echo "Создание роли $name"
#curl -u $auth -k -X PUT $url/_opendistro/_security/api/roles/$name -H 'Content-Type: application/json' -d @role_varshb.json
#echo ""

echo "Создание пользователя $name"
curl -u $auth -k -X PUT $url/_opendistro/_security/api/internalusers/$name -H 'Content-Type: application/json' -d '{"password": "Ert##34##56"}'
echo ""

#echo "Мапинг пользователей на роли"
#curl -u $auth -k -X PATCH $url/_opendistro/_security/api/rolesmapping -H 'Content-Type: application/json' -d @role_mapping_varshb.json
#echo ""

#echo "Патерн индексов $name*"
#curl -u $auth -k -X POST $urlk/api/saved_objects/index-pattern/crshb?overwrite=true -H "securitytenant: $name" -H "kbn-xsrf: true" -H "Content-Type: application/json" -d '{"attributes":{"title":"varshb*","timeFieldName":"@timestamp"}}'
#echo ""

echo "All done"

