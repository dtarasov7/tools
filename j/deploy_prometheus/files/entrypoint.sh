#!/bin/sh
set -e

cmd="$@"

>&2 echo "!!!!!!!! Check consul for available !!!!!!!!"

until curl -s -G $CONSUL_URL:8500/v1/health/node/$CONSUL_NODE --data-urlencode 'filter=CheckID == "serfHealth"' | grep -o "passing"; do
  >&2 echo "Waiting consul"
  sleep 1
done

>&2 echo "Consul is up - executing command"

exec $cmd
