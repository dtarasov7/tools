#!/bin/bash
set -e

#psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    create database "$KC_DB";
    create user "$KC_USER" with encrypted password  '$KC_PASSWORD';
    grant all privileges on database "$KC_DB" to "$KC_USER";
EOSQL