Источник: https://github.com/weaponry/pgscv

1) Для начала необходимо включить плагин "pg_stat_statements". Логинимся в БД под postgres пользователем (-U postgres) и включаем плагин:
# CREATE EXTENSION  IF NOT EXISTS pg_stat_statements;
Проверка:
# SELECT * FROM pg_available_extensions WHERE name = 'pg_stat_statements' and installed_version is not null;

2) Так же надо убедиться в наличии прав для пользователя под которым экспортер будет коннектиться к БД.Например, можно создать пользователя "pgscv" и предоставить ему соответствующие права описанные по ссылке https://github.com/weaponry/pgscv/wiki/Security-considerations


3) Пример docker-compose.yml файла с запуском контейнера:

version: '3'

services:
  postgres_exporter:
    image: weaponry/pgscv/0.7.5
    hostname: $HOSTNAME
    container_name: pgscv
    ports:
      - 9890:9890
    environment:
      - PGSCV_LISTEN_ADDRESS=0.0.0.0:9890
      - PGSCV_DISABLE_COLLECTORS=system,postgres/settings
      - POSTGRES_DSN_POSTGRES=postgresql://user:password@10.10.10.10:5432/test?sslmode=disable
# для каждого инстанса своя строка с данными
#      - POSTGRES_DSN_<NAME>=postgresql://<PG_USER>:<PG_PASSWORD>@<PG_HOST>:<PG_PORT>/<DB_NAME>?sslmode=disable
    restart: unless-stopped
    labels:
      app: "victoriametrics"
      product_id: "vm-postgresexporter"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "product_id"

3) Что бы поставить экспортер на мониторинг в Викторию-метрикс необходимо в файл vmagent/prometheus.yml добавить следующий job, например, с именем 'postgres-exporter', перед этим создать каталог "sd_adl_postgres-exporter" в директории vmagent/sd/:

  - job_name: 'postgres-exporter'
    scrape_interval: 15s
    scrape_timeout: 15s
    file_sd_configs:
      - files:
        - '/etc/prometheus/sd/sd_adl_postgres-exporter/*.yml'

4) Добавить файл с таргетами в каталог vmagent/sd/sd_adl_postgres-exporter/название_файла.yml с содержимым:

- targets: ['<ip_хоста_экспортера>:9890']
  labels:
    host: <hostname_хоста_экспортера>
    owner: adl
    env:  dtln-preprod
