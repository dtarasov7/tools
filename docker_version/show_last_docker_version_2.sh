#!/bin/bash
#image="aquasec/trivy"
#set -x
tags=$(curl -s -L --fail "https://registry.hub.docker.com/v1/repositories/$1/tags" | jq ' .[] | .name' -r | sed 's/latest//' | grep -E '.*[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+.*'| grep -v arm| sort --version-sort | tail -n 2)
echo "$tags"
