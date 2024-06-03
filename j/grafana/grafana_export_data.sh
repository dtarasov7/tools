#!/bin/bash

HOST=10.80.252.20:3000
USER=admin
PASSWD=8n7Se0BqDQYRzEwl6yVS
PATH_DIR=/data/minio/grafana/prod_dtln
BKDATE=$(date -d "today" +"%Y-%m-%d")

if [[ -f "$PATH_DIR/grafana_export_$BKDATE" ]]; then
> $PATH_DIR/grafana_export_$BKDATE
fi

#Определяем список всех имеющихся организаций
curl -s "$HOST/api/orgs" -u $USER:$PASSWD | jq -c -r .[].name | while read orgs
do
#orgs=$(curl -s "$HOST/api/orgs" -u $USER:$PASSWD | jq -c -r .[].name)
cat <<EOF >> $PATH_DIR/grafana_export_$BKDATE
Org:$orgs
EOF
done

#orgs=$(curl -s "$HOST/api/orgs" -u $USER:$PASSWD | jq -r '.[] | "\(.id) \(.name)"' | sed 's/ /,/')
#orgs=$(curl -s "$HOST/api/orgs" -u $USER:$PASSWD | jq -c -r .[].name)
#cat <<EOF > grafana_$BKDATE.txt
#List of Organizations
#Org: $orgs

#EOF

#Экспорт информации пользователя: id name,login,name,role,email
for org_id in $(curl -s "$HOST/api/orgs" -u $USER:$PASSWD | jq .[].id); do
org_name=$(curl -s "$HOST/api/orgs/$org_id" -u $USER:$PASSWD | jq -r .name)
cat <<EOF >> $PATH_DIR/grafana_export_$BKDATE
#################
#users and datasources
EOF

for user in $(curl -s "$HOST/api/orgs/$org_id/users" -u $USER:$PASSWD | jq -r '.[] | {login,name,role,email} | join(",")' | sed '/^admin/d'); do
#for user in $(curl -s "$HOST/api/orgs/$org_id/users" -u $USER:$PASSWD | jq -c -r '.[] | {login,name,role,email}' | sed '/admin/d'); do
cat <<EOF >> $PATH_DIR/grafana_export_$BKDATE
User:$org_name,$user
EOF
done

#Экспорт всех датасоурсов из организаций
for datasource in $(curl -s -XGET -H "x-grafana-org-id: $org_id" "$HOST/api/datasources" -u $USER:$PASSWD | jq -r '.[] | "\(.name),\(.type),\(.typeName),\(.access),\(.url),\(.basicAuth),\(.isDefault)"'); do
cat <<EOF >> $PATH_DIR/grafana_export_$BKDATE
Datasource:$org_name,$datasource
EOF
done

done

#Удалить файлы старше 7 дней
find $PATH_DIR/ -type f -name 'grafana_export_*' -mtime +7 -exec rm {} \;
