#!/usr/bin/env python

import os
import time
import docker
import sys
import psycopg2
import socket
import glob
import shutil

#LOG = open("/opt/postgres/scripts/log", 'a')
PG_CONT_NAME= "postgres"
PG_DB = "grafana"
PG_USER = "grafana"
PG_PASSWD = "M78IwbNOILny9d6BL6yA"
#PG_HOST = ""
PG_PORT = "" or "5432"
PG_BK_PATH = "/var/lib/postgresql/backup"
HOST_BK_PATH = "/opt/ans_VMCluster_deploy/postgres/backup"
DUMP_STORAGE = "/opt/nfs-client/scripts/dtln-prod/grafana/backups"
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
# проверка наличия каталога для хранения dump файлов
if not os.path.exists(DUMP_STORAGE):
    print (f"'{DUMP_STORAGE}' not exist")
    sys.exit()
# создаем dump для PG_DB
pg_dump_cmd = f""" /bin/bash -c 'pg_dump "host=localhost port={PG_PORT} dbname={PG_DB} user={PG_USER} password={PG_PASSWD}" > {PG_BK_PATH}/{PG_DB}-{DUMP_DATE}.dump' """
run_pg_dump_cmd = pg_cont_name.exec_run(pg_dump_cmd)
# копируем dump файл в каталог для хранения
for dump_file in glob.glob(os.path.join(HOST_BK_PATH, '*.dump')):
    shutil.move(dump_file, DUMP_STORAGE)
# удаляем dump файлы старше n-дней
for filename in sorted(glob.glob(os.path.join(f'{DUMP_STORAGE}/*.dump')))[:-14]:
    filename_path = os.path.join(filename)
    filename_basename = os.path.basename(filename_path)
    if not filename_path:
        print("No dump files for delete")
    else:
        os.remove(filename_path)
        print(f"Dump file {filename_basename} deleted")

####### restore steps
## psql template1 -U postgres -c 'drop database grafana;'
# Password for user postgres:
## psql template1 -U postgres -c 'create database grafana with owner grafana;'
# Password for user postgres:
## psql -U postgres grafana < grafana-******.dump
# Password for user postgres:
