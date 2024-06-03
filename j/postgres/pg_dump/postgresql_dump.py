#!/usr/bin/env python

import os
import time
import docker
import sys
import psycopg2
import socket

#LOG = open("/opt/postgres/scripts/log", 'a')
PG_CONT_NAME= "postgres_for_test"
PG_DB = "lighthouse_ci_db_test"
PG_USER = "lighthouse"
PG_PASSWD = "pQLNgoT6ruwvIkaWWU23"
#PG_HOST = ""
PG_PORT = "5433" or "5432"
PG_BK_PATH = "/var/lib/postgresql/backup"
HOST_BK_PATH = "/data/lhci_postgres_backup_for_test"
DUMP_DATE = time.strftime("%Y-%m-%d-%H:%M")

docker_client = docker.from_env()
# проверка, что контейнер с именем PG_CONT_NAME запущен иначе завершение скрипта
try:
    pg_cont_name = docker_client.containers.get(PG_CONT_NAME)
except:
    print(f"No such container: {PG_CONT_NAME}")
    sys.exit()
# проверка переменной PG_HOST иначе автоматическое определение ip хоста
try:
    PG_HOST
except NameError:
    h_name = socket.gethostname()
    ip_addr = socket.gethostbyname(h_name)
    PG_HOST = ip_addr
# проверка коннекта к БД по описанным данным (PG_DB,PG_USER,PG_HOST,PG_PASSWD и PG_PORT)
try:
    conn = psycopg2.connect(dbname=PG_DB,user=PG_USER,host=PG_HOST,password=PG_PASSWD,port=PG_PORT,connect_timeout=5)
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    conn.close()
except:
    print(f"No connect to DB '{PG_DB}' on host '{PG_HOST}' with port '{PG_PORT}' with user '{PG_USER}' and '***' password")
    sys.exit()
# создаем dump для PG_DB
pg_dump_cmd = f""" pg_dump -U {PG_USER} -d {PG_DB} -Z1 -Fc > {PG_BK_PATH}/{PG_DB}-{DUMP_DATE}.dump """
run_check_id = pg_cont_name.exec_run(check_id_cmd)
# удаляем dump файлы старше n-дней
for filename in sorted(os.listdir(HOST_BK_PATH))[:-14]:
    filename_path = os.path.join(HOST_BK_PATH,filename)
    filename_basename = os.path.basename(filename_path)
    if not filename_path:
        print("No dump files for delete")
    else:
        os.remove(filename_path)
        print(f"Dump file {filename_basename} was deleted")
