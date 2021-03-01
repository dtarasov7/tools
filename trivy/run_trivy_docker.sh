#!/bin/bash
VER=$(curl -s -L --fail "https://hub.docker.com/v2/repositories/aquasec/trivy/tags/?page_size=1000" | jq '.results | .[] | .name' -r | sed 's/latest//' | sort --version-sort | tail -n 1)
echo $VER
set -x
docker run --rm -v $(pwd)/.trivyignore:/root/.trivyignore -v $(pwd)/db:/root/.cache/ -v /var/run/docker.sock:/var/run/docker.sock:ro aquasec/trivy:$VER --ignorefile /root/.trivyignore "$@"
set +x