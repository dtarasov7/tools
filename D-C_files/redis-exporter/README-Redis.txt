Источник: https://hub.docker.com/r/oliver006/redis_exporter

1) Пример docker-compose.yml файла с запуском контейнера:

version: '3'

services:
  redis_exporter:
    image: oliver006/redis_exporter:v1.35.1
    container_name: redis_exporter
    hostname: $HOSTNAME
    ports:
      - ${REDIS_EXP_PORT:-9121}:9121
    restart: unless-stopped
    command:
      - '--include-system-metrics'
      - '--ping-on-connect'
      - '--redis-only-metrics'
      - '--redis.addr=redis://${REDIS_HOST}:${REDIS_PORT:-6379}'
#      - '--redis.user=${REDIS_USER}'
#      - '--redis.password=${REDIS_PASSWORD}'
    labels:
      app: "victoriametrics"
      product_id: "vm-redisexporter"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "product_id"

2) Что бы поставить экспортер на мониторинг в Викторию-метрикс необходимо в файл vmagent/prometheus.yml 
   добавить (если отсутствует) следующий job  с именем 'redis-exporter':

  - job_name: 'redis-exporter'
    scrape_interval: 60s
    honor_labels: true
    file_sd_configs:
      - files:
        - '/etc/prometheus/sd/sd_adl_redis/*.yml'

3) Добавить файл с расширением ".yml" с таргетами в каталог vmagent/sd/sd_adl_redis/ с содержимым:

- targets: ['<ip_хоста_экспортера>:9121']
  labels:
    host: <hostname_хоста_экспортера>
    owner: adl
    env:  <указать_среду>

Можно добавить другие labels (метки), в зависимости от имеющейся потребности в фильтрации метрик

Если порт с дефолтного "9121" менялся на иной, то учесть эти изменения.

4) Если в redis включена авторизация, то надо указать учетную запись, обладающую как минимум следующими правами

(это пример - пользователь prometheus , пароль Wdc555#Wdc#)

user prometheus +client +ping +info +config|get +cluster|info +slowlog +latency +memory +select +get +scan +xinfo +type +pfcount +strlen +llen +scard +zcard +hlen +xlen +eval allkeys on >Wdc555#Wdc#

