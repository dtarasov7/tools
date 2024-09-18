docker run --rm --add-host="gitlab.rshbcloud.ru:178.57" \
  -v gitlab_gitlab_runner:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:alpine register \
  --non-interactive \
  --executor "docker" \
  --docker-image alpine:latest \
  --url "https://gitlab.rshbcloud.ru/" \
  --registration-token "3ipbufqK1" \
  --description "docker-runner-pub-dtln" \
  --locked="false" \
  --docker-extra-hosts="gitlab.rshbcloud.ru:178.57" \
  --env "GIT_SSL_NO_VERIFY=true" \
  --docker-privileged \
  --tag-list "pubdtln" \
  --run-untagged="false" \
  --shell bash
