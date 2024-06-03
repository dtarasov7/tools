#!/bin/sh
filename='/consul/services.json'
if [ -n "$CONSUL_HTTP_TOKEN" ]; then
while IFS= read -r line
do
curl -s -X PUT -d "$line" "$CONSUL_URL:8500/v1/agent/service/register?token=$CONSUL_HTTP_TOKEN"
echo "Service added: $line"
done < $filename
else
while IFS= read -r line
do
curl -s -X PUT -d "$line" "$CONSUL_URL:8500/v1/agent/service/register"
echo "Service added: $line"
done < $filename
fi
