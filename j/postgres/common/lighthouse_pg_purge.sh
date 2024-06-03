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
for ID_PROJECT in db8ef0ad-c1fa-406c-8344-c6a4908eb852 c089a32e-d305-4983-9fed-bd4ed44d37b5 dc3fc372-95ff-4647-8945-7ddb8f6c5524 6a4737c4-792f-4c1b-97e0-125df8bef4be 6ddb1c54-5b0a-467d-83a2-3350c5431a31 b424ddae-2905-455b-8def-f48fd93f19f9 ce6ff4b2-793e-4982-bcd1-5727082ba9b9
do
PROJECT_NAME=$(echo SELECT name FROM projects WHERE \"id\" \= \'$ID_PROJECT\' | $WHEREIS_DOCKER exec -i $PG_CONT_NAME psql -U $PG_USER -d $PG_DB | grep -v name | grep -v row | grep -i '[a-z]' | tr -d ' ')
if [[ $CHECK_ID_EXIST =~ (^|[[:space:]])$ID_PROJECT($|[[:space:]]) ]]; then
        echo "# Project ID '$ID_PROJECT' with name '$PROJECT_NAME' exist"
COUNT_IDS=$(echo create local temp view delete_ids AS \(SELECT id FROM builds where \(\(\"createdAt\" \< now\(\) \- interval \'7 day\' and extract\(hour from \"createdAt\"\) \!\= 14 and extract\(hour from \"createdAt\"\) \!\= 15\) or \"createdAt\" \< now\(\) \- interval \'30 day\'\) and \"projectId\" \= \'$ID_PROJECT\'\)\; SELECT count\(\*\) AS exact_count FROM delete_ids | $WHEREIS_DOCKER exec -i $PG_CONT_NAME psql -U $PG_USER -d $PG_DB)
COUNT_IDS_SHOW=$(echo $COUNT_IDS | awk '{print $5}')
if [ "$COUNT_IDS_SHOW" == "0" ]; then
        echo "# No data to delete"
else
        echo "# $COUNT_IDS_SHOW builds will be deleting..."
        echo create local temp view delete_ids AS \(SELECT id FROM builds where \(\(\"createdAt\" \< now\(\) \- interval \'7 day\' and extract\(hour from \"createdAt\"\) \!\= 14 and extract\(hour from \"createdAt\"\) \!\= 15\) or \"createdAt\" \< now\(\) \- interval \'30 day\'\) and \"projectId\" \= \'$ID_PROJECT\'\)\; DELETE FROM runs r WHERE exists\(select 1 from delete_ids where id \= r.\"buildId\"\)\; DELETE FROM statistics s WHERE exists\(select 1 from delete_ids where id \= s.\"buildId\"\)\; DELETE FROM builds b WHERE exists\(select 1 from delete_ids where id \= b.\"id\"\)\; | $WHEREIS_DOCKER exec -i $PG_CONT_NAME psql -U $PG_USER -d $PG_DB
        fi
else
        echo "# Project ID '$ID_PROJECT' doesn't exist"
        fi
done >> $LOG_PATH/lighthouse_pg_purge.log
echo "= Stop script: $(date) =" >> $LOG_PATH/lighthouse_pg_purge.log
