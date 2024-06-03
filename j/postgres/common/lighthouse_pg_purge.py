#!/usr/bin/env python

import os
import time
import docker
import sys
import psycopg2
import socket

LOG = open("/opt/postgres/scripts/log", 'a')
PG_CONT_NAME= "postgres"
PG_DB = "lighthouse_ci_db"
PG_USER = "lighthousee"
PG_PASSWD = "v638jY0wAkC42NpdhP3W"
#PG_HOST = ""
PG_PORT = "15432" or "5432"
IDS = ["6ddb1c54-5b0a-467d-83a2-3350c5431a31", "b424ddae-2905-455b-8def-f48fd93f19f9"]
START_SCRIPT = time.strftime("%Y-%m-%d %H:%M")

docker_client = docker.from_env()
# проверка, что контейнер с именем PG_CONT_NAME запущен иначе завершение скрипта
try:
    pg_cont_name = docker_client.containers.get(PG_CONT_NAME)
except:
    print(f"No such container: {PG_CONT_NAME}")
    LOG.write(f"= {START_SCRIPT} No such container: {PG_CONT_NAME}\n")
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
    LOG.write(f"= {START_SCRIPT} No connect to DB '{PG_DB}' on host '{PG_HOST}' with port '{PG_PORT}' with user '{PG_USER}' and '***' password\n")
    sys.exit()
# определяем все имеющиеся id что бы потом проверить указанный список IDS на достоверность
check_id_cmd = f""" psql -U {PG_USER} -d {PG_DB} -t -c 'SELECT id FROM projects;' """
run_check_id = pg_cont_name.exec_run(check_id_cmd)
check_id_exist = run_check_id.output.decode().rstrip().replace(" ", "")
#print(check_id_exist)
# пишем в лог время старта
print(f"= Start script: {START_SCRIPT} =")
LOG.write(f"= Start script: {START_SCRIPT} =\n")
for build_id in IDS:
# проверяем существует ли id указанный в IDS
    if build_id in check_id_exist:
# соотносим id с именем проекта
        build_name_cmd = f""" psql -U {PG_USER} -d {PG_DB} -t -c "SELECT name FROM projects WHERE "id" = '{build_id}';" """
        run_build_name = pg_cont_name.exec_run(build_name_cmd)
        project_name = run_build_name.output.decode().rstrip().replace(" ", "")
#        print(project_name)
        print(f"# Project name {project_name} with id '{build_id}' exist")
        LOG.write(f"# Project name '{project_name}' with id '{build_id}' exist\n")
# подсчитываем кол-во доступных для удаления билдов
        count_ids_cmd = f""" psql -U {PG_USER} -d {PG_DB} -t -c "create local temp view delete_ids AS (SELECT id FROM builds where (("\'"createdAt"\'" < now() - interval '7 day' and extract(hour from "\'"createdAt"\'") != 14 and extract(hour from "\'"createdAt"\'") != 15) or "\'"createdAt"\'" < now() - interval '30 day') and "\'"projectId"\'" = '{build_id}'); SELECT count(*) AS exact_count FROM delete_ids" """
        run_count_ids_cmd = pg_cont_name.exec_run(count_ids_cmd)
        count_ids = run_count_ids_cmd.output.decode().rstrip().replace(" ", "")
#        print(count_ids)
# если кол-во билдов равно 0 - ничего не удаляем, иначе удаляем
        if count_ids == 0:
            print(f"# No data to delete")
            LOG.write(f"# No data to delete\n")
        else:
            print(f"# {count_ids} builds will be deleting...")
            LOG.write(f"# {count_ids} builds will be deleting...\n")
            delete_ids_cmd = f""" psql -U {PG_USER} -d {PG_DB} -t -c "create local temp view delete_ids AS (SELECT id FROM builds where (("\'"createdAt"\'" < now() - interval '7 day' and extract(hour from "\'"createdAt"\'") != 14 and extract(hour from "\'"createdAt"\'") != 15) or "\'"createdAt"\'" < now() - interval '30 day') and "\'"projectId"\'" = '{build_id}'); DELETE FROM runs r WHERE exists(select 1 from delete_ids where id = r."\'"buildId"\'"); DELETE FROM statistics s WHERE exists(select 1 from delete_ids where id = s."\'"buildId"\'"); DELETE FROM builds b WHERE exists(select 1 from delete_ids where id = b."\'"id"\'");" """
            run_delete_ids_cmd = pg_cont_name.exec_run(delete_ids_cmd)
# если id указанный в IDS не существует
    else:
        print(f"# Project ID {build_id} doesn't exist")
        LOG.write(f"# Project ID {build_id} doesn't exist\n")
# пишем в лог время завершения
STOP_SCRIPT = time.strftime("%Y-%m-%d %H:%M")
print(f"= Stop script: {STOP_SCRIPT} =")
LOG.write(f"= Stop script: {STOP_SCRIPT} =\n")
