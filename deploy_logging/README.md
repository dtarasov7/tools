**Описание ролей:**

* preparatory_tasks

1. создание корневого каталога плейбука,
1. создание подкаталогов,
1. копирование скриптов быстрого запуска/остановки/рестарта.

* deploy_opensearch

1. генерация сертификатов (если generate_new_certs=true),
1. генерация es и kibana конфигов,
1. создание volumes для данных odfe,
1. создание каталога для снапшотов,
1. деплой docker-compose.yaml,
1. логин и логофф в docker registry (если имеется внутреннее хранилище образов), (TODO)
1. старт/стоп контейнеров (dc=up/down),
1. запуск securityadmin.sh для приминения новых конфигураций,
1. создание репозитория для снапшотов, деплой скрипта для cron и добавление выполнение скрипта в cron,
1. деплой конфига для curator и добавление выполнение скрипта в cron.

* rolling_restart (node by node)

1. check and enable shard allocation for the cluster,
1. disable shard allocation for the cluster,
1. stop indexing new data and perform a synced flush,
1. stop/start node and wait status,
1. enable shard allocation for the cluster.

* deploy_logstash

1. копирование pipelines,
1. генерация конфигов,
1. деплой docker-compose.yaml,
1. получение сертификата с ODFE,
1. старт контейнеров.

* deploy_filebeat

1. генерация конфигов,
1. деплой docker-compose.yaml,
1. старт контейнеров.

**Запуск деплоя:**

Запуск из каталога /opt/deploy_opensearch на хосте ansible. На примере, среды - _prod_dtln_ с hosts-файлом - _prod-hosts_.

Развертывание всего стека - первичная установка кластера ODFE (генерация сертификатов, если certificates=new), Logstash и Filebeat:

`# ansible-playbook install_opensearch.yml -i inventories/prod_dtln/prod-hosts`

Развертывание (ТОЛЬКО первичная установка) кластера ODFE (генерация сертификатов, если certificates=new):

`# ansible-playbook install_opendistro.yml -i inventories/prod_dtln/prod-hosts` -t "preparatory_tasks,deploy_opendistro"

Наверное не нужно в случае с докерами - Реконфигурация/рестарт ODFE (генерация сертификатов, если certificates=new) - каждая нода по очереди:

`# ansible-playbook reconfig_odfe_cluster.yml -i inventories/prod_dtln/prod-hosts`

Развертывание(dc=up)/внесение изменений(dc=restart) Logstash:

`# ansible-playbook install_logstash.yml -i inventories/prod_dtln/prod-hosts`

Развертывание/внесение изменений Filebeat:

`# ansible-playbook install_filebeat.yml -i inventories/prod_dtln/prod-hosts`

Деплой экшенов (удаление старых снапшотов и индексов), запускается с одного хоста:

`# ansible-playbook deploy_actions.yml -i inventories/prod_dtln/hosts -l <host>`

**Полезные команды:**
```
# curl -XGET https://localhost:9200/_cat/nodes?v -u 'admin:admin_passwd' --insecure - список нод
# curl -k https://localhost:9200/_cluster/health?pretty=true -u 'admin:admin_passwd' - проверить статус
# curl -XGET -k https://localhost:9200/_cat/master -u 'admin:admin_passwd' - посмотреть кто мастер
# curl -XGET -k https://localhost:9200/_cluster/allocation/explain?pretty -u admin:admin_passwd' - Provides an explanation for a shard’s current allocation.


```
Через Dev Tools в интерфейсе Kibana:

```
GET _cat/shards?s=state

GET _cat/indices?v

GET _cluster/health

GET _opendistro/_security/api/internalusers/

DELETE /my-index-000001

GET /_cat/repositories

GET /_cat/snapshots/repo_name
```


**Полезные информация:**

"After changing any of the configuration files in plugins/opendistro_security/securityconfig, however, you must run plugins/opendistro_security/tools/securityadmin.sh to load these new settings into the index. You must also run this script at least once to initialize the .opendistro_security index and configure your authentication and authorization methods."
