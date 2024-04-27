Файл описывающий объект мониторинга для elasticsearch экспортера

файл должен находится по пути
/opt/VMCluster_deploy_ADL/vmagent/sd/sd_adl_common

И имя должно соответсвовать шаблону 

elasticsearch*.yml

содержимое файла

- targets: ['<IP_adress_сервера_с_экспортером>:<порт_экспортера>']
  labels:
    host: <имя_сервера>
    owner: adl
    env: <окружение>

Пример:
- targets: ['192.168.109.31:9114']
  labels:
    host: elasticsearch1
    owner: adl
    env: dtln-preprod

