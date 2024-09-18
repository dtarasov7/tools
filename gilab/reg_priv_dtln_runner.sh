docker run --rm --add-host="gitlab.rshbcloud.ru:178.57.9" \
  -v gitlab_gitlab_runner_priv:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:alpine register \
  --non-interactive \
  --executor "docker" \
  --docker-image alpine:latest \
  --url "https://gitlab.rshbcloud.ru/" \
  --registration-token "3ipbo2" \
  --description "docker-runner-priv" \
  --locked="false" \
  --docker-extra-hosts="gitlab.rshbcloud.ru:178.57." \
  --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
  --env "GIT_SSL_NO_VERIFY=true" \
  --docker-privileged \
  --tag-list "dtln_priv" \
  --run-untagged="false" \
  --shell bash
