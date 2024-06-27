Для добавления создания пользователей в организации в Grafana, модифицируем скрипт следующим образом:

1. Добавим функцию для создания пользователей.
2. Внесем изменения в основную часть скрипта для обработки раздела `users` в конфигурационном файле.

### Обновленный скрипт:

```bash
#!/bin/bash

# Учетные данные администратора Grafana
GRAFANA_URL="http://localhost:3000"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin_password"

# Функция для получения сессионного токена
get_session_token() {
  local response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"user\":\"$ADMIN_USER\", \"password\":\"$ADMIN_PASSWORD\"}" \
    "$GRAFANA_URL/api/auth/login")

  echo $(echo $response | jq -r '.token')
}

# Функция для создания организации
create_organization() {
  local org_name=$1
  curl -s -X POST -H "Content-Type: application/json" -d "{\"name\":\"$org_name\"}" "$GRAFANA_URL/api/orgs" -H "Authorization: Bearer $SESSION_TOKEN"
}

# Функция для получения ID организации по имени
get_organization_id() {
  local org_name=$1
  curl -s -H "Authorization: Bearer $SESSION_TOKEN" "$GRAFANA_URL/api/orgs" | jq -r ".[] | select(.name==\"$org_name\") | .id"
}

# Функция для создания источника данных
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

# Функция для создания API-ключа
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

# Функция для создания пользователя
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

# Основная часть скрипта
yaml_file=$1

if [[ ! -f $yaml_file ]]; then
  echo "YAML файл не найден!"
  exit 1
fi

# Получение сессионного токена
SESSION_TOKEN=$(get_session_token)
if [[ -z $SESSION_TOKEN ]]; then
  echo "Не удалось получить сессионный токен!"
  exit 1
fi

# Чтение организаций и источников данных из YAML-файла
organizations=$(yq e '.organizations' $yaml_file)
api_keys_file="api_keys.txt"
> $api_keys_file

for org in $(echo "$organizations" | yq e '.[] | @base64' -); do
  _jq() {
    echo ${org} | base64 --decode | jq -r ${1}
  }

  org_name=$(_jq '.name')
  echo "Создание организации: $org_name"
  create_organization "$org_name"

  org_id=$(get_organization_id "$org_name")
  datasources=$(_jq '.datasources')

  for ds in $(echo "$datasources" | jq -r '.[] | @base64'); do
    _jq_ds() {
      echo ${ds} | base64 --decode | jq -r ${1}
    }

    ds_name=$(_jq_ds '.name')
    ds_path=$(_jq_ds '.path')
    echo "  Создание источника данных: $ds_name с URL: $ds_path"
    create_datasource "$org_id" "$ds_name" "$ds_path"
  done

  users=$(_jq '.users')
  for user in $(echo "$users" | jq -r '.[] | @base64'); do
    _jq_user() {
      echo ${user} | base64 --decode | jq -r ${1}
    }

    user_name=$(_jq_user '.name')
    user_role=$(_jq_user '.role')
    echo "  Создание пользователя: $user_name с ролью: $user_role"
    create_user "$org_id" "$user_name" "$user_role"
  done

  api_key=$(create_api_key "$org_id" "$org_name-api-key" "Admin")
  echo "API Key для организации $org_name: $api_key"
  echo "$org_name: $api_key" >> $api_keys_file
done

echo "Все API ключи сохранены в $api_keys_file"
```

### Установка необходимых утилит

Для работы этого скрипта необходимо установить `jq` и `yq`. Установите их следующим образом:

```bash
# Для jq
sudo apt-get install jq  # для Debian/Ubuntu
sudo yum install jq      # для CentOS/RHEL
brew install jq          # для macOS

# Для yq
sudo wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
sudo chmod +x /usr/local/bin/yq
```

### Запуск сценария

Сделайте файл скрипта исполняемым и запустите его, указав путь к вашему YAML-файлу:

```bash
chmod +x setup_grafana.sh
./setup_grafana.sh path/to/your_config.yaml
```

Этот скрипт выполняет аутентификацию с использованием имени пользователя и пароля, создает организации и источники данных, создает пользователей, генерирует API-ключи и сохраняет их в файл `api_keys.txt`.
