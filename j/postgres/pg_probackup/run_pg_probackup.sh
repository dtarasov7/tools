#!/bin/bash
#set -x
pg_probackup_backup=/mnt/pgbak
pg_probackup_data=/data
pg_probackup_instance=12
pg_probackup_redundancy=2
pg_probackup_window=2
PGHOST=192.168.3.52
PGPORT=5432
PGDATABASE=test_db
PGUSER=test_user
PGPASSWORD=test_passwd
PGPASSFILE=$pg_probackup_backup/backups/$pg_probackup_instance/.pgpass

if [ ! -d "$pg_probackup_backup" ]; then
   pg_probackup-12 init -B $pg_probackup_backup
fi
if [ ! -d "$pg_probackup_backup/backups/$pg_probackup_instance" ]; then
   pg_probackup-12 add-instance -B $pg_probackup_backup -D $pg_probackup_data --instance $pg_probackup_instance
fi

pg_probackup-12 set-config -B $pg_probackup_backup --instance $pg_probackup_instance -U $PGUSER -d $PGDATABASE -h $PGHOST -p $PGPORT --log-level-file=info --log-filename=pg_probackup-%u.log --backup-pg-log --external-dirs=/log --compress-algorithm=zlib --compress-level=9 --retention-redundancy=$pg_probackup_redundancy --retention-window=$pg_probackup_window

cat <<EOF > $pg_probackup_backup/backups/$pg_probackup_instance/.pgpass
$PGHOST:$PGPORT:$PGDATABASE:$PGUSER:$PGPASSWORD
EOF

if [ "$show_config" = "yes" ]; then
   pg_probackup-12 show-config -B $pg_probackup_backup --instance $pg_probackup_instance
fi

if [ "$show_status" = "yes" ]; then
   pg_probackup-12 show -B $pg_probackup_backup --instance $pg_probackup_instance
fi

if [ "$backup" = "full" ]; then
   pg_probackup-12 backup -B $pg_probackup_backup --instance $pg_probackup_instance -b FULL --stream
   pg_probackup-12 show -B $pg_probackup_backup --instance $pg_probackup_instance
fi

if [ "$backup" = "delta" ]; then
   pg_probackup-12 backup -B $pg_probackup_backup --instance $pg_probackup_instance -b delta --stream
   pg_probackup-12 show -B $pg_probackup_backup --instance $pg_probackup_instance
fi
