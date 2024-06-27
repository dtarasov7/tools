��� ���������� �������� ������������� � ����������� � Grafana, ������������ ������ ��������� �������:

1. ������� ������� ��� �������� �������������.
2. ������ ��������� � �������� ����� ������� ��� ��������� ������� `users` � ���������������� �����.

### ����������� ������:

```bash
#!/bin/bash

# ������� ������ �������������� Grafana
GRAFANA_URL="http://localhost:3000"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin_password"

# ������� ��� ��������� ����������� ������
get_session_token() {
  local response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"user\":\"$ADMIN_USER\", \"password\":\"$ADMIN_PASSWORD\"}" \
    "$GRAFANA_URL/api/auth/login")

  echo $(echo $response | jq -r '.token')
}

# ������� ��� �������� �����������
create_organization() {
  local org_name=$1
  curl -s -X POST -H "Content-Type: application/json" -d "{\"name\":\"$org_name\"}" "$GRAFANA_URL/api/orgs" -H "Authorization: Bearer $SESSION_TOKEN"
}

# ������� ��� ��������� ID ����������� �� �����
get_organization_id() {
  local org_name=$1
  curl -s -H "Authorization: Bearer $SESSION_TOKEN" "$GRAFANA_URL/api/orgs" | jq -r ".[] | select(.name==\"$org_name\") | .id"
}

# ������� ��� �������� ��������� ������
create_datasource() {
  local org_id=$1
  local datasource_name=$2
  local datasource_url=$3
  curl -s -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $SESSION_TOKEN" \
    -H "X-Grafana-Org-Id: $org_id" \
    -d "{\"name\":\"$datasource_name\",\"type\":\"prometheus\",\"url\":\"$datasource_url\",\"access\":\"proxy\",\"isDefault\":false}" \
    "$GRAFANA_URL/api/datasources"
}

# ������� ��� �������� API-�����
create_api_key() {
  local org_id=$1
  local api_key_name=$2
  local api_key_role=$3
  local response=$(curl -s -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $SESSION_TOKEN" \
    -H "X-Grafana-Org-Id: $org_id" \
    -d "{\"name\":\"$api_key_name\", \"role\":\"$api_key_role\"}" \
    "$GRAFANA_URL/api/auth/keys")

  echo $(echo $response | jq -r '.key')
}

# ������� ��� �������� ������������
create_user() {
  local org_id=$1
  local user_name=$2
  local user_role=$3
  curl -s -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $SESSION_TOKEN" \
    -H "X-Grafana-Org-Id: $org_id" \
    -d "{\"name\":\"$user_name\", \"email\":\"$user_name@example.com\", \"login\":\"$user_name\", \"password\":\"password\", \"role\":\"$user_role\"}" \
    "$GRAFANA_URL/api/org/users"
}

# �������� ����� �������
yaml_file=$1

if [[ ! -f $yaml_file ]]; then
  echo "YAML ���� �� ������!"
  exit 1
fi

# ��������� ����������� ������
SESSION_TOKEN=$(get_session_token)
if [[ -z $SESSION_TOKEN ]]; then
  echo "�� ������� �������� ���������� �����!"
  exit 1
fi

# ������ ����������� � ���������� ������ �� YAML-�����
organizations=$(yq e '.organizations' $yaml_file)
api_keys_file="api_keys.txt"
> $api_keys_file

for org in $(echo "$organizations" | yq e '.[] | @base64' -); do
  _jq() {
    echo ${org} | base64 --decode | jq -r ${1}
  }

  org_name=$(_jq '.name')
  echo "�������� �����������: $org_name"
  create_organization "$org_name"

  org_id=$(get_organization_id "$org_name")
  datasources=$(_jq '.datasources')

  for ds in $(echo "$datasources" | jq -r '.[] | @base64'); do
    _jq_ds() {
      echo ${ds} | base64 --decode | jq -r ${1}
    }

    ds_name=$(_jq_ds '.name')
    ds_path=$(_jq_ds '.path')
    echo "  �������� ��������� ������: $ds_name � URL: $ds_path"
    create_datasource "$org_id" "$ds_name" "$ds_path"
  done

  users=$(_jq '.users')
  for user in $(echo "$users" | jq -r '.[] | @base64'); do
    _jq_user() {
      echo ${user} | base64 --decode | jq -r ${1}
    }

    user_name=$(_jq_user '.name')
    user_role=$(_jq_user '.role')
    echo "  �������� ������������: $user_name � �����: $user_role"
    create_user "$org_id" "$user_name" "$user_role"
  done

  api_key=$(create_api_key "$org_id" "$org_name-api-key" "Admin")
  echo "API Key ��� ����������� $org_name: $api_key"
  echo "$org_name: $api_key" >> $api_keys_file
done

echo "��� API ����� ��������� � $api_keys_file"
```

### ��������� ����������� ������

��� ������ ����� ������� ���������� ���������� `jq` � `yq`. ���������� �� ��������� �������:

```bash
# ��� jq
sudo apt-get install jq  # ��� Debian/Ubuntu
sudo yum install jq      # ��� CentOS/RHEL
brew install jq          # ��� macOS

# ��� yq
sudo wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
sudo chmod +x /usr/local/bin/yq
```

### ������ ��������

�������� ���� ������� ����������� � ��������� ���, ������ ���� � ������ YAML-�����:

```bash
chmod +x setup_grafana.sh
./setup_grafana.sh path/to/your_config.yaml
```

���� ������ ��������� �������������� � �������������� ����� ������������ � ������, ������� ����������� � ��������� ������, ������� �������������, ���������� API-����� � ��������� �� � ���� `api_keys.txt`.
