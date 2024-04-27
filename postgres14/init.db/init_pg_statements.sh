#!/bin/bash
set -e

#psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    create user "$DB_USER" with encrypted password  '$DB_PASSWORD';
    create database "$DB" with owner  "$DB_USER";
    grant all privileges on database "$DB" to "$DB_USER";
    alter schema public owner to "$DB_USER";
EOSQL