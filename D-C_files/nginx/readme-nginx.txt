Файл описывающий объект мониторинга для nginx экспортера

файл должен находится по пути
/opt/VMCluster_deploy_ADL/vmagent/sd/sd_adl_common

И имя должно соответствовать шаблону 

nginxexporter*.yml

содержимое файла: 

- targets: ['<IP_adress_сервера_с_экспортером>:<порт_экспортера>']
  labels:
    host: <имя_сервера>
    owner: adl
    env: <окружение>

Пример:
- targets: ['192.168.109.31:9113']
  labels:
    host: nginx1
    owner: adl
    env: dtln-prod


В конфигурации nginx должен былть определен location /status с директоивой "stub_status on;" в секции Server которая слушает порт 8080
Если порт и localtion  другой, то нреобходимо внести соответсвующие коррективы в docker-compose файл