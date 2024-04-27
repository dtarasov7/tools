Источник: https://github.com/prometheus/mysqld_exporter

1) Пример docker-compose.yml файла с запуском контейнера Percona и экспортера для msql. Если сервис msql уже имеется, то создаем сначало пользователя командами из п. 2 и после запустить контейнер с экспортером.

version: '3'

volumes:
    percona_data: {}


services:
  percona:
    image: percona:ps-5.7
    container_name: percona
    hostname: ${HOSTNAME}
    ports:
      - 3306:3306
    volumes:
      - percona_data:/var/lib/mysql
#    command:
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password1
      - MYSQL_DATABASE=test_db
      - MYSQL_ROOT_HOST=10.80
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "product_id"
    labels:
      app: "victoriametrics"
      product_id: "vm-mysql"

  mysqld-exporter:
    image: prom/mysqld-exporter:v0.13.0
    container_name: mysqld-exporter
    hostname: ${HOSTNAME}
    ports:
      - 9104:9104
#    volumes:
    command:
#      - '--config.my-cnf=/usr/local/etc/.mysqld_exporter.cnf'
      - '--collect.global_status'
      - '--collect.info_schema.innodb_metrics'
      - '--collect.auto_increment.columns'
      - '--collect.info_schema.processlist'
      - '--collect.binlog_size'
      - '--collect.info_schema.tablestats'
      - '--collect.global_variables'
      - '--collect.info_schema.query_response_time'
      - '--collect.info_schema.userstats'
      - '--collect.info_schema.tables'
      - '--collect.perf_schema.tablelocks'
      - '--collect.perf_schema.file_events'
      - '--collect.perf_schema.eventswaits'
      - '--collect.perf_schema.indexiowaits'
      - '--collect.perf_schema.tableiowaits'
      - '--collect.slave_status'
    environment:
      - DATA_SOURCE_NAME=prom:superpass@(percona_ip:3306)/test_db
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "product_id"
    labels:
      app: "victoriametrics"
      product_id: "vm-mysqlexp"

2) После запуска необходимо создать пользователя, например, <prom> с паролем <superpass> под которым экспортер будет собирать метрики и наделить его привилегиями. Зайти в консоль msql с правами супер пользователя и выполнить:

CREATE USER 'prom' IDENTIFIED BY 'superpass' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'prom';

Перезапустить контйнер с экспортером и проверить логи контейнера на отсутствие ошибок.

3) Что бы поставить экспортер на мониторинг в Викторию-метрикс необходимо в файл vmagent/prometheus.yml добавить следующий job, например, с именем 'percona':

  - job_name: 'percona'
    scrape_interval: 15s
    scrape_timeout: 5s
    file_sd_configs:
      - files:
        - '/etc/prometheus/sd/sd_adl_mysqlexporter/*.yml'
		
4) Добавить файл с таргетами в каталог vmagent/sd/sd_adl_mysqlexporter/название_файла.yml с содержимым:

- targets: ['<ip_хоста_экспортера>:9104']
  labels:
    host: <hostname_хоста_экспортера>
    owner: adl
    env:  dtln-preprod
