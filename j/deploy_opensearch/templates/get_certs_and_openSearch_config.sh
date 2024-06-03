#!/bin/bash

ODFE_CONTAINER_NAME=odfe-node
ODFE_CERTS_DIR=/opt/ans_odfe_deploy/certs
NFS_DIR=/opt/nfs-client-odfe3
DOCKER_VOLUMES=/mnt/prod-odfe03
ODFE_HOST=$(hostname --short)

# Копируем конфиг файлы плагина opendistro_security
if [ ! -d "$NFS_DIR/opendistro_security_config" ]; then
mkdir $NFS_DIR/opendistro_security_config
fi

docker exec $ODFE_CONTAINER_NAME /bin/sh /usr/share/elasticsearch/plugins/opendistro_security/tools/securityadmin.sh -backup $DOCKER_VOLUMES/opendistro_security_config -icl -nhnv -cacert /usr/share/elasticsearch/config/root-ca.pem -cert /usr/share/elasticsearch/config/admin.pem -key /usr/share/elasticsearch/config/admin.key > /dev/null

# Копируем сертификаты
if [ ! -d "$NFS_DIR/certs" ]; then
mkdir -p $NFS_DIR/certs/$ODFE_HOST
fi

rsync -am --include='*.key' --include='*.pem' --exclude='*' $ODFE_CERTS_DIR/ $NFS_DIR/certs/$ODFE_HOST/
