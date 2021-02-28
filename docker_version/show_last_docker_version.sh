#!/bin/bash
#image="aquasec/trivy"
#set -x
tags=$(curl -s -L --fail "https://hub.docker.com/v2/repositories/$1/tags/?page_size=1000" | jq '.results | .[] | .name' -r | sed 's/latest//' | grep -E '.*[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+.*'| grep -v arm| sort --version-sort | tail -n 2)
echo "$tags"
