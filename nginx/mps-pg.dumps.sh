#!/bin/bash
#set -x

WHEREIS_DOCKER=$(whereis docker | awk '{print $2}')
PG_IMAGE=docker.io/bitnami/postgresql:16.0.0-debian-11-r10
PG_CONT_NAME=pg-dump
PG_BK_PATH=/bitnami/postgresql/data/backup
PG_DB=postgres
PG_USER=postgres
PG_PASSWD=12Qwaszx
HOST_BK_PATH=/opt/mps-postgresql-dump/dumps
LOG_PATH=/opt/mps-postgresql-dump
NODE_EXPORTER_DIR=/opt/ans_VMCluster_deploy/nodeExporter/custom_metrics
START_SCRIPT=$(date)

echo "=== Start script: $START_SCRIPT ===" >> $LOG_PATH/pg-dumps.log

for DB in cos-billboard cos-cms cos-history cos-quiz cos-scheduler cos-statistic directory idea-bank keycloak notifications storage synapse synapse-mskguz us postgres
do
        echo "= $DB ="
        docker run --rm --name pg-dump --env 'PGPASSWORD=12Qwaszx' -v /opt/mps-postgresql-dump/dumps:/bitnami/postgresql/data/backup docker.io/bitnami/postgresql:16.0.0-debian-11-r10 /bin/bash -c "pg_dump -h 10.80.110.5 -p 5432 -U postgres -d $DB -Z1 -Fc > /bitnami/postgresql/data/backup/$DB-$(date +%Y-%m-%d).dump"
#done >> $LOG_PATH/pg-dumps.log
#echo "=== Stop script: $(date) ===" >> $LOG_PATH/pg-dumps.log

        FOR_DELETE=$(ls -tr /opt/mps-postgresql-dump/dumps/$DB-*.dump | head -n -3)

        while IFS= read -r FILE_PATH; do
        if [ -z "$FILE_PATH" ]; then
                echo "No $DB dump files for delete"
        else
                FILE_NAME=$(basename ${FILE_PATH})
                ls $FILE_PATH | xargs --no-run-if-empty rm
                echo "$DB dump file $FILE_NAME was deleted"
        fi
        done <<< "$FOR_DELETE"
#done >> $LOG_PATH/pg-dumps.log
        echo "=== Stop script: $(date) ===" >> $LOG_PATH/pg-dumps.log

        # metrics
        TOTAL_OBJECTS=$( ls $HOST_BK_PATH/$DB-* | wc -l )
        TOTAL_OBJECTS_SIZE=$( du -c $HOST_BK_PATH/$DB-* | grep total | cut -f1 )
        OLDEST_OBJECTS=$( ls -tr $HOST_BK_PATH/$DB-* | head -1 )
        OLDEST_OBJECTS_TIME=$( ls -l --time-style=+%s $OLDEST_OBJECTS | awk '{print$6}' )
        LAST_OBJECTS=$( ls -t $HOST_BK_PATH/$DB-* | head -1 )
        LAST_OBJECTS_TIME=$( ls -l --time-style=+%s $LAST_OBJECTS | awk '{print$6}' )
        echo "pgdump_total_backups{pg_db="\"$DB"\"} $TOTAL_OBJECTS" >> $NODE_EXPORTER_DIR/mps_pgdump.prom.$$
        echo "pgdump_total_size_backups{pg_db="\"$DB"\"} $TOTAL_OBJECTS_SIZE" >> $NODE_EXPORTER_DIR/mps_pgdump.prom.$$
        echo "pgdump_oldest_backup{pg_db="\"$DB"\"} $OLDEST_OBJECTS_TIME" >> $NODE_EXPORTER_DIR/mps_pgdump.prom.$$
        echo "pgdump_last_backup{pg_db="\"$DB"\"} $LAST_OBJECTS_TIME" >> $NODE_EXPORTER_DIR/mps_pgdump.prom.$$

done >> $LOG_PATH/pg-dumps.log
mv $NODE_EXPORTER_DIR/mps_pgdump.prom.$$ $NODE_EXPORTER_DIR/mps_pgdump.prom

