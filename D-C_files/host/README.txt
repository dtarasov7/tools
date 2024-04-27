1) заполнить файл с переменными .env

2)создать подкаталоги:
nodeExporter
processExporter
cadvisor

3) в каталоге nodeExporter находится web-config.yml (basic auth для node-exporter), структура файла:

basic_auth_users:
  <basic_auth_user>: <basic_auth_passwd>
  
где <basic_auth_user> - пользователь,
<basic_auth_passwd> - зашифрованный пароль (Bcrypt encrypte hash), можно воспользоваться данным ресурсом https://bcrypt-generator.com/

В нем уже указаны данные необходимые для авторизации vmagent для сбора метрик.

4) в каталоге processExporter создать файл process-exporter.yml, в файле указать процессы необходимые для мониторинга, примерный файл с базовыми процессами:

process_names:
  - name: "{{.Comm}}"
    comm:
    - httpd
    - java
    - systemd
    - named-pkcs11
    - rsyslogd
    - ns-slapd
    - sudo
    - su
    - containerd
    - containerd-shim
    - sssd_nss
    - sssd_be
    - dockerd
    - docker-containe
    - docker-proxy
    - systemd-journal
    - bash
    - sshd
    - node
    - vmagent-prod
    - blackbox_exporter
    - cadvisor
    - filebeat
    - beat-exporter
    - node_exporter
    - process-exporter

например, если необходимо добавить в отдельную группу некий java-процесс, то в конце файла добавить секцию и удалить '- java' из секции 'name: "{{.Comm}}"'
  - name: 'название'
    cmdline:
    - '.*уникальная_подстрока_в_команде_запуска_java-процесса.*'
	
5) в каталоге cadvisor создать файл web.htpasswd, в нем описан логин/пароль от basic auth для доступа на ui cadvisor, содржимое файла (пароль зашифрован):

cadvisor:$apr1$wq9fcObZ$hdpbt0qEVOI0owSs5RQT31 