FROM quay.io/keycloak/keycloak:21.0.2 as builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

ENV KC_HTTP_ENABLED=true

# Configure a database vendor
ENV KC_DB=postgres
ENV KC_HOSTNAME_STRICT=true

ENV KC_FEATURES=authorization,token-exchange,docker,upload-scripts,impersonation,web-authn,client-policies
# dynamic-scopes,

COPY keycloak-metrics-spi-3.0.0.jar /opt/keycloak/providers/

WORKDIR /opt/keycloak
# for demonstration purposes only, please make sure to use proper certificates in production instead
#RUN keytool -genkeypair -storepass password -days 3650 -storetype PKCS12 -keyalg RSA -keysize 2048 -dname "CN=dev-kc.sz.rshbcloud.ru" -alias server -ext "SAN:c=DNS:localhost,IP:127.0.0.1" -keystore conf/server.keystore

RUN /opt/keycloak/bin/kc.sh build
RUN /opt/keycloak/bin/kc.sh show-config

FROM quay.io/keycloak/keycloak:21.0.2
COPY --from=builder /opt/keycloak/ /opt/keycloak/
COPY keycloak-metrics-spi-3.0.0.jar /opt/keycloak/providers/

# change these values to point to a running postgres instance
ENV KC_DB=postgres
ENV KC_DB_URL=jdbc:postgresql://10.80:5432/kcdb
ENV KC_DB_USERNAME=kcuser
ENV KC_DB_PASSWORD=Dfret45dferet
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
