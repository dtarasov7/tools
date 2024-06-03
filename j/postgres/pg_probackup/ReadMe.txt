Command examples:
# pg_probackup-12 init -B /opt/postgres/pg_probackup/
# pg_probackup-12 add-instance -B /opt/postgres/pg_probackup -D /opt/postgres/data --instance test
# pg_probackup-12 backup -B /opt/postgres/pg_probackup --instance test -b FULL -j 4 --stream -U test_user -d test_db -h localhost
# pg_probackup-12 show -B /opt/postgres/pg_probackup --instance test
# pg_probackup-12 backup -B /opt/postgres/pg_probackup --instance test -b delta --stream -U test_user -d test_db -h localhost
# pg_probackup-12 set-config -B /opt/postgres/pg_probackup --instance test -U test_user -d test_db -h localhost --log-level-file=info --log-filename=pg_probackup-%u.log --backup-pg-log --external-dirs=/opt/postgres/log --compress-algorithm=zlib --compress-level=9 --retention-redundancy=2 --retention-window=2
# pg_probackup-12 backup -B /opt/postgres/pg_probackup --instance test -b delta --stream --external-dirs=/opt/postgres/log
# pg_probackup-12 merge -B /opt/postgres/pg_probackup --instance test -i ид_резервной_копии(самой последней)
# pg_probackup-12 delete -B /opt/postgres/pg_probackup --instance test --status=ERROR(с определённым состоянием)
# pg_probackup-12 show-config -B /opt/postgres/pg_probackup --instance test
# pg_probackup-12 validate -B /opt/postgres/pg_probackup --instance test -i R8XYNZ
# pg_probackup-12 restore -B /opt/postgres/pg_probackup--instance test -i R8XYNZ
# pg_probackup-12 restore -B /opt/postgres/pg_probackup --instance test --db-include=test_db
# pg_probackup-12 set-config -B /opt/postgres/pg_probackup --instance test --retention-redundancy=2 --retention-window=2
# pg_probackup-12 delete -B /opt/postgres/pg_probackup --instance test --delete-expired
# export PGPASSFILE=/opt/postgres/pg_probackup/backups/test/.pgpass
# pg_probackup-12 checkdb -B /opt/postgres/pg_probackup --instance test
