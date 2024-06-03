FROM debian:9.13-slim

CMD ["bash"]

ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    wget \
    lsb-core \
    gnupg \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN echo "deb [arch=amd64] https://repo.postgrespro.ru/pg_probackup/deb/ $(lsb_release -cs) main-$(lsb_release -cs)" > /etc/apt/sources.list.d/pg_probackup.list && \
    wget -qO - https://repo.postgrespro.ru/pg_probackup/keys/GPG-KEY-PG_PROBACKUP | apt-key add - && \
    apt-get update -qq && \
    apt-get install -y pg-probackup-12 && \
#    apt-get install -y pg-probackup-12-dbg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY backup.sh /usr/local/bin

RUN chmod +x /usr/local/bin/*.sh

ENTRYPOINT ["/usr/local/bin/backup.sh"]
