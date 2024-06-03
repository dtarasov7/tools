#!/bin/bash
DO=$1

if [ "$1" == "-h" ]; then
cat << EOF
Пример запуска: ./$(basename "$0") <arg>
# show_config=yes
# show_status=yes
# backup=(full/delta)
EOF
  exit 0
fi

docker run --rm --name pg_probackup -v /opt/postgres/data:/data -v /opt/postgres/log:/log -v /opt/postgres/docker/pgbak:/mnt/pgbak -v /opt/postgres/docker/run/run_pg_probackup.sh:/usr/local/bin/backup.sh -e TZ=Europe/Moscow -e $DO pg_probackup:12-debian
