set -x
curl -s -d 'client_id=myclient' -d 'username=myuser' -d 'password=password' -d 'grant_type=password' \
    'http://10.80.:8080/realms/myrealm/protocol/openid-connect/login' | jq .
set +x
