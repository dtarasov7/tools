Файл описывающий объект мониторинга для blackbox экспортера

файл должен находится по пути
/opt/VMCluster_deploy_ADL/vmagent/sd/sd_adl_blackbox/

И имя должно соответствовать шаблону:

- 2xx*.yml  - http или https запрос и ожидание кода 200-299
- 401*.yml  - http или https запрос и ожидание кода 401
- tcp*.yml  - установдление tcp соединения
- icmp*.yml  - ping


Cодержимое файла:

2xx*.yml  

- targets: ['<http|https>://<IP_adress_сервера>:<порт_сервера>/<путь>']
  labels:
    host: <имя_сервера>
    application: <имя_сервера>
    owner: adl
    env: <окружение>

Пример:
- targets: ['https://10.80:5601/app/login?nextUrl=%2F']
  labels:
    host: prod-odfe01
    application: kibana
    owner: ctp
    env: dtln-prod



tcp*.yml

Пример tcp:
- targets: ['10.80:5601']
  labels:
    host: prod-odfe01
    application: kibana
    owner: ctp
    env: dtln-prod



icmp*.yml

Пример icmp:
- targets: ['10.80']
  labels:
    host: prod-odfe01
    owner: ctp
    env: dtln-prod
