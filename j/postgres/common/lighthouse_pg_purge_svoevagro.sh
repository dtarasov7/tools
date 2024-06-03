#!/bin/bash
#set -x

WHEREIS_DOCKER=$(whereis docker | awk '{print $2}')
LOG_PATH=/opt/lhciserver_postgres/scripts
PG_CONT_NAME=postgres
PG_DB=lighthouse_ci_db
PG_USER=lighthouse

CHECK_ID_EXIST=$(echo SELECT id FROM projects | $WHEREIS_DOCKER exec -i $PG_CONT_NAME psql -U $PG_USER -d $PG_DB | grep -v id | grep -v rows | grep -i '[a-z]' | tr '\n' ' ')
START_SCRIPT=$(date)

echo "= Start script: $START_SCRIPT =" >> $LOG_PATH/lighthouse_pg_purge.log
for ID_PROJECT in d8a69f83-eac8-4285-bd78-de9882628a5a
do
PROJECT_NAME=$(echo SELECT name FROM projects WHERE \"id\" \= \'$ID_PROJECT\' | $WHEREIS_DOCKER exec -i $PG_CONT_NAME psql -U $PG_USER -d $PG_DB | grep -v name | grep -v row | grep -i '[a-z]' | tr -d ' ')
if [[ $CHECK_ID_EXIST =~ (^|[[:space:]])$ID_PROJECT($|[[:space:]]) ]]; then
        echo "# Project ID '$ID_PROJECT' with name '$PROJECT_NAME' exist"
COUNT_IDS=$(echo create local temp view delete_ids AS \(SELECT id FROM builds where \(\(\"createdAt\" \< now\(\) \- interval \'7 day\' and extract\(hour from \"createdAt\"\) \!\= 16 and extract\(hour from \"createdAt\"\) \!\= 17\) or \"createdAt\" \< now\(\) \- interval \'30 day\'\) and \"projectId\" \= \'$ID_PROJECT\'\)\; SELECT count\(\*\) AS exact_count FROM delete_ids | $WHEREIS_DOCKER exec -i $PG_CONT_NAME psql -U $PG_USER -d $PG_DB)
COUNT_IDS_SHOW=$(echo $COUNT_IDS | awk '{print $5}')
if [ "$COUNT_IDS_SHOW" == "0" ]; then
        echo "# No data to delete"
else
        echo "# $COUNT_IDS_SHOW builds will be deleting..."
        echo create local temp view delete_ids AS \(SELECT id FROM builds where \(\(\"createdAt\" \< now\(\) \- interval \'7 day\' and extract\(hour from \"createdAt\"\) \!\= 16 and extract\(hour from \"createdAt\"\) \!\= 17\) or \"createdAt\" \< now\(\) \- interval \'30 day\'\) and \"projectId\" \= \'$ID_PROJECT\'\)\; DELETE FROM runs r WHERE exists\(select 1 from delete_ids where id \= r.\"buildId\"\)\; DELETE FROM statistics s WHERE exists\(select 1 from delete_ids where id \= s.\"buildId\"\)\; DELETE FROM builds b WHERE exists\(select 1 from delete_ids where id \= b.\"id\"\)\; | $WHEREIS_DOCKER exec -i $PG_CONT_NAME psql -U $PG_USER -d $PG_DB
        fi
else
        echo "# Project ID '$ID_PROJECT' doesn't exist"
        fi
done >> $LOG_PATH/lighthouse_pg_purge.log
echo "= Stop script: $(date) =" >> $LOG_PATH/lighthouse_pg_purge.log
