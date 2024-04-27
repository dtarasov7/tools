Источник: https://hub.docker.com/r/kbudde/rabbitmq-exporter

1) Пример docker-compose.yml файла с запуском контейнера:

version: '3'

services:
  rabbitmq_exporter:
    image: kbudde/rabbitmq-exporter:1.0.0-RC13
    container_name: rabbitmq_exporter
    hostname: $HOSTNAME
    ports:
      - 9419:9419
    environment:
      - RABBIT_URL=${RABBIT_URL}
      - RABBIT_USER=${RABBIT_USER}
      - RABBIT_PASSWORD=${RABBIT_PASSWORD}
    restart: unless-stopped
    labels:
      app: "victoriametrics"
      product_id: "vm-rabbitmqexporter"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "product_id"

2) Из документации следует, что у указанного пользователя "RABBIT_USER" должен быть "User needs monitoring tag!"
По данной ссылке есть необходимые шаги по добавлению данного тэга:
https://stackoverflow.com/questions/52010390/permissions-that-need-to-be-assigned-for-a-rabbitmq-monitoring-user

3) Что бы поставить экспортер на мониторинг в Викторию-метрикс необходимо в файл vmagent/prometheus.yml 
   добавить (если отсутствует) следующий job, с именем 'rabbitmq-exporter':

  - job_name: 'rabbitmq-exporter'
    scrape_interval: 60s
    honor_labels: true
    file_sd_configs:
      - files:
        - '/etc/prometheus/sd/sd_adl_rabbitmq/*.yml'

4) Добавить файл с расширением ".yml" с таргетами в каталог vmagent/sd/sd_adl_rabbitmq/ с содержимым:

- targets: ['<ip_хоста_экспортера>:9419']
  labels:
    host: <hostname_хоста_экспортера>
    owner: adl
    env:  <указать_среду>

Можно добавить другие labels(метки), в зависимости от имеющейся потребности в фильтрации метрик

Если порт с дефолтного "9419" менялся на иной, то учесть эти изменения.
