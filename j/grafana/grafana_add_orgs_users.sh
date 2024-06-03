#!/bin/bash
#set -x
if [ "$1" == "-h" ]; then
cat << EOF
Пример запуска: ./$(basename "$0") /путь/до/файла.yml
# Создание организации
# Создание пользователя и назначение его определенной организации
# Добавление/смена прав (роли)
# Добавление пользователю глобальныйх админских прав
EOF
  exit 0
fi

PATH_TO_FILE=$1
GR_URL=http://admin:admin@localhost:3000

# Create Org
yq eval '.grafana_organization[] | .name' $PATH_TO_FILE | while read org
do
echo "# Create organization '$org'"
addorg_status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X POST -H "Content-Type: application/json" -d '{
  "name":"'$org'"
}' $GR_URL/api/orgs; echo)
if [[ "$addorg_status_code" == 200 ]] ; then
        echo -e "Organization '$org' successfully created in server\n"
elif [[ "$addorg_status_code" == 409 ]]; then
        echo -e "Organization '$org' already exists in server\n"
fi
done

# Create user and add to Org with his roles
for content in $(yq eval -o=j $PATH_TO_FILE | jq -cr '.grafana_users[]'); do
      user_name=$(echo $content | jq -r '.name' -)
      org_name=$(echo $content | jq -r '.OrgId' -)
      user_role=$(echo $content | jq -r '.role' -)
      is_admin=$(echo $content | jq -r '.isGrafanaAdmin' -)
# get org id from org name
      org_id=$(curl -s -X GET -H 'Content-Type: application/json' $GR_URL/api/orgs/name/$org_name | jq -r .id)
# add user to server (global) to special Org with default role Viewer
echo "# Add user '$user_name' to server"
adduser_status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X POST -H "Content-Type: application/json" -d '{
  "name": "'$user_name'",
  "email": "'$user_name'@localhost",
  "login": "'$user_name'",
  "password": "'$user_name'",
  "OrgId": '$org_id'
}' $GR_URL/api/admin/users; echo)
if [[ "$adduser_status_code" == 200 ]] ; then
        echo "User '$user_name' successfully created in server"
elif [[ "$adduser_status_code" == 412 ]]; then
        echo "User '$user_name' already exists in server"
fi
echo "# Add user '$user_name' to '$org_name' organization with role '$user_role'"
# get user id by user name
        user_id=$(curl -s "$GR_URL/api/users" -H 'Content-Type: application/json' | jq -r '.[] | "\(.id) \(.login)"' | grep $user_name | cut -d " " -f 1)
# update user data
adduser_org_status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X POST -H 'Content-Type: application/json' -d '{
  "loginOrEmail": "'$user_name'",
  "role": "'$user_role'"
}' $GR_URL/api/orgs/$org_id/users; echo)
if [[ "$adduser_org_status_code" == 200 ]]; then
        echo -e "User $user_name successfully added to '$org_name'"
elif [[ "$adduser_org_status_code" == 409 ]]; then
        echo "User '$user_name' already exists in organization"
else
        echo -e "Failed to add user to organization"
fi
# update user data
adduser_role_status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X PATCH -H 'Content-Type: application/json' -d '{
  "role": "'$user_role'"
}' $GR_URL/api/orgs/$org_id/users/$user_id; echo)
if [[ "$adduser_role_status_code" == 200 ]]; then
        echo -e "Role for user '$user_name' successfully added/updated\n"
else
        echo -e "Failed. Role add error\n"
fi
if [ "$is_admin" = true ] ; then
echo "# Add Global Admin role for user '$user_name'"
# add user global admin role
addrole_admin_status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X PUT -H 'Content-Type: application/json' -d '{
  "isGrafanaAdmin": true
}' $GR_URL/api/admin/users/$user_id/permissions; echo)
if [[ "$addrole_admin_status_code" == 200 ]]; then
        echo -e "Global Admin role for user $user_name successfully added\n"
else
        echo -e "Failed\n"
fi
fi

done

