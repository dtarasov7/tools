#!/bin/bash
#set -x

if [ "$1" == "-h" ]; then
cat << EOF
Пример запуска: ./$(basename "$0") /путь/до/файла.yml
# Создание/обновление пространств
# Создание/обновление ролей
# Создание пользователей (в случае отсутствия)
# Мапирование ролей
EOF
  exit 0
fi

PATH_TO_FILE=$1
ES_URL=https://admin:x7RHtzsIP@10.80.:9200
KIBANA_URL=https://admin:x7RzsIP@10.80.:5601

# Create/update tenant
for tenant in $(yq eval -o=j $PATH_TO_FILE | jq -rc '.tenants[]'); do
        tenant_name=$(echo $tenant | jq -r '.name')
        tenant_description=$(echo $tenant | jq -r '.description')
        echo "# Создание пространства '$tenant_name'"
curl -k -X PUT -H "Content-Type: application/json" -d '{
        "description": "'"$tenant_description"'"
}' $ES_URL/_opendistro/_security/api/tenants/$tenant_name; echo
done

# Create/update role
for role in $(yq eval -o=j $PATH_TO_FILE | jq -rc '.roles[]'); do
        role_name=$(echo $role | jq -r '.name')
        role_content=$(echo $role | jq -c 'del(.name)')
        echo "# Создание роли '$role_name'"
curl -k -X PUT -H 'Content-Type: application/json' -d ''$role_content'' $ES_URL/_opendistro/_security/api/roles/$role_name; echo
done

# Create user if user not exists
for role in $(yq eval -o=j $PATH_TO_FILE | jq -rc '.users[]'); do
        user_name=$(echo $role | jq -r '.name' -)
        user_pass=$(echo $role | jq -r '.password' -)
# check if user exists
check_user_exists=$(curl -k -s -X GET $ES_URL/_opendistro/_security/api/internalusers/$user_name | grep status)
if [ $? -eq 0 ]; then
        echo "# Создание пользователя '$user_name'"
curl -k -X PUT -H "Content-Type: application/json" -d '{
        "password": "'"$user_pass"'"
}' $ES_URL/_opendistro/_security/api/internalusers/$user_name; echo
else
        echo "# Пользователь '$user_name' уже существует"
fi
done

# Role mappings
echo "# Мапирование ролей"
mapping_content=$(yq eval -o=j .rolesmapping[] $PATH_TO_FILE | jq -c . | tr '\n' ',' | sed '$ s/.$//')
curl -k -X PATCH -H "Content-Type: application/json" -d '['$mapping_content']' $ES_URL/_opendistro/_security/api/rolesmapping; echo

# Create index pattern for tenant
for index_pattern in $(yq eval -o=j $PATH_TO_FILE | jq -rc '.index_pattern[]'); do
        tenant_name=$(echo $index_pattern | jq -r '.tenant' -)
yq eval -o=j $PATH_TO_FILE | jq -rc ".index_pattern[]| select(.tenant==\"$tenant_name\").index_name[]" | while read index_pattern; do
check_index_pattern=$(curl -k -s -X GET -H "Content-Type: application/json" -H "securitytenant: $tenant_name" "$ES_URL/.kibana/_search?size=10000&filter_path=hits.hits._source.index-pattern.title&pretty" | jq -rc '.[].hits[]._source[].title | select(. == ("'$index_pattern'"))')
if [[ -n $check_index_pattern ]]; then
        echo "# Index pattern '$index_pattern' для пространства '$tenant_name' уже существует"
else
        echo "# Создание index pattern '$index_pattern' для пространства '$tenant_name'"
curl -k -s -X POST -H "Content-Type: application/json" -H "kbn-xsrf: true" -H "securitytenant: $tenant_name" -d '{
"attributes":{
  "title":"'"$index_pattern"'",
  "timeFieldName":"@timestamp"
  }
}' $KIBANA_URL/api/saved_objects/index-pattern; echo
fi
done
done
