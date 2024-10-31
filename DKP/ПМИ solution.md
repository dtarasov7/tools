# ПМИ ЕЕ - команды для прохождения

Файл с прохождением ПМИ можно передавать Клиентам

## 1. Возможность установки платформы в закрытом контуре

Следуем согласно Быстрому старту

## 2. Автоматическое обновление платформы Deckhouse

Установить платформу версии меньше на 1 в миноре необходимого релизного канала и убедиться, что платформа автоматически обновится до актуальной версии (механизм обновления **Automatic**)

Идём на https://releases.deckhouse.ru/ee, для канала Stable у нас сейчас указано `1.58.10`, соответственно нам требуется установить версию Deckhouse `1.57.x` (последней патч-версии)

Получить список патч-версий релиза

```
curl -L -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/deckhouse/deckhouse/tags?per_page=100 -s | jq -r '.[].name' | sort | grep 'v1.57'
```

Пример вывода
```
~ $ curl -L -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/deckhouse/deckhouse/tags?per_page=100 -s | jq -r '.[].name' | sort | grep 'v1.57'
v1.57.0
v1.57.1
v1.57.2
v1.57.3
v1.57.4
v1.57.5
v1.57.6
```

Установить Deckhouse используя последнюю патч-версию

Пример команды запуска установщика
```
docker run --pull=always -it -v "$PWD/config.yml:/config.yml" -v "$HOME/.ssh/:/tmp/.ssh/" -v "$PWD/resources.yml:/resources.yml" -v "$PWD/dhctl-tmp:/tmp/dhctl" registry.deckhouse.ru/deckhouse/ee/install:v1.57.6 bash
```

После установки убедиться, что Deckhouse обновился до необходимого релиза (в нашем случае до `v1.58.10` c канала Stable) - релиз должен быть в статусе `Deployed`

```
kubectl get deckhousereleases.deckhouse.io
NAME      PHASE      TRANSITIONTIME   MESSAGE
v1.58.10   Deployed   2d2h
```

