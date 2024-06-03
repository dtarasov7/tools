#!/bin/bash
#set -x

WHEREIS_DOCKER=$(whereis docker | awk '{print $2}')
PG_CONT_NAME=postgres
PG_BK_PATH=/var/lib/postgresql/backup
PG_DB=test_db
PG_USER=test_user
HOST_BK_PATH=/opt/postgres/backup

#$WHEREIS_DOCKER exec $PG_CONT_NAME /bin/sh -c "pg_dump -U $PG_USER -d $PG_DB -Ft > $PG_BK_PATH/$PG_DB-$(date +%Y-%m-%d-%H:%M).tar"
$WHEREIS_DOCKER exec $PG_CONT_NAME /bin/sh -c "pg_dump -U $PG_USER -d $PG_DB -Z1 -Fc > $PG_BK_PATH/$PG_DB-$(date +%Y-%m-%d-%H:%M).dump"

#ls -tr /opt/postgres/backup/*.tar | head -n -14 | xargs --no-run-if-empty rm
#FOR_DELETE=$(ls -tr $HOST_BK_PATH/*.tar | head -n -14)
FOR_DELETE=$(ls -tr $HOST_BK_PATH/*.dump | head -n -14)

while IFS= read -r FILE_PATH; do
if [ -z "$FILE_PATH" ]; then
      echo "No dump files for delete"
else
      FILE_NAME=$(basename ${FILE_PATH})
      ls $FILE_PATH | xargs --no-run-if-empty rm
      echo "Dump file $FILE_NAME was deleted"
fi
done <<< "$FOR_DELETE"

# restore command for terminal
#$WHEREIS_DOCKER exec -it $PG_CONT_NAME /bin/sh -c "pg_restore -U $PG_USER -d $PG_DB -v $PG_BK_PATH/$PG_DB-$(date +%Y-%m-%d-%H:%M.dump"
