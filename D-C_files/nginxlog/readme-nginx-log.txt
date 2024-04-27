Файл описывающий объект мониторинга для nginxlog экспортера

файл должен находится по пути
/opt/VMCluster_deploy_ADL/vmagent/sd/sd_adl_common

И имя должно соответсвовать шаблону 

nginxlog*.yml

содержимое файла

- targets: ['<IP_adress_сервера_с_экспортером>:<порт_экспортера>']
  labels:
    host: <имя_сервера>
    owner: adl
    env: <окружение>

Пример:
- targets: ['192.168.109.31:4040']
  labels:
    host: elasticsearch1
    owner: adl
    env: dtln-preprod

Конфигурационный файл экспортера настроен на стандартный (combined) формат access лога nginx
При использовании измененного формата access лог файла - необходимо внести коррективы в файл конфига экспортера