На обновление может потребоваться время, в том числе если релиз стоит в [Pending](https://deckhouse.ru/documentation/v1/modules/002-deckhouse/#%D0%BE%D0%B1%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D1%80%D0%B5%D0%BB%D0%B8%D0%B7%D0%BE%D0%B2-deckhouse) ожидании, протолкнуть его можно командой

```
kubectl annotate deckhousereleases v1.57.6 release.deckhouse.io/apply-now="true"
```

## 3. Возможность ручного обновления платформы Deckhouse

Провести аналогично пункту "Автоматическое обновление платформы Deckhouse", но с первоначально [заданным режимом обновления в Manual](https://deckhouse.ru/documentation/v1/modules/002-deckhouse/usage.html#%D1%80%D1%83%D1%87%D0%BD%D0%BE%D0%B5-%D0%BF%D0%BE%D0%B4%D1%82%D0%B2%D0%B5%D1%80%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BE%D0%B1%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B9)

В config.yml устанавливаемого кластера указать

```
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: deckhouse
spec:
  version: 1
  settings:
    releaseChannel: Stable
    update:
      mode: Manual
```

Либо в существующем кластере задать ручной режим обновления и переключить на другой releaseChannel (например с Stable на EarlyAccess)

После проверить, что в появился свежий релиз ожидающий подтверждения

```
~ $ kubectl get deckhousereleases.deckhouse.io
NAME       PHASE      TRANSITIONTIME   MESSAGE
v1.58.10   Deployed   106s
v1.59.8    Pending    1s               Waiting for manual approval
```

Подтвердить его можно с помощью команды

```
kubectl patch DeckhouseRelease v1.59.8 --type=merge -p='{"approved": true}'
```

Поcле подтверждения убедиться, что необходимый релиз перешёл в состояние `Deployed`

```
~ $ kubectl get deckhousereleases.deckhouse.io
NAME       PHASE        TRANSITIONTIME   MESSAGE
v1.58.10   Superseded   2s
v1.59.8    Deployed     2s
```

И сменился Image у пода Deckhouse

```
~ $ kubectl -n d8-system get deployment deckhouse -o yaml | grep image
        image: registry.deckhouse.ru/deckhouse/ee:v1.59.8 <-------- Необходимый image
        imagePullPolicy: Always
        image: registry.deckhouse.ru/deckhouse/ee@sha256:9e39972534549245803c003b4423cc745297af43affc2bbc4dd3c4da225e46e5
        imagePullPolicy: IfNotPresent
      imagePullSecrets:
        image: registry.deckhouse.ru/deckhouse/ee@sha256:79ed551f4d0ec60799a9bd67f35441df6d86443515dd8337284fb68d97a01b3d
        imagePullPolicy: Always
```

## 4. Поддержка РФ операционных систем (РЕДОС, ALT linux, Astra Linux)

Добавить worker в NodeGroup worker с Static инстансами

Получить скрипт

```
kubectl -n d8-cloud-instance-manager get secrets manual-bootstrap-for-worker-static -o json | jq -r '.data."bootstrap.sh"'
```

Выполнить на подключаемом узле

```
echo BASE64_SCRIPT | base64 -d | sudo bash
```

Дождаться завершения bootstrap-процесса узла и проверить наличие узла в выводе

```
kubectl get nodes -o wide
```

Пример вывода
```
~ $ kubectl get nodes -o wide
NAME                                        STATUS   ROLES                  AGE     VERSION    INTERNAL-IP    EXTERNAL-IP     OS-IMAGE                         KERNEL-VERSION       CONTAINER-RUNTIME
static-0                           Ready    worker-static          5h22m   v1.25.16   10.241.32.27   <none>          Debian GNU/Linux 11 (bullseye)   5.10.0-19-amd64      containerd://1.7.13
test-master-0                      Ready    control-plane,master   16h     v1.25.16   10.241.32.10   84.201.158.17   Ubuntu 22.04.4 LTS               5.15.0-105-generic   containerd://1.7.13
test-worker-7c379976-68579-drhkp   Ready    worker                 16h     v1.25.16   10.241.32.15   <none>          Ubuntu 22.04.4 LTS               5.15.0-105-generic   containerd://1.7.13
rf-worker                                   Ready    worker-static          34s     v1.25.16   10.241.32.30   <none>          Astra Linux                      6.1.50-1-generic     containerd://1.7.13
```

Видим в OS Image Astra Linux

Посмотреть, какие поды запущены на данной ноде можно с помощью конструкции

```
kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=NODE_NAME
```

Пример
```
~ $ kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=rf-worker
NAMESPACE                   NAME                             READY   STATUS    RESTARTS        AGE     IP             NODE        NOMINATED NODE   READINESS GATES
d8-chrony                   chrony-ztcfn                     1/1     Running   0               2m35s   10.241.32.30   rf-worker   <none>           <none>
d8-cloud-instance-manager   early-oom-c4s8v                  2/2     Running   0               2m35s   10.111.6.2     rf-worker   <none>           <none>
d8-cni-simple-bridge        simple-bridge-7r26z              1/1     Running   1 (2m46s ago)   3m6s    10.241.32.30   rf-worker   <none>           <none>
d8-monitoring               ebpf-exporter-wmcmv              2/2     Running   0               2m35s   10.241.32.30   rf-worker   <none>           <none>
d8-monitoring               monitoring-ping-564bc            1/1     Running   0               3m4s    10.241.32.30   rf-worker   <none>           <none>
d8-monitoring               node-exporter-js9tl              3/3     Running   0               3m5s    10.241.32.30   rf-worker   <none>           <none>
d8-upmeter                  smoke-mini-a-0                   1/1     Running   0               2m30s   10.111.6.3     rf-worker   <none>           <none>
d8-upmeter                  smoke-mini-e-0                   1/1     Running   0               72s     10.111.6.4     rf-worker   <none>           <none>
kube-system                 d8-kube-proxy-mbd24              2/2     Running   0               3m6s    10.241.32.30   rf-worker   <none>           <none>
kube-system                 kubernetes-api-proxy-rf-worker   2/2     Running   0               2m9s    10.241.32.30   rf-worker   <none>           <none>
kube-system                 node-local-dns-zbkkm             3/3     Running   0               2m35s   10.241.32.30   rf-worker   <none>           <none>
```

## 5. Обновление версии Kubernetes

Проверить версию можно с помощью команды

```
~ $ kubelet --version
Kubernetes v1.25.16
```

После установки кластера сменить версию путём редактирования ClusterConfiguration

```
# До версии Deckhouse v1.59
kubectl -n d8-system exec -ti deployments/deckhouse -c deckhouse -- deckhouse-controller edit cluster-configuration

# После версии Deckhouse v1.59 и при мульти-мастере
kubectl -n d8-system exec -it $(kubectl -n d8-system get leases.coordination.k8s.io deckhouse-leader-election -o jsonpath='{.spec.holderIdentity}' | awk -F'.' '{ print $1 }') -c deckhouse -- deckhouse-controller edit cluster-configuration
```

После изменения версии запуститься процесс обновления, который можно отслеживать изменением версии в описании нод

Пример вывода (производится переключение с Automatic версии `v1.25` на `v1.26`)

```
~ $ kubectl get nodes
NAME                                        STATUS   ROLES                  AGE    VERSION
my-cluster-master-0                      Ready    control-plane,master   2d4h   v1.25.16
my-cluster-worker-3c009883-57f96-mlp4g   Ready    worker                 2d4h   v1.25.16

~ $ kubectl -n d8-system exec -ti deployments/deckhouse -c deckhouse -- deckhouse-controller edit cluster-configuration
Connect to Kubernetes API
Get Kubernetes API client
INFO[0000] Kubernetes client is configured successfully with 'out-of-cluster' config  operator.component=KubernetesAPIClient
Succeeded!

Get Kubernetes API client
Waiting for Kubernetes API to become Ready
Succeeded!

Waiting for Kubernetes API to become Ready
Connect to Kubernetes API
Save cluster-configuration back to the Kubernetes cluster
Configurations are equal. Nothing to update.
Save cluster-configuration back to the Kubernetes cluster

~ $ kubectl get nodes
NAME                                        STATUS   ROLES                  AGE    VERSION
test-master-0                      Ready    control-plane,master   2d4h   v1.26.15
test-worker-3c009883-57f96-mlp4g   Ready    worker                 2d4h   v1.26.15
```

Для двух нод процесс занял около 5 минут

## 6. Возможность увеличения количества control-plane узлов

Провести добавление узлов согласно документации

Для Bare-Metal через применение скрипта из секрета

1. Получить скрипт в формате base64 на мастер-узле

```
kubectl -n d8-cloud-instance-manager get secrets manual-bootstrap-for-master -o json | jq -r '.data."bootstrap.sh"'
```

2. Выполнить скрипт на подключаемом узле

```
echo BASE64_SCRIPT | base64 -d | sudo bash
```

Для Cloud-провайдеров произвести увеличение мастер узлов через увеличение количества реплик masterNodeGroup в соответствии с используемым провайдером

Убедиться в количестве узлов через `kubectl get nodes`

Также проверить количество членов etcd кластера с помощью скрипта

```
#!/bin/bash
etcd=`kubectl -n kube-system get pod -l component=etcd,tier=control-plane -o json | jq -r '.items[] | select( .status.conditions[] | select(.type == "ContainersReady" and .status == "True")) | .metadata.name' | head -n1`
cmd="kubectl -n kube-system exec --stdin --tty $etcd -- etcdctl --cacert /etc/kubernetes/pki/etcd/ca.crt --cert /etc/kubernetes/pki/etcd/ca.crt --key /etc/kubernetes/pki/etcd/ca.key --endpoints"
endpoints=`eval "$cmd https://127.0.0.1:2379/ member list -w table | grep https | awk -v ORS=\",\" '{print \\\$10 }' | sed 's/,$//'"`
eval "$cmd $endpoints member list -w table"
eval "$cmd $endpoints endpoint status -w table"
```

Пример вывода ( при увеличении с 1 до 3 мастеров)

```
~ $ bash etcd.sh
+------------------+---------+------------------------+---------------------------+---------------------------+------------+
|        ID        | STATUS  |          NAME          |        PEER ADDRS         |       CLIENT ADDRS        | IS LEARNER |
+------------------+---------+------------------------+---------------------------+---------------------------+------------+
| 46e6db2c59113584 | started | mcluster-test-master-0 | https://10.241.32.10:2380 | https://10.241.32.10:2379 |      false |
| 95803e07877f9fe9 | started | mcluster-test-master-2 | https://10.241.40.31:2380 | https://10.241.40.31:2379 |      false |
| c699beba4de3e238 | started | mcluster-test-master-1 |  https://10.241.36.4:2380 |  https://10.241.36.4:2379 |      false |
+------------------+---------+------------------------+---------------------------+---------------------------+------------+
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
| https://10.241.32.10:2379 | 46e6db2c59113584 |   3.5.9 |  113 MB |      true |      false |         7 |     769449 |             769449 |        |
| https://10.241.40.31:2379 | 95803e07877f9fe9 |   3.5.9 |  112 MB |     false |      false |         7 |     769450 |             769450 |        |
|  https://10.241.36.4:2379 | c699beba4de3e238 |   3.5.9 |  113 MB |     false |      false |         7 |     769450 |             769450 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```

## 7. Управление узлами кластера (добавление, удаление)

Добавление с помощью [CAPS](https://deckhouse.ru/documentation/latest/modules/040-node-manager/examples.html#%D1%81-%D0%BF%D0%BE%D0%BC%D0%BE%D1%89%D1%8C%D1%8E-cluster-api-provider-static)

После добавления проверить, что нода появилась и перешла в статус Ready

Отключить ноду

```
kubectl label staticinstances.deckhouse.io NAME_OF_STATIC_INSTANCE node.deckhouse.io/allow-bootstrap=false --overwrite=true
```

Если узел был добавлен в ручную с помощью скрипта, то произвести его отключение следующим образом

Удалите узел из кластера Kubernetes:

```
kubectl drain <node> --ignore-daemonsets --delete-local-data
kubectl delete node <node>
```

Запустите на узле скрипт очистки:

```
bash /var/lib/bashible/cleanup_static_node.sh --yes-i-am-sane-and-i-understand-what-i-am-doing
```

## 8. Автоматическая настройка узлов кластера

Применить ресурс NodeGroupConfiguration и проверить работу systemd сервиса bashbile на узле кластера - убедиться, что параметр на узле кластера изменился на необходимое значение

Получаем текущее значение на узле

```
sysctl vm.max_map_count
```

Пример вывода

```
~ $ sysctl vm.max_map_count
vm.max_map_count = 65530
```

Применяем NodeGroupConfiguration

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: NodeGroupConfiguration
metadata:
  name: sysctl-tune.sh
spec:
  weight: 100
  bundles:
  - "*"
  nodeGroups:
  - "*"
  content: |
    sysctl -w vm.max_map_count=262144
EOF
```

Дожидаемся перехода всех NG в UpToDate состояние

```
~ $ k get ng
NAME     TYPE             READY   NODES   UPTODATE   INSTANCES   DESIRED   MIN   MAX   STANDBY   STATUS   AGE    SYNCED
master   CloudPermanent   1       1       1                                                               2d6h   True
worker   CloudEphemeral   1       1       1          1           1         1     1                        2d6h   True
```

Проверяем

```
~ $ sysctl vm.max_map_count
vm.max_map_count = 262144
```

## 9. Возможность дополнительной конфигурации runtime-компонентов узлов кластера

Произвести корректировку параметра kubelet maxPods (сменить с значения по умолчанию 110 на 150)

```
kubectl patch ng worker --type=merge -p='{"spec":{"kubelet":{"maxPods": 150}}}'
```

Проверить изменение на узле группы

```
cat /var/lib/kubelet/config.yaml | grep maxPods
```

Пример
```
~# cat /var/lib/kubelet/config.yaml | grep maxPods
maxPods: 110
# После выполнения сервиса bashible
~# cat /var/lib/kubelet/config.yaml | grep maxPods
maxPods: 150
```

## 10. Размещение компонентов Deckhouse Kubernetes Platform на выделенных узлах

Добавляем NodeGroup мониторинг с необходимыми лейблами и тейнтами

```
apiVersion: deckhouse.io/v1
kind: NodeGroup
metadata:
  name: monitoring
spec:
  nodeType: Static
  nodeTemplate:
    labels:
      node-role.deckhouse.io/monitoring: ""
    taints:
      - effect: NoExecute
        key: dedicated.deckhouse.io
        value: monitoring
```

Добавляем в данную группу узлы

```
kubectl -n d8-cloud-instance-manager get secrets manual-bootstrap-for-monitoring -o json | jq -r '.data."bootstrap.sh"'
```

или с помощью **CAPS**

Убеждаемся, что для группы узлов есть доступный storageclass

Выключаем prometheus

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: prometheus
spec:
  version: 2
  enabled: false
EOF
```

Дожидаемся прохождения очередей Deckhouse и завершения подов prometheus и после включаем prometheus обратно

```
kubectl patch mc prometheus --type merge --patch='{"spec":{"enabled":true}}'
```

Дожидаемся прохождения очередей и проверяем, что поды prometheus разместились на новых узлах группы monitoring

```
~ $ kubectl -n d8-monitoring get pods -o wide -l prometheus
NAME                    READY   STATUS    RESTARTS   AGE    IP            NODE                                            NOMINATED NODE   READINESS GATES
prometheus-longterm-0   3/3     Running   0          117s   10.111.4.22   test-monitoring-7c379976-6b8f8-skgnp   <none>           <none>
prometheus-main-0       3/3     Running   0          117s   10.111.4.21   test-monitoring-7c379976-6b8f8-skgnp   <none>           <none>
prometheus-main-1       3/3     Running   0          117s   10.111.3.18   test-monitoring-0e3b78fc-67df6-nqk8d   <none>           <none>
```

## 11. Запуск модулей Deckhouse Enterprise версии

> Включить модуль `operator-trivy` и убедиться, что создался namespace `d8-operator-trivy` и в нем есть под dex

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: operator-trivy
spec:
  version: 1
  enabled: true
EOF
```

Проверить прохождения очередей Deckhouse
```
# До версии Deckhouse v1.59
kubectl -n d8-system exec -it deployments/deckhouse -c deckhouse -- deckhouse-controller queue list
# После версии Deckhouse v1.59 и при мульти-мастере
kubectl -n d8-system exec -it $(kubectl -n d8-system get leases.coordination.k8s.io deckhouse-leader-election -o jsonpath='{.spec.holderIdentity}' | awk -F'.' '{ print $1 }') -c deckhouse -- deckhouse-controller queue list
```

Проверяем, что поды в `d8-operator-trivy` запустились

```
kubectl -n d8-operator-trivy get pods
```

Пример вывода

```shell
~ $ kubectl -n d8-operator-trivy get pods
NAME                              READY   STATUS    RESTARTS   AGE
node-collector-6794468cf5-kzqnw   1/1     Running   0          6s
operator-88975ff9d-m8tzl          2/2     Running   0          55s
trivy-server-0                    1/1     Running   0          55s
```

## 12. Установка / добавление элементов интерфейса / модулей (из поставки платформы)

Включаем модуль [Console](https://deckhouse.ru/modules/console/stable/#%D0%BA%D0%B0%D0%BA-%D0%B2%D0%BA%D0%BB%D1%8E%D1%87%D0%B8%D1%82%D1%8C)
```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: console
spec:
  enabled: true
EOF
```

После прохождения очередей Dekchouse проверяем, что появились соответствующие ingress

```
~ $ kubectl -n d8-console get ingress frontend
frontend  nginx   console.example.com   158.160.156.133   80, 443   99s
```

А также появился пункт в grafana (веб-интерфейс Grafana можно получить `kubectl -n d8-monitoring get ingress grafana`)

## 13. Возможность отключения неиспользуемых модулей платформы

Отключить модуль upmeter и убедиться, что из кластера был удален namespace d8-upmeter

Убедимся, что модуль включён

```
kubectl -n d8-upmeter get pods
```

Пример вывода

```
~ $ kubectl -n d8-upmeter get pods
NAME                                         READY   STATUS    RESTARTS       AGE
smoke-mini-a-0                               1/1     Running   0              2m36s
smoke-mini-b-0                               1/1     Running   0              3m36s
smoke-mini-c-0                               1/1     Running   0              96s
smoke-mini-d-0                               1/1     Running   0              36s
smoke-mini-e-0                               1/1     Running   0              4m37s
status-ddf466df7-l9sk6                       1/1     Running   0              2d6h
status-dex-authenticator-67f87765d-nlgxb     2/2     Running   1 (2d6h ago)   2d6h
upmeter-0                                    2/2     Running   0              2d6h
upmeter-agent-jrg4c                          1/1     Running   2 (26h ago)    2d6h
upmeter-dex-authenticator-6dc9658cfd-4clkr   2/2     Running   1 (2d6h ago)   2d6h
webui-67bd74cbc-vmlkt                        1/1     Running   0              2d6h
```

Произвести отключение

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: upmeter
spec:
  version: 2
  enabled: false
EOF
```

Дождаться прохождения очередей Deckhouse и проверить наличие подов в namespace `d8-upmeter`

```
kubectl -n d8-upmeter get pods
kubectl get namespace d8-upmeter
```

Пример вывода

```
~ $ kubectl -n d8-upmeter get pods
No resources found in d8-upmeter namespace.
~ $ kubectl get namespace d8-upmeter
Error from server (NotFound): namespaces "d8-upmeter" not found
```

## 14. Отказоустойчивая конфигурация всех компонентов платформы

Получить состояние

```
kubectl -n d8-monitoring get statefulset prometheus-main
kubectl -n d8-monitoring get deployment grafana
kubectl -n d8-dashboard get deployment dashboard
```

Пример вывода
```
NAME              READY   AGE
prometheus-main   2/2     2d
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
grafana   2/2     2            2           2d
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
dashboard   2/2     2            2           2d
```

Размещение подов по нодам

```
kubectl -n d8-monitoring get pods -o wide | grep -E 'prometheus-main|grafana|dashboard'
```

Пример
```
~ $ kubectl -n d8-monitoring get pods -o wide | grep -E 'prometheus-main|grafana|dashboard'
grafana-5d9b8d7f86-j8rfn                         3/3     Running   0             117s    10.111.3.24    test-monitoring-0e3b78fc-67df6-nqk8d   <none>           <none>
grafana-5d9b8d7f86-lfgjf                         3/3     Running   0             2m30s   10.111.4.27    test-monitoring-7c379976-6b8f8-skgnp   <none>           <none>
grafana-dex-authenticator-6ccfff67c8-dd7cv       2/2     Running   0             2m      10.111.2.30    test-worker-d8fdbcc2-754df-xdpmk       <none>           <none>
grafana-dex-authenticator-6ccfff67c8-jqssq       2/2     Running   1 (85s ago)   91s     10.111.1.124   test-worker-7c379976-68579-drhkp       <none>           <none>
grafana-v10-76b46f8d5f-5q6f2                     3/3     Running   0             93s     10.111.3.26    test-monitoring-0e3b78fc-67df6-nqk8d   <none>           <none>
grafana-v10-76b46f8d5f-jzrp9                     3/3     Running   0             2m27s   10.111.4.28    test-monitoring-7c379976-6b8f8-skgnp   <none>           <none>
grafana-v10-dex-authenticator-575c679768-54x6k   2/2     Running   0             2m2s    10.111.1.123   test-worker-7c379976-68579-drhkp       <none>           <none>
grafana-v10-dex-authenticator-575c679768-kmlfl   2/2     Running   0             94s     10.111.2.31    test-worker-d8fdbcc2-754df-xdpmk       <none>           <none>
prometheus-main-0                                3/3     Running   0             3m51s   10.111.4.21    test-monitoring-7c379976-6b8f8-skgnp   <none>           <none>
prometheus-main-1                                3/3     Running   0             3m51s   10.111.3.18    test-monitoring-0e3b78fc-67df6-nqk8d   <none>           <none>
```

## 15. Управление namespaces (добавление, удаление, редактирование)

Создать / удалить / добавить labels на произвольный namespace

Создать namespace
```
kubectl create namespace test-namespace
```

Добавим лейбл

```
~ $ kubectl label namespace test-namespace mylabel=label
namespace/test-namespace labeled
```

Убедиться, что лейбл появился
```
~ $ kubectl get namespace test-namespace -o yaml
apiVersion: v1
kind: Namespace
metadata:
  creationTimestamp: "2024-05-07T15:20:12Z"
  labels:
    kubernetes.io/metadata.name: test-namespace
    mylabel: label
  name: test-namespace
  resourceVersion: "855611"
  uid: 7f1494b7-83c3-48ec-ab9d-e79a58b00253
spec:
  finalizers:
  - kubernetes
status:
  phase: Active
```

## 16. Возможность использования внешних модулей

Согласно быстрому старту устанавливаем postres-operator

```
kubectl apply -k github.com/zalando/postgres-operator/manifests
```

Проверяем, что оператор запустился (в default namespace)
```
~ $ kubectl get pods
NAME                                 READY   STATUS    RESTARTS        AGE
postgres-operator-78dffd89df-ztmvk   1/1     Running   1 (2m42s ago)   3m4s
```

# Безопасность

## 17. Аудит событий Kubernetes API

Убедиться, что в файле имеются `/var/log/kube-audit/audit.log` события

Пример

```
~# tail -1 /var/log/kube-audit/audit.log
{"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"Metadata","auditID":"698ed1e5-6db1-4477-98eb-823043bf87c0","stage":"ResponseComplete","requestURI":"/apis/authentication.k8s.io/v1/tokenreviews","verb":"create","user":{"username":"system:serviceaccount:d8-monitoring:grafana","uid":"551dceb9-4f4c-4122-a919-e44fcb46e0e5","groups":["system:serviceaccounts","system:serviceaccounts:d8-monitoring","system:authenticated"],"extra":{"authentication.kubernetes.io/pod-name":["grafana-7888f986f-4m9s6"],"authentication.kubernetes.io/pod-uid":["24cb17fe-f6b4-40fb-a98c-ebaed0361db0"]}},"sourceIPs":["10.111.4.199"],"userAgent":"kube-rbac-proxy/v0.0.0 (linux/amd64) kubernetes/$Format","objectRef":{"resource":"tokenreviews","apiGroup":"authentication.k8s.io","apiVersion":"v1"},"responseStatus":{"metadata":{},"code":201},"requestReceivedTimestamp":"2024-05-10T19:05:57.096125Z","stageTimestamp":"2024-05-10T19:05:57.098075Z","annotations":{"authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":"RBAC: allowed by ClusterRoleBinding \"d8:prometheus:grafana:rbac-proxy\" of ClusterRole \"d8:rbac-proxy\" to ServiceAccount \"grafana/d8-monitoring\""}}
```

## 18. Фильтрации трафика внутри кластера (поддержка NetworkPolicy). Только для кластеров с CNI Cilium

Создадим namespace для экспериментов

```
kubectl create namespace np-test
```

Создадим в нём деплоймент nginx и сервис к данному деплойменту

```
kubectl -n np-test create deployment nginx --image=nginx
kubectl -n np-test expose deployment nginx --port=80
```

Проверим доступ к сервису из другого пода

Запустим под
```
kubectl -n np-test run busybox --rm -ti --image=busybox -- /bin/sh
```

и проверим доступ к nginx
```
wget -S --spider --timeout=1 nginx
```

Пример вывода
```
/ # wget -S --spider --timeout=1 nginx
Connecting to nginx (10.222.210.117:80)
  HTTP/1.1 200 OK
  Server: nginx/1.25.5
  Date: Mon, 13 May 2024 18:46:22 GMT
  Content-Type: text/html
  Content-Length: 615
  Last-Modified: Tue, 16 Apr 2024 14:29:59 GMT
  Connection: close
  ETag: "661e8b67-267"
  Accept-Ranges: bytes

remote file exists
```

т.е. доступ успешно получен

Теперь ограничим доступ к поду nginx только с подов с лейблом `access=true`

```
kubectl -n np-test create -f -<<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: access-nginx
spec:
  podSelector:
    matchLabels:
      app: nginx
  ingress:
  - from:
    - podSelector:
        matchLabels:
          access: "true"
EOF
```

и повторим проверку доступа

```
/ # wget -S --spider --timeout=1 nginx
Connecting to nginx (10.222.210.117:80)
wget: download timed out
```

Как видно, ответа не получили

Теперь создадим под с лейблом `access=true` и проверим доступ снова

```
kubectl -n np-test run busybox --rm -ti --labels="access=true" --image=busybox -- /bin/sh
```

Результат проверки
```
/ # wget -S --spider --timeout=1 nginx
Connecting to nginx (10.222.210.117:80)
  HTTP/1.1 200 OK
  Server: nginx/1.25.5
  Date: Mon, 13 May 2024 18:50:48 GMT
  Content-Type: text/html
  Content-Length: 615
  Last-Modified: Tue, 16 Apr 2024 14:29:59 GMT
  Connection: close
  ETag: "661e8b67-267"
  Accept-Ranges: bytes

remote file exists
```

## 19. Фильтрация трафика на уровне L7 внутри кластера

Создадим namespace для экспериментов

```
kubectl create namespace cnp-test
```

Добавим деплоймент echo-сервера

```
kubectl -n cnp-test create deployment echo-server --image=ealen/echo-server
kubectl -n cnp-test expose deployment echo-server --port=80
```

Применим политику
```
kubectl -n cnp-test create -f -<<EOF
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "access-echo-server"
spec:
  description: "Allow HTTP GET /public from access=true to app=echo-server"
  endpointSelector:
    matchLabels:
      app: echo-server
  ingress:
  - fromEndpoints:
    - matchLabels:
        access: "true"
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/public"
EOF
```

Проверим доступ к сервису

```
kubectl -n cnp-test run busybox --rm -ti --labels="access=true" --image=busybox -- /bin/sh
```

```
wget -S --spider --timeout=1 echo-server
wget -S --spider --timeout=1 echo-server/public
```

Пример
```
/ # wget -S --spider --timeout=1 echo-server
Connecting to echo-server (10.222.111.196:80)
  HTTP/1.1 403 Forbidden
wget: server returned error: HTTP/1.1 403 Forbidden
/ # wget -S --spider --timeout=1 echo-server/public
Connecting to echo-server (10.222.111.196:80)
  HTTP/1.1 200 OK
  content-type: application/json; charset=utf-8
  content-length: 1230
  etag: W/"4ce-IMcgvS4Z4rmT2+ns8Rj3gMMNT/0"
  date: Wed, 15 May 2024 12:25:24 GMT
  x-envoy-upstream-service-time: 16
  server: envoy
  connection: close

remote file exists
```

Как видно, запрос к `/` отдаёт 403, а на `/public` - 200

При этом запросы с пода без необходимого лейбла вовсе будут давать таймаут

```
kubectl -n cnp-test run busybox --rm -ti --image=busybox -- /bin/sh
If you don't see a command prompt, try pressing enter.
/ # wget -S --spider --timeout=1 echo-server
Connecting to echo-server (10.222.111.196:80)
wget: download timed out
/ # wget -S --spider --timeout=1 echo-server/public
Connecting to echo-server (10.222.111.196:80)
wget: download timed out
```

## 20. Отображения действия политик (NetworkPolicy) в веб-интерфейсе

Включаем модуль cilium-hubble

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: cilium-hubble
spec:
  version: 2
  enabled: true
EOF
```

Получаем доступ к веб-интерфейсу

```
kubectl -n d8-cni-cilium get ingress hubble-ui
```

Выбираем необходимый namespace np-test из предыдущего шага и проводим аналогичные запросы из подов без лейблов

Наблюдаем `audit` потоки

## 21. Возможность использования корпоративного TLS/SSL сертификата для компонентов платформы

https://deckhouse.ru/documentation/v1/modules/101-cert-manager/faq.html#%D0%BA%D0%B0%D0%BA-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-%D1%81%D0%B2%D0%BE%D0%B9-%D0%B8%D0%BB%D0%B8-%D0%BF%D1%80%D0%BE%D0%BC%D0%B5%D0%B6%D1%83%D1%82%D0%BE%D1%87%D0%BD%D1%8B%D0%B9-ca-%D0%B4%D0%BB%D1%8F-%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7%D0%B0-%D1%81%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D0%B2

Создадим RootCA - на примере самоподписанного

```
mkdir certs
openssl req -x509 -newkey rsa:4096 -keyout certs/wild.private.key -out certs/wild.public.crt -sha256 -days 3650 -nodes -subj "/C=RU/ST=SPB/L=SPB/O=MYORG/OU=MYORG/CN=My Super Cool Certificate"
```

Создадим секрет с данным сертфиикатом

```
kubectl create secret tls internal-ca-key-pair -n d8-cert-manager --key certs/wild.private.key --cert certs/wild.public.crt
```

И создазим ClusterIssuer

```
kubectl create -f -<<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: inter-ca
spec:
  ca:
    secretName: internal-ca-key-pair
EOF
```

Убедимся, что он создался

```
~ $ kubectl get clusterissuers.cert-manager.io inter-ca
NAME       READY   AGE
inter-ca   True    19m
```

После чего переключим сертификаты на использование данного ClusterIssuer

```
kubectl edit mc global
```

и добавим блок в `spec`
```
      https:
        certManager:
          clusterIssuerName: inter-ca
        mode: CertManager
```

Проверить, что сертификаты перевыпустились на использование inter-ca

```
~$ curl --verbose --insecure https://grafana.158.160.147.28.sslip.io/ 2>&1 | grep -A5 'Server certificate'
* Server certificate:
*  subject: CN=grafana.158.160.147.28.sslip.io
*  start date: May 20 22:22:05 2024 GMT
*  expire date: Aug 18 22:22:05 2024 GMT
*  issuer: C=RU; ST=SPB; L=SPB; O=MYORG; OU=MYORG; CN=My Super Cool Certificate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
```

## 22. Использования временных статических пользователей в кластере

Установить htpasswd

Для Debian-based ОС
```
sudo apt install apache2-utils
```

Воспользоваться сниппетом

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: User
metadata:
  name: my-user
spec:
  email: myuser@example.com
  password: $(echo "my-super-password-QWEzxc" | htpasswd -BinC 10 "" | cut -d: -f2 | base64 -w0)
  ttl: 1h
EOF
```

Дождаться прохождения очередей

Войти в grafana (`kubectl -n d8-monitoring get ingress grafana`) с созданным пользователем `myuser@example.com` и паролем `my-super-password-QWEzxc`

Через время ttl равное 1 часу проверить, что пользователь удалился

```
~ $ kubectl get users.deckhouse.io my-user
Error from server (NotFound): users.deckhouse.io "my-user" not found
```

## 23. Использование статических групп пользователей в кластере

Зайдём в kubeconfig (`kubectl -n d8-user-authn get ingress kubeconfig-generator`) от созданного в предыдущем пункте пользователя и скачаем конфиг для kubectl и попробуем выполнить получение списка namespace

```
kubectl --kubeconfig /tmp/myconf get namespaces
Error from server (Forbidden): namespaces is forbidden: User "myuser@example.com" cannot list resource "namespaces" in API group "" at the cluster scope
```

Добавим группу

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: Group
metadata:
  name: my-users
spec:
  name: my-users
  members:
    - kind: User
      name: my-user
EOF
```

и права для группы
```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: ClusterAuthorizationRule
metadata:
  name: my-users
spec:
  subjects:
  - kind: Group
    name: my-users
  accessLevel: User
EOF
```

Проверим доступ

```
kubectl --kubeconfig /tmp/myconf get namespaces
NAME                               STATUS        AGE
d8-admission-policy-engine         Active        4h5m
d8-cert-manager                    Active        4h4m
d8-chrony                          Active        4h16m
d8-cloud-instance-manager          Active        4h17m
d8-cni-cilium                      Active        4h18m
d8-dashboard                       Active        4h2m
d8-descheduler                     Active        4h3m
d8-ingress-nginx                   Active        4h2m
d8-local-path-provisioner          Active        4h18m
d8-log-shipper                     Active        4h2m
d8-monitoring                      Active        4h18m
d8-operator-prometheus             Active        4h4m
d8-pod-reloader                    Active        4h2m
d8-service-accounts                Active        4h18m
d8-system                          Active        4h20m
d8-upmeter                         Active        4h2m
d8-user-authn                      Active        4h4m
default                            Active        4h21m
kube-node-lease                    Active        4h21m
kube-public                        Active        4h21m
kube-system                        Active        4h21m
upmeter-probe-namespace-4112598c   Terminating   2s
upmeter-probe-namespace-f733fe8d   Terminating   5s
```

## 24. Использование внешнего провайдера аутентификации (LDAP/AD/OIDC)

Воспользоваться интеграцией с [keycloak](https://fox.flant.com/team/dpdcs/arch/deckhouse-features-demo/-/blob/main/integrations_examples/keycloak/README.md?ref_type=heads)

## 25. Настройка ролевой модели доступа на основе групп, атрибутов пользователя

Включить пользователя в группу (добавить роль в контексте Keycloak) administrators

Добавить CAR

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: ClusterAuthorizationRule
metadata:
  name: admin
spec:
  accessLevel: SuperAdmin
  allowScale: false
  portForwarding: true
  subjects:
  - kind: Group
    name: administrators
EOF
```

Сгенерировать kubeconfig и проверить доступ

Пример вывода
```
~ $ kubectl --kubeconfig /tmp/kubeconfig2 get mc
NAME         ENABLED   VERSION   AGE   MESSAGE
deckhouse    true      1         24h
global                 1         24h
kube-dns     true      1         11h
user-authn   true      1         24h
```

## 26. Ограничение доступа пользователей к определенным namespace

Настраиваем модуль 

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: user-authz
spec:
  version: 1
  enabled: true
  settings:
    enableMultiTenancy: true
EOF
```

Создаём пользователя и CAR к нему

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: User
metadata:
  name: my-user2
spec:
  email: myuser2@example.com
  password: $(echo "my-super-password-QWEzxc" | htpasswd -BinC 10 "" | cut -d: -f2 | base64 -w0)
  ttl: 12h
EOF
```

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: ClusterAuthorizationRule
metadata:
  name: user-with-limit
spec:
  accessLevel: User
  namespaceSelector:
    labelSelector:
      matchLabels:
        team: my-user2
  subjects:
  - kind: User
    name: myuser2@example.com
EOF
```

Создадим namespace и присвоим ему label
```
kubectl create namespace test-namespace-limit
kubectl label namespace test-namespace-limit team=my-user2
```

Сгенерируем kubeconfig и проверим доступ

```
~$ kubectl --kubeconfig /tmp/user-limit-kubeconfig get pods
Error from server (Forbidden): pods is forbidden: User "myuser2@example.com" cannot list resource "pods" in API group "" in the namespace "default": user has no access to the namespace
~$ kubectl --kubeconfig /tmp/user-limit-kubeconfig -n test-namespace-limit get pods
No resources found in test-namespace-limit namespace.
```

## 27. Возможность расширения прав доступа

Продолжим с пользователем из предыдущего шага, так как пользователь у нас с правами User, то он не имеет доступ к секретам

```
~$ kubectl --kubeconfig /tmp/user-limit-kubeconfig -n test-namespace-limit get secrets
Error from server (Forbidden): secrets is forbidden: User "myuser2@example.com" cannot list resource "secrets" in API group "" in the namespace "test-namespace-limit"
```

Расширим права User для чтения секретов

```
kubectl create -f -<<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    user-authz.deckhouse.io/access-level: User
  name: user-with-secrets
rules:
- apiGroups:
  - ""
  resources:
  - secrets
  verbs:
  - get
  - list
  - watch
EOF
```

После применения
```
~$ kubectl --kubeconfig /tmp/user-limit-kubeconfig -n test-namespace-limit get secrets
No resources found in test-namespace-limit namespace.
```

## 28. Использование сервисной учетной записи для выката прикладного ПО в платформу

https://deckhouse.ru/documentation/v1/modules/140-user-authz/usage.html#%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5-serviceaccount-%D0%B4%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D0%B8-%D0%BF%D1%80%D0%B5%D0%B4%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B5%D0%BC%D1%83-%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0

С использованием данной учётной записи выкатить приложение

```
kubectl --kubeconfig kube.config create deployment nginx --image=nginx
```

## 29. Создание статического пользователя с помощью клиентского сертификата

https://deckhouse.ru/documentation/v1/modules/140-user-authz/usage.html#%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81-%D0%BF%D0%BE%D0%BC%D0%BE%D1%89%D1%8C%D1%8E-%D0%BA%D0%BB%D0%B8%D0%B5%D0%BD%D1%82%D1%81%D0%BA%D0%BE%D0%B3%D0%BE-%D1%81%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82%D0%B0

```
mkdir user-cert
cd user-cert/
openssl genrsa -out myuser.key 2048
openssl req -new -key myuser.key -out myuser.csr -subj "/CN=myuser/O=mygroup1/O=mygroup2"
openssl x509 -req -in myuser.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out myuser.crt -days 10
```

```
cat << EOF > myuser-kubeconfig
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: $(cat /etc/kubernetes/pki/ca.crt | base64 -w0)
    server: https://<хост кластера>:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: myuser
  name: myuser@kubernetes
current-context: myuser@kubernetes
kind: Config
preferences: {}
users:
- name: myuser
  user:
    client-certificate-data: $(cat myuser.crt | base64 -w0)
    client-key-data: $(cat myuser.key | base64 -w0)
EOF
```

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: ClusterAuthorizationRule
metadata:
  name: myuser
spec:
  subjects:
  - kind: User
    name: myuser
  accessLevel: PrivilegedUser
  portForwarding: true
EOF
```

Проверить доступ с использованием сгенерированного kubeconfig

```
kubectl --kubeconfig myuser-kubeconfig get pods
NAME                    READY   STATUS    RESTARTS   AGE
nginx-76d6c9b8c-qthtm   1/1     Running   0          8m52s
```

## 30. Использование политик безопасности Kubernetes (Pod Security Standards)

Создадим namespace

```
kubectl create namespace pod-sec-test
```

Применим на него политику
```
kubectl label ns pod-sec-test security.deckhouse.io/pod-policy=restricted
```

Создадим под
```
kubectl -n pod-sec-test create -f -<<EOF
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: sec-ctx-demo
    image: busybox:1.28
    command: [ "sh", "-c", "sleep 1h" ]
    securityContext:
      privileged: true
      allowPrivilegeEscalation: true
      capabilities:
        drop:
        - ALL
EOF
```

Получим ошибки вида о нарушении политик
```
Error from server (Forbidden): error when creating "STDIN": admission webhook "admission-policy-engine.deckhouse.io" denied the request: [d8-pod-security-restricted-deny-default] Privilege escalation container is not allowed: sec-ctx-demo
[d8-pod-security-baseline-deny-default] Privileged container is not allowed: sec-ctx-demo, securityContext: {"capabilities": {"drop": ["ALL"]}, "privileged": true}
```

И под не создастся

```
~ $ kubectl -n pod-sec-test get pods
No resources found in pod-sec-test namespace.
```

## 31. Использование операционных политик для безопасной работы прикладного ПО

Применим политику, ограничивающую реджистри, с которых можно использовать имеджи

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: OperationPolicy
metadata:
  name: common
spec:
  policies:
    allowedRepos:
      - docker.io
      - myrepo.example.com
      - registry.deckhouse.io
  match:
    namespaceSelector:
      labelSelector:
        matchLabels:
          operation-policy.deckhouse.io/enabled: "true"
EOF
```

Создадим namespace и поставим на него лейбл

```
kubectl create namespace pod-ops-test
kubectl label namespace pod-ops-test operation-policy.deckhouse.io/enabled=true
```

И создадим деплоймент

```
kubectl -n pod-ops-test create deployment hello --image quay.io/podman/hello
```

Увидим, что под не создался, а в events зафиксировалось нарушение политики
```
~ $ kubectl -n pod-ops-test get pods
No resources found in pod-ops-test namespace.
~ $ kubectl -n pod-ops-test get events
LAST SEEN   TYPE      REASON              OBJECT                       MESSAGE
62s         Warning   FailedCreate        replicaset/hello-d55bf4c7b   Error creating: admission webhook "admission-policy-engine.deckhouse.io" denied the request: [common] container <hello> has an invalid image repo <quay.io/podman/hello>, allowed repos are ["docker.io", "myrepo.example.com", "registry.deckhouse.io"]
```

## 32. Использование политик безопасности для безопасной работы прикладного ПО

Добавим политику

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: SecurityPolicy
metadata:
  name: mypolicy
spec:
  enforcementAction: Deny
  policies:
    allowPrivileged: false
  match:
    namespaceSelector:
      labelSelector:
        matchLabels:
          enforce: mypolicy
EOF
```

Создадим namespace

```
kubectl create namespace test-custom-sec-policy
kubectl label namespace test-custom-sec-policy enforce=mypolicy
```

Создадим deployment

```
kubectl -n test-custom-sec-policy create deployment nginx --image=nginx
```

Увидим, что под не смог создаться и в events получим причину
```
~ $ kubectl -n test-custom-sec-policy get pods
No resources found in test-custom-sec-policy namespace.
~ $ kubectl -n test-custom-sec-policy get events
LAST SEEN   TYPE      REASON              OBJECT                       MESSAGE
4s          Warning   FailedCreate        replicaset/nginx-76d6c9b8c   Error creating: admission webhook "admission-policy-engine.deckhouse.io" denied the request: [mypolicy] Privilege escalation container is not allowed: nginx
9s          Normal    ScalingReplicaSet   deployment/nginx             Scaled up replica set nginx-76d6c9b8c to
```

## 33. Возможность использовать квот в рамках namespaces

Создадим namespace
```
kubectl create namespace test-rq
```

Применим ресурс
```
kubectl -n test-rq create -f -<<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
EOF
```

Создадим под с превышением выделенных ресурсов
```
kubectl -n test-rq create -f -<<EOF
apiVersion: v1
kind: Pod
metadata:
  name: frontend
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "4000m"
      limits:
        memory: "128Mi"
        cpu: "8000m"
EOF
```

Должны получить ошибку создания
```
Error from server (Forbidden): error when creating "STDIN": pods "frontend" is forbidden: exceeded quota: compute-resources, requested: limits.cpu=8,requests.cpu=4, used: limits.cpu=500m,requests.cpu=250m, limited: limits.cpu=2,requests.cpu=1
```

## 34. Создание изолированного окружения по заготовленному шаблону

Включаем модуль

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: multitenancy-manager
spec:
  enabled: true
EOF
```

Создадим проект

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha2
kind: Project
metadata:
  name: my-project
spec:
  description: This is an example from the Deckhouse documentation.
  projectTemplateName: default
  parameters:
    resourceQuota:
      requests:
        cpu: 5
        memory: 5Gi
        storage: 1Gi
      limits:
        cpu: 5
        memory: 5Gi
    networkPolicy: Isolated
    podSecurityProfile: Restricted
    extendedMonitoringEnabled: true
    administrators:
    - subject: Group
      name: k8s-admins
EOF
```

Проверим статус проёкта и созданные внутри неймспейса проёкта ресурсы, например `ResourceQuota`

```
kubectl get projects my-project
kubectl -n my-project get resourcequotas
```

Пример вывода
```
~ $ kubectl get projects my-project
NAME         STATE   PROJECT TEMPLATE   DESCRIPTION
my-project   Sync    default            This is an example from the Deckhouse documentation.
~ $ kubectl -n my-project get resourcequotas
NAME       AGE     REQUEST                                                              LIMIT
all-pods   3m42s   requests.cpu: 0/5, requests.memory: 0/5Gi, requests.storage: 0/1Gi   limits.cpu: 0/5, limits.memory: 0/5Gi
```

## 35. Обнаружение угроз безопасности анализирую прикладное ПО и контейнеры

Включаем модуль
```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: runtime-audit-engine
spec:
  enabled: true
EOF
```

Применим политику из примера в документации https://deckhouse.ru/documentation/v1/modules/650-runtime-audit-engine/examples.html#%D0%B4%D0%BE%D0%B1%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%B0-%D0%B4%D0%BB%D1%8F-%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B8-%D1%83%D0%B2%D0%B5%D0%B4%D0%BE%D0%BC%D0%BB%D0%B5%D0%BD%D0%B8%D0%B9-%D0%BE-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA%D0%B5-shell-%D0%BE%D0%B1%D0%BE%D0%BB%D0%BE%D1%87%D0%BA%D0%B8-%D0%B2-%D0%BA%D0%BE%D0%BD%D1%82%D0%B5%D0%B9%D0%BD%D0%B5%D1%80%D0%B5

Запустим bash

```
kubectl -n d8-system exec -ti deckhouse-54bc865957-ktz69 -- bash -c 'echo hello'
```

И найдём наше событие согласно https://deckhouse.ru/documentation/v1/modules/650-runtime-audit-engine/advanced_usage.html#%D0%BF%D1%80%D0%BE%D1%81%D0%BC%D0%BE%D1%82%D1%80-%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D0%BA

Например
```
kubectl -n d8-monitoring exec -it prometheus-main-0 prometheus -- curl -s http://127.0.0.1:9090/api/v1/query\?query\=falco_events | jq '.data.result[] | select(.metric.rule == "run_shell_in_container")'
```

## 36. Организация mTLS между узлами прикладного ПО

Включаем модуль

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: istio
spec:
  version: 2
  enabled: true
EOF
```

```
kubectl create namespace test-istio
kubectl label namespace test-istio istio-injection=enabled
kubectl label namespace test-istio security.deckhouse.io/pod-policy=privileged
```

Добавим политику (для ясности, по умолчанию именно PERMISSIVE и устанавливается, в данном режиме между участниками mesh-сети трафик будет зашифрован, но также будет возможность принимать не зашифрованный трафик. В STRICT режиме возможность подключения будет только участникам mesh-сети)
```
kubectl -n test-istio create -f -<<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: PERMISSIVE
EOF
```

Создадим deployment
```
kubectl -n test-istio create deployment nginx --image=nginx
kubectl -n test-istio expose deployment nginx --port=80
```

Получим адрес пода и ноду, на которой он запущен для запуска на данной ноде tcpdump для анализа трафика
```
~ $ kubectl -n test-istio get pods -o wide
NAME                    READY   STATUS    RESTARTS   AGE   IP             NODE                                        NOMINATED NODE   READINESS GATES
nginx-76d6c9b8c-9mdtb   2/2     Running   0          48m   10.111.1.122   test-worker-e36e4712-5948b-sp9t8   <none>           <none>
```

Перейдём на данную ноду по SSH от root-пользователя для запуска tcpdump

```
tcpdump -A -v -i any host 10.111.1.122 and port 80
```

И запустим curl из того же неймспейса, т.е. под будет участником mesh-сети
```
kubectl -n test-istio run curl --rm -ti --image=curlimages/curl -- curl nginx
```

В tcpdump увидим зашифрованный трафик
```
    10.111.1.159.51122 > 10.111.1.122.http: Flags [P.], cksum 0x2310 (incorrect -> 0x63c8), seq 518:3321, ack 3031, win 140, options [nop,nop,TS val 1145309596 ecr 363185222], length 2803: HTTP
E..'C.@.@...
o..
o.z...P.bmm...K....#......
DD	....F.........
....B........V...J57.c>.<..:.x..C&...|.@...*$......8*{....KH.E0J0...}~7...m.........K....Inp.....k.Lv.....R<......y(......p......9..5..]O.......Y.....s..6.	<.swi,6....._..l.....B^^L.......yYfzY....~<...;...>o...Y#<.@...`vP...c-..........r*..A3e#..^.w{.a.g4nV.../D...k......Q...!o.PD.. M..Lxl.MY...@x...y....G.....F.g...RNB|D=.,..B..ZX.s<'fm.E.....O[8-..R...D.-...._-. .u......4.(..6.B....:|.R..s..vNs0..S3..g........B.F......l.X...h....f^......-.....z...+...x./
m+	t-?...W...._A@D%..U=..~._}.xT.2i...~.}...%...P_.I..+.%T.(..@y..u..)..k,...e......
..7....d.........T_{J....94....1>..._%~J...
u.;...GjF...z...4!.....V...../.M..pz..&pk]+.7Y..F.....d..^:L#P. ...3.f.5~._....,....`?......t`......Z.}...|.....=)g.'n.O...1......!$.Lg....z.g..DC(..._...........C.!....m.#D8.....L.;.....Y.W.p,5={".p..*.'......b......L...z.X.U..A.2..x..c.>.../...M.
..7x.y....$a.$f.8..u..U.!.Yim.9..t.....'....Vs..x.4......l.....m.......*..S....k...'.5.%9Y.G.....F.Eh..w=..G..yH1....fJ..q:..~...(....T.k.?...B}..W.WiV.Y.'(.Pn.
$$*./......(-.4bCc.^..T).....3P....%U.].egx..t...>gJ....{;.(.hO..^.7RQ....$.o..m"[..w..aD?Z:.7.m_......+.........u]W!..&m	ny~.Y..cak.n.........A..E....5.<...m@ql;kz......`...y..<.cs.....NIU...........s.l.Y.8.5...di..Rs.?.l.%h......S..@.6...=rU1.N...`T..	.}N...w..-...>.......m...........u.m..2...=..`....... ......p%H.	x...TD.b;S.K-4...`..6.V..D1..O..7S1y*=.mV.Gq4TS...s.,..&'7K>..#...S.6.o.b..F...;...&b..?,]..IwY...-....6..........T.H....0......@{|.3.......S.I....j	..]G...h.......ZI....>1.YTx.~....s......G	..f..p.."...mi...........AJ"..7......q..v[...._..5.^\.sn.A.O.g.........1.!.5^...L71`	.q.......[F.PY..*2'1...[...W..}G..._V9.(].^..O.Z5{a...........N......O.l...tz.\.|...?.d!:.z&z...=....d...P..Z..N.m...5r..i.............Fe.v.^....Rh.....P......k..`.....N..3....^.........\..S...=9.2}.....T..~.............59#.....f....S...AC.(....;...h.m..1W.{bU.......Df.G.....D..."..J>|L....1.........!#.(..FY*..I....I.2.S.m..O...Q..H4..<...q.....fr..	...d)>.._.2V...Y...nI...@..5.................7	.>Atz6@.....T..Qs.j.sk...lJ.+.*o:	..IxM.t..j......!4......>.......t....Q.......OT...B.NHX...v..../...t...*...[....2v.....3...9.~.r.V=Y.e@....G..E.$K1../$.....
```

И запустим curl из друго неймспейса (без istio), т.е. под не будет участником mesh-сети
```
kubectl -n default run curl --rm -ti --image=curlimages/curl -- curl nginx.test-istio
```

В tcpdump обнаружим plaint text запросы и ответы вида
```
    10.111.1.161.52496 > 10.111.1.122.http: Flags [P.], cksum 0x186d (incorrect -> 0x771b), seq 1:79, ack 1, win 128, options [nop,nop,TS val 3409477578 ecr 3323225931], length 78: HTTP, length: 78
	GET / HTTP/1.1
	Host: nginx.test-mtls
	User-Agent: curl/8.8.0
	Accept: */*

E....s@.@.I

o..
o.z...P...B.|.......m.....
.8....gKGET / HTTP/1.1
Host: nginx.test-mtls
User-Agent: curl/8.8.0
Accept: */*


15:28:21.896631 vethd6d7f7c6 P   IP (tos 0x0, ttl 64, id 52355, offset 0, flags [DF], proto TCP (6), length 52)
    10.111.1.122.http > 10.111.1.161.52496: Flags [.], cksum 0x181f (incorrect -> 0xe9a1), ack 79, win 128, options [nop,nop,TS val 3323225931 ecr 3409477578], length 0
E..4..@.@.VH
o.z
o...P...|.................
..gK.8..
15:28:21.900010 vethd6d7f7c6 P   IP (tos 0x0, ttl 64, id 52356, offset 0, flags [DF], proto TCP (6), length 983)
    10.111.1.122.http > 10.111.1.161.52496: Flags [P.], cksum 0x1bc2 (incorrect -> 0xcd47), seq 1:932, ack 79, win 128, options [nop,nop,TS val 3323225935 ecr 3409477578], length 931: HTTP, length: 931
	HTTP/1.1 200 OK
	server: istio-envoy
	date: Mon, 27 May 2024 15:28:21 GMT
	content-type: text/html
	content-length: 615
	last-modified: Tue, 16 Apr 2024 14:29:59 GMT
	etag: "661e8b67-267"
	accept-ranges: bytes
	x-envoy-upstream-service-time: 0
	x-envoy-decorator-operation: nginx.test-mtls.svc.cluster.local:80/*

	<!DOCTYPE html>
	<html>
	<head>
	<title>Welcome to nginx!</title>
	<style>
	html { color-scheme: light dark; }
	body { width: 35em; margin: 0 auto;
	font-family: Tahoma, Verdana, Arial, sans-serif; }
	</style>
	</head>
	<body>
	<h1>Welcome to nginx!</h1>
```

## 37. Организация авторизации доступа между сервисами

Запустим echo-server

```
kubectl -n test-istio create deployment echo-server --image=ealen/echo-server
kubectl -n test-istio expose deployment echo-server --port=80
```

Добавим политику
```
kubectl -n test-istio create -f -<<EOF
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: nginx-allow-only-info
spec:
  action: ALLOW
  rules:
  - from:
    - source:
        namespaces: ["test-istio2"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/info"]
EOF
```

Создадим namespace, сделаем его участником сети
```
kubectl create namespace test-istio2
kubectl label namespace test-istio2 istio-injection=enabled
kubectl label namespace test-istio2 security.deckhouse.io/pod-policy=privileged
```

Проведём тесты (последовательно, дожидаясь удаления пода)
```
kubectl -n test-istio run curl --rm -ti --image=curlimages/curl -- curl --verbose echo-server # Получим 403
kubectl -n test-istio run curl --rm -ti --image=curlimages/curl -- curl --verbose echo-server/info # Получим 403
kubectl -n test-istio2 run curl --rm -ti --image=curlimages/curl -- curl --verbose echo-server.test-istio # Получим 403
kubectl -n test-istio2 run curl --rm -ti --image=curlimages/curl -- curl --verbose echo-server.test-istio/info # Получим 200
```

## 38. Сканирование образов прикладного ПО на наличие известных уязвимостей

Включить модуль

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: operator-trivy
spec:
  version: 1
  enabled: true
EOF
```

Пометить namespace для сканирования образов

```
kubectl label namespace test-istio security-scanning.deckhouse.io/enabled=""
```

После проведения сканирования получить отчёты
```
kubectl -n test-istio get vulnerabilityreports.aquasecurity.github.io
```

Пример
```
~ $ kubectl -n test-istio get vulnerabilityreports.aquasecurity.github.io
NAME                                            REPOSITORY          TAG      SCANNER   AGE
replicaset-echo-server-784c467f5b-echo-server   ealen/echo-server   latest   Trivy     16m
```

В Grafana - https://grafana.DOMAIN.TLD/dashboards - Security -> Trivy Image Vulnerability Overview

# Мониторинг

## 39. Встроенный мониторинг состояния служебных компонент кластера

В Grafana - https://grafana.DOMAIN.TLD/dashboards - Main -> Deckhouse

## 40. Мониторинг аппаратных ресурсов платформы

В Grafana - https://grafana.DOMAIN.TLD/dashboards - Kubernetes Cluster -> Nodes

## 41. Мониторинг Kubernetes в составе платформы

В Grafana - https://grafana.DOMAIN.TLD/dashboards

Kubernetes Cluster -> Control Plane Status
Kubernetes Cluster -> etcd3

## 42. Встроенный мониторинг входящего трафика

В Grafana - https://grafana.DOMAIN.TLD/dashboards - Ingress Nginx -> Vhosts

## 43. Оценка использования ресурсов

В Grafana - https://grafana.DOMAIN.TLD/dashboards - Main -> Capacity Planning

## 44. Уведомления (alerts) по нагрузке серверов кластера, количество ошибочных запросов ingress и пр.

Перейти в https://grafana.DOMAIN.TLD/prometheus/alerts и ознакомиться со списком

## 45. Расширенный мониторинг состояния прикладных сервисов

Создадим namespace test-em

```
kubectl create namespace test-em
kubectl label namespace test-em extended-monitoring.deckhouse.io/enabled=""
```

Создадим заведомо сломанный deployment

```
kubectl -n test-em create deployment nginx --image nginx:not_exist_tag
```

Через 5 минут (время срабатывания алерта) проверяем наличие алерта `KubernetesDeploymentReplicasUnavailable`

```
kubectl get clusteralerts.deckhouse.io
NAME               ALERT                                      SEVERITY   AGE     LAST RECEIVED   STATUS
d8f67d4fa496f796   KubernetesDeploymentReplicasUnavailable    5          10m     53s             firing
```

## 46. Мониторинг прикладных сервисов

Произведём деплой приложения https://github.com/brancz/prometheus-example-app (https://quay.io/repository/brancz/prometheus-example-app?tab=info)

```
kubectl create deployment prometheus-example-app --image quay.io/brancz/prometheus-example-app:v0.5.0
kubectl expose deployment prometheus-example-app --port 8080
```

И согласно документации проставим лейбл и аннотацию

```
kubectl label service prometheus-example-app prometheus.deckhouse.io/custom-target=prometheus-example-app
kubectl annotate service prometheus-example-app prometheus.deckhouse.io/port=8080
```

После чего переходим в https://grafana.DOMAIN.TLD/prometheus/ и вводим запрос `{job="custom-prometheus-example-app"}` и убеждаемся в наличии метрик

## 47. Возможность добавления своего набора уведомлений (alerts)

Применим правило по метрикам, собираемым с сервиса, поднятого в предыдущем пункте

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: CustomPrometheusRules
metadata:
  name: my-rules
spec:
  groups:
  - name: cluster-state-alert.rules
    rules:
    - alert: TooManyPostRequests
      annotations:
        description: Too many POST requests.
        summary: Too many POST requests.
        plk_markup_format: markdown
      expr: |
        rate(http_requests_total{job="custom-prometheus-example-app", method="post"}[5m]) > 0
EOF
```

Запустим curl и поделаем POST запросы

```
kubectl run curl --rm -ti --image=curlimages/curl -- /bin/sh
```

```
curl -XPOST prometheus-example-app:8080/
```

После чего проверим алерты в кластере либо веб-интерфейс, либо через `kubectl get clusteralerts.deckhouse.io`

```
~ $ kubectl get clusteralerts.deckhouse.io
NAME               ALERT                 SEVERITY   AGE     LAST RECEIVED   STATUS
0563e4ee6d8e7a0d   TooManyPostRequests              4m29s   59s             firing
30ecc868eb05a8b9   TooManyPostRequests              4m59s   59s             firing
9d252db64eed1d56   TooManyPostRequests              4m59s   59s             firing
c0c6eb6aaa5caab3   TooManyPostRequests              4m59s   59s             firing
```

## 48. Возможность отправки уведомлений (alerts) во внешнюю систему

### Webhook

Получим URL webhook https://webhook.site/

Настроим, заменив URL на полученный
```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: CustomAlertmanager
metadata:
  name: mywebhook
spec:
  type: Internal
  internal:
    receivers:
      - name: webhook
        webhookConfigs:
          - httpConfig:
            url: https://webhook.site/6e335f84-3e87-4c93-bf5a-26941dbc3043
    route:
      groupBy:
        - job
      groupInterval: 5m
      groupWait: 30s
      receiver: webhook
      repeatInterval: 12h
EOF
```

И повторим запросы POST из предыдущего шага - получим наши алерты на странице https://webhook.site/#!/view/6e335f84-3e87-4c93-bf5a-26941dbc3043 (Ваша страница, URL для примера)

### Email

Создадим пароль для приложения

Деплоим секрет

```
kubectl create -f -<<EOF
apiVersion: v1
kind: Secret
metadata:
  name: email-secret
  namespace: d8-monitoring
stringData:
  password: "8XRd********91BSg"
EOF
```

И ресурс CustomAlertManager:

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: CustomAlertmanager
metadata:
  name: email
spec:
  type: Internal
  internal:
    receivers:
      - name: email
        emailConfigs:
          - authPassword:
              name: email-secret
              key: password
            authUsername: 'email@mail.ru'
            from: 'email@mail.ru'
            to: 'email@mail.ru'
            smarthost: smtp.mail.ru:465
            requireTLS: false
    route:
      groupBy:
        - job
      groupInterval: 5m
      groupWait: 30s
      receiver: email
      repeatInterval: 12h
EOF
```

### Telegram

Создадим бота согласно инструкции https://core.telegram.org/bots/tutorial#obtain-your-bot-token

Добавим секрет

```
kubectl create -f -<<EOF
apiVersion: v1
kind: Secret
metadata:
  name: telegram-bot-secret
  namespace: d8-monitoring
stringData:
  token: "7306049413:AAE0WhyNu7pYs4De9QotG2EdTwxDBZszK5A"
EOF
```

Создадим группу, в которой будут алерты, добавим туда бота и отправим какое-либо сообщение с упоминанием бота (например `/my_id @dkpalarmer_bot`)

После этого сделаем запрос `https://api.telegram.org/botXXX:YYYY/getUpdates`

```
curl 'https://api.telegram.org/bot7306049413:AAE0WhyNu7pYs4De9QotG2EdTwxDBZszK5A/getUpdates' | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   432  100   432    0     0    187      0  0:00:02  0:00:02 --:--:--   187
{
  "ok": true,
  "result": [
    {
      "update_id": 222160491,
      "message": {
        "message_id": 2,
        "from": {
          "id": 190165913,
          "is_bot": false,
          "first_name": "Dmitrii",
          "last_name": "Batkovich",
          "username": "mycoolusername"
        },
        "chat": {
          "id": -4256581561,
          "title": "TestAlerts",
          "type": "group",
          "all_members_are_administrators": true
        },
        "date": 1723485681,
        "text": "/my_id @dkpalarmer_bot",
        "entities": [
          {
            "offset": 0,
            "length": 6,
            "type": "bot_command"
          },
          {
            "offset": 7,
            "length": 15,
            "type": "mention"
          }
        ]
      }
    }
  ]
}
```

Наш искомый в данном случае chatID `-4256581561`

Задеплоим custom resource CustomAlertManager:

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: CustomAlertmanager
metadata:
  name: telegram
spec:
  type: Internal
  internal:
    receivers:
      - name: telegram
        telegramConfigs:
          - botToken:
              name: telegram-bot-secret
              key: token
            chatID: -4256581561
    route:
      groupBy:
        - job
      groupInterval: 5m
      groupWait: 30s
      receiver: telegram
      repeatInterval: 12h
EOF
```

# Автомасштабирование

## 49. Балансировка нагрузки контейнеров между узлами кластера

Создадим deployment c affinity

```
kubectl create -f -<<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-mainline-deployment
  labels:
    app: nginx-mainline
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-mainline
  template:
    metadata:
      labels:
        app: nginx-mainline
    spec:
      containers:
      - name: nginx-mainline
        image: nginx:mainline-alpine
        ports:
        - containerPort: 80
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: "app"
                operator: In
                values:
                - nginx-mainline
            topologyKey: "kubernetes.io/hostname"
EOF
```

И убедимся, что поды разместились на разных нодах `kubectl get pods -o wide -l app=nginx-mainline`

Пример
```
~ $ kubectl get pods -o wide -l app=nginx-mainline
NAME                                        READY   STATUS    RESTARTS   AGE     IP             NODE                                         NOMINATED NODE   READINESS GATES
nginx-mainline-deployment-c6b788787-gp828   1/1     Running   0          8m39s   10.111.1.189   test2-worker-a3960fea-75fc9-tmjtm   <none>           <none>
nginx-mainline-deployment-c6b788787-s8d7z   1/1     Running   0          8m39s   10.111.2.4     test2-worker-a3960fea-75fc9-6jqgk   <none>           <none>
```

## 50. Масштабирование прикладных сервисов на основе бизнес метрик

Установим rabbitmq-operator https://github.com/rabbitmq/cluster-operator/

```
kubectl apply -f https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml
```

Проверим, что operator задеплоился
```
kubectl -n rabbitmq-system get pods
```

Пример вывода
```
~ $ kubectl -n rabbitmq-system get pods
NAME                                         READY   STATUS    RESTARTS   AGE
rabbitmq-cluster-operator-8457984675-bmzb9   1/1     Running   0          18m
```

Создадим namespace my-hpa-custom-test
```
kubectl create namespace my-hpa-custom-test
```

Задеплоим в него rabbitmq (для сервиса сразу укажем лейблы и аннотации для сбора метрик)
```
kubectl -n my-hpa-custom-test apply -f -<<EOF
apiVersion: rabbitmq.com/v1beta1
kind: RabbitmqCluster
metadata:
  name: my-rabbitmq
spec:
  override:
    service:
      metadata:
        labels:
          prometheus.deckhouse.io/custom-target: my-rabbitmq
        annotations:
          prometheus.deckhouse.io/port: '15692'
EOF
```

Создадим worker, который будет обрабатывать очередь:
Скрипт:
```
kubectl -n my-hpa-custom-test apply -f -<<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-worker-py
data:
  worker.py: |
    #!/usr/bin/env python
    import pika
    import time
    import os

    myhost = os.environ['MY_RABBITMQ_HOST']
    mycredentials = pika.PlainCredentials(os.environ['MY_RABBITMQ_USERNAME'], os.environ['MY_RABBITMQ_PASSWORD'])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=myhost, credentials=mycredentials))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    print(' [*] Worker started. Waiting for messages.')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        timetosleep = body.count(b'.') * 5
        print(f" [x] Will sleep for {timetosleep} seconds")
        time.sleep(timetosleep)
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    channel.start_consuming()
EOF
```

И стартуем deployment worker
```
kubectl -n my-hpa-custom-test apply -f -<<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: my-worker
  annotations:
    pod-reloader.deckhouse.io/auto: "true"
  name: my-worker
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-worker
  template:
    metadata:
      labels:
        app: my-worker
    spec:
      containers:
      - image: python:3.12.6-alpine3.20
        name: python
        command: ["/bin/sh"]
        args: ["-c", "pip install pika==1.3.2; python -u /opt/scripts/worker.py"]
        volumeMounts:
        - name: script-volume
          mountPath: /opt/scripts
        env:
        - name: MY_RABBITMQ_USERNAME
          valueFrom:
            secretKeyRef:
              name: my-rabbitmq-default-user
              key: username
        - name: MY_RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: my-rabbitmq-default-user
              key: password
        - name: MY_RABBITMQ_HOST
          valueFrom:
            secretKeyRef:
              name: my-rabbitmq-default-user
              key: host
      volumes:
      - name: script-volume
        configMap:
          name: my-worker-py
EOF
```

Создадим tasker, который будет наполнять очередь:
Скрипт:
```
kubectl -n my-hpa-custom-test apply -f -<<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-tasker-py
data:
  tasker.py: |
    #!/usr/bin/env python
    import pika
    import sys
    import os
    import random

    myhost = os.environ['MY_RABBITMQ_HOST']
    mycredentials = pika.PlainCredentials(os.environ['MY_RABBITMQ_USERNAME'], os.environ['MY_RABBITMQ_PASSWORD'])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=myhost, credentials=mycredentials))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    for i in range(1,100):
      message=f"This is task №{i} with dots"+"."*random.randrange(1, 10, 1)
      channel.basic_publish(
          exchange='',
          routing_key='task_queue',
          body=message,
          properties=pika.BasicProperties(
              delivery_mode=pika.DeliveryMode.Persistent
          ))
      print(f" [x] Sent {message}")
    connection.close()
EOF
```

И стартуем deployment tasker
```
kubectl -n my-hpa-custom-test apply -f -<<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: my-tasker
  annotations:
    pod-reloader.deckhouse.io/auto: "true"
  name: my-tasker
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-tasker
  template:
    metadata:
      labels:
        app: my-tasker
    spec:
      containers:
      - image: python:3.12.6-alpine3.20
        name: python
        command: ["/bin/sh"]
        args: ["-c", "pip install pika==1.3.2; ls /opt/scripts; python -u /opt/scripts/tasker.py; sleep 1800"]
        volumeMounts:
        - name: script-volume
          mountPath: /opt/scripts
        env:
        - name: MY_RABBITMQ_USERNAME
          valueFrom:
            secretKeyRef:
              name: my-rabbitmq-default-user
              key: username
        - name: MY_RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: my-rabbitmq-default-user
              key: password
        - name: MY_RABBITMQ_HOST
          valueFrom:
            secretKeyRef:
              name: my-rabbitmq-default-user
              key: host
      volumes:
      - name: script-volume
        configMap:
          name: my-tasker-py
EOF
```

Добавляем ServiceMetric (метрика, по которой будем скейлиться):
```
kubectl -n my-hpa-custom-test create -f -<<EOF
apiVersion: deckhouse.io/v1beta1
kind: ServiceMetric
metadata:
  name: rmq-queue-messages
spec:
  query: avg_over_time(rabbitmq_queue_messages{job="custom-my-rabbitmq"}[1m])
EOF
```

И hpa
```
kubectl -n my-hpa-custom-test create -f -<<EOF
kind: HorizontalPodAutoscaler
apiVersion: autoscaling/v2
metadata:
  name: my-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-worker
  minReplicas: 1
  maxReplicas: 15
  metrics:
  - type: Object
    object:
      describedObject:
        apiVersion: v1
        kind: Service
        name: my-rabbitmq
      metric:
        name: rmq-queue-messages
      target:
        type: Value
        value: 30
EOF
```

И начинаем наблюдать за увеличением количества реплик для нашего deployment с помощью конструкций `kubectl -n my-hpa-custom-test get deploy my-worker -w` (также можно наблюдать за количеством подов my-worker `kubectl -n my-hpa-custom-test get pods -w`) и изменением рекомендаций hpa `kubectl -n my-hpa-custom-test get hpa my-hpa -w`

Пример:
```
~ $ kubectl -n my-hpa-custom-test get hpa my-hpa -w
NAME     REFERENCE              TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
my-hpa   Deployment/my-worker   0/30      1         15        1          27m
my-hpa   Deployment/my-worker   49500m/30   1         15        1          27m
my-hpa   Deployment/my-worker   49500m/30   1         15        2          27m
my-hpa   Deployment/my-worker   98500m/30   1         15        4          28m
my-hpa   Deployment/my-worker   98500m/30   1         15        8          28m
my-hpa   Deployment/my-worker   96/30       1         15        15         28m
my-hpa   Deployment/my-worker   89500m/30   1         15        15         29m
my-hpa   Deployment/my-worker   75500m/30   1         15        15         29m
my-hpa   Deployment/my-worker   55/30       1         15        15         29m
my-hpa   Deployment/my-worker   34500m/30   1         15        15         30m
my-hpa   Deployment/my-worker   14500m/30   1         15        15         30m
my-hpa   Deployment/my-worker   2/30        1         15        15         31m
my-hpa   Deployment/my-worker   0/30        1         15        15         31m
my-hpa   Deployment/my-worker   0/30        1         15        15         35m
my-hpa   Deployment/my-worker   0/30        1         15        8          35m
my-hpa   Deployment/my-worker   0/30        1         15        8          36m
my-hpa   Deployment/my-worker   0/30        1         15        1          36m
my-hpa   Deployment/my-worker   0/30        1         15        1          36m
```

## 51. Масштабирование прикладных сервисов на основе потребления ресурсов

Применим следующие манифесты

```
kubectl create -f -<<EOF
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: keydb-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: keydb
  updatePolicy:
    updateMode: "Initial"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keydb
  labels:
    app: keydb
spec:
  selector:
    matchLabels:
      app: keydb
  replicas: 1
  template:
    metadata:
      labels:
        app: keydb
    spec:
      containers:
        - name: keydb
          image: eqalpha/keydb:x86_64_v6.3.4
          resources:
            requests:
              cpu: 100m
              memory: 100Mi
          ports:
            - containerPort: 6379
EOF
```

Получим состояние VPA

```
kubectl get vpa keydb-vpa
NAME        MODE      CPU   MEM        PROVIDED   AGE
keydb-vpa   Initial   25m   52428800   True       72s
```

Через `kubectl get vpa keydb-vpa -o yaml` подробнее можно ознакомиться с рекомендациями

VPA предлагает уменьшить ресурсы

В режиме "Initial" — VPA изменяет ресурсы подов только при создании подов, но не во время работы.

Проверим реквесты пода, перезапустим и снова проверим

```
~ $ kubectl get pods -l app=keydb -o yaml | grep requests -A 2
        requests:
          cpu: 100m
          memory: 100Mi
~ $ kubectl rollout restart deployment keydb
deployment.apps/keydb restarted
~ $ kubectl get pods -l app=keydb -o yaml | grep requests -A 2
        requests:
          cpu: 25m
          memory: "52428800"
```

Выведем сервис
```
kubectl expose deployment keydb --port 6379
```

И подадим нагрузку
```
kubectl run --rm -ti alpine --image alpine -- /bin/sh -c 'apk add redis && redis-benchmark -h keydb --threads 20 -c 80 -r 10000000 -n 10000000 lpush mylist __rand_int__'
```

Снова проверим VPA
```
~ $ kubectl get vpa keydb-vpa
NAME        MODE      CPU     MEM         PROVIDED   AGE
keydb-vpa   Initial   1168m   225384266   True       41m
```

Проверим реквесты пода, перезапустим и снова проверим
```
~ $ kubectl get pods -l app=keydb -o yaml | grep requests -A 2
        requests:
          cpu: 25m
          memory: "52428800"
~ $ kubectl rollout restart deployment keydb
deployment.apps/keydb restarted
~ $ kubectl get pods -l app=keydb -o yaml | grep requests -A 2
        requests:
          cpu: 1168m
          memory: "248153480"
```

## 52. Автоматические масштабирование количества узлов кластера

Выкатить deployment с суммарными реквестами по CPU / RAM больше, чем доступно на текущих узлах, через 10 минут зафиксировать автоматический заказ и добавление нового узла

Либо выкатить деплоймент с affinity, например из шага ## 49. Балансировка нагрузки контейнеров между узлами кластера

## 53. Автоматические распределение ресурсов между узлами кластера

Добавим стратегию по вытеснению подов, которые нарушают Taints ноды

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: Descheduler
metadata:
  name: evict-from-cordon
spec:
  deschedulerPolicy:
    strategies:
      removePodsViolatingNodeTaints:
        enabled: true
EOF
```

Закордоним узел

```
kubectl cordon WORKER_NODE
```

И пронаблюдаем, как поды на данной ноде будут вытеснены на другие

# Разное

## 54. Встроенная возможность автоматического распространения secrets

Создаём секрет и ставим на него лейбл

```
kubectl create secret generic my-secret --from-literal=key1=supersecret --from-literal=key2=topsecret
kubectl label secrets my-secret secret-copier.deckhouse.io/enabled=""
```

Проверяем, что секрет появился в каком либо другом неймспейсе, например в `d8-system`: `kubectl -n d8-system get secrets my-secret`

```
~ $ kubectl -n d8-system get secrets my-secret
NAME        TYPE     DATA   AGE
my-secret   Opaque   2      66s
```

## 55. Автоматический перезапуск прикладного ПО в случае изменения secret / configmap

Создадим namespace test-pd

```
kubectl create namespace test-pd
```

Создадим secret

```
kubectl -n test-pd create secret generic alpine-secret-value --from-literal=extra=supersecret
```

Добавим deployment

```
kubectl -n test-pd create -f -<<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alpine-deployment
  labels:
    app: alpine-deployment
  annotations:
    pod-reloader.deckhouse.io/auto: "true"
spec:
  selector:
    matchLabels:
      app: alpine-deployment
  template:
    metadata:
      labels:
        app: alpine-deployment
    spec:
      containers:
        - name: alpine-deployment
          image: alpine
          command:
          - /bin/sh
          - "-c"
          - "sleep 60m"
          env:
            - name: SECRET_WORD
              valueFrom:
                secretKeyRef:
                  name: alpine-secret-value
                  key: extra
EOF
```

Получим переменную `SECRET_WORD` из контейнера

```
kubectl -n test-pd exec -ti $(kubectl -n test-pd get pods -l app=alpine-deployment --no-headers | cut -d' ' -f1) -- /bin/sh -c 'export' | grep SECRET_WORD
```

В выводе увидим `export SECRET_WORD='supersecret'`

Произведём изменение секрета

```
kubectl -n test-pd get secrets alpine-secret-value -o json | jq --arg myvalue "$(echo -n NEWsupersecret | base64)" '.data["extra"]=$myvalue' | kubectl apply -f -
```

Увидим, что под был перезапущен
```
~ $ kubectl -n test-pd get pods
NAME                                 READY   STATUS    RESTARTS   AGE
alpine-deployment-5dfc455f66-gkhdv   1/1     Running   0          44s
```

Получим переменную `SECRET_WORD` из контейнера

```
kubectl -n test-pd exec -ti $(kubectl -n test-pd get pods -l app=alpine-deployment --no-headers | cut -d' ' -f1) -- /bin/sh -c 'export' | grep SECRET_WORD
```

В выводе увидим `export SECRET_WORD='NEWsupersecret'`

## 56. Настройка входящего трафика для кластера (Ingress)

Применим манифест

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1
kind: IngressNginxController
metadata:
  name: main
spec:
  ingressClass: nginx
  inlet: HostPort
  hostPort:
    httpPort: 80
    httpsPort: 443
    behindL7Proxy: true
EOF
```

Убедимся, что появились поды контроллера

```
kubectl -n d8-ingress-nginx get pods -l app=controller
```

Проверить запросом из вне

## 57. Встроенные инструменты удаленного ведения и агрегации журналов (логов)

Включим модуль

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: log-shipper
spec:
  version: 1
  enabled: true
EOF
```

Настроим удалённое хранилище
```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ClusterLogDestination
metadata:
  name: es-storage
spec:
  type: Elasticsearch
  elasticsearch:
    endpoint: http://192.168.1.1:9200
    index: logs-%F
    auth:
      strategy: Basic
      user: elastic
      password: c2VjcmV0IC1uCg==
EOF
```

Настроим отправку логов из namespace 
```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ClusterLoggingConfig
metadata:
  name: nginx-test-istio-logs
spec:
  type: KubernetesPods
  kubernetesPods:
    namespaceSelector:
      matchNames:
        - test-istio
    labelSelector:
      matchLabels:
        app: nginx
  destinationRefs:
  - es-storage
EOF
```

## 58. Встроенная система кратковременного хранения логов

Включим модуль

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: loki
spec:
  version: 1
  enabled: true
EOF
```

Убедимся, что под поднялся
```
kubectl -n d8-monitoring get pods -l app=loki
```

Автоматически будет добавлен ClusterLogDestination `d8-loki` и ClusterLoggingConfig `d8-namespaces-to-loki`, который собирает логи с системных namespace

Перейдем в https://grafana.DOMAIN.TLD/explore выберем DataSource `d8-loki` и введём запрос логов пода Deckhouse `{pod="deckhouse-7c55fc76dd-ctxb2"}`

## 59. Доступ к кластеру через OpenVPN

Включаем и настраиваем модуль

```
kubectl create -f -<<EOF
apiVersion: deckhouse.io/v1alpha1
kind: ModuleConfig
metadata:
  name: openvpn
spec:
  version: 2
  enabled: true
  settings:
    externalHost: 51.250.89.240
    inlet: HostPort
    nodeSelector:
      node-role.kubernetes.io/control-plane: ""
    tolerations:
    - operator: Exists
EOF
```

Перейти в админку https://openvpn-admin.DOMAIN.TLD/ создать пользователя, скачать конфиг, подключиться и пропинговать под/сервис
