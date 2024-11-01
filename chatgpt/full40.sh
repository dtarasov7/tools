��� ��������� bash-������, ������� ������ yaml-����, �������� ������������ Grafana � ������������ � ����������� � ����� � �������� ��� �������� � ������:

```bash
#!/bin/bash

# ���� � ����� � ������������� � ����� ��� �������� API ������
CONFIG_FILE="grafana_config.yaml"
API_KEYS_FILE="api_keys.yaml"
LOG_FILE="grafana_sync.log"

# ������� ��� �����������
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# �������� ������� yq � curl
if ! command -v yq &> /dev/null || ! command -v curl &> /dev/null; then
    log "yq or curl is not installed. Please install them first."
    exit 1
fi

# �������� �������� ��������� �� Grafana
current_orgs=$(curl -s -H "Authorization: Bearer $GRAFANA_API_TOKEN" -H "Content-Type: application/json" "$GRAFANA_URL/api/orgs")
if [[ $? -ne 0 ]]; then
    log "Failed to fetch current organizations from Grafana."
    exit 1
fi

# ������� ��� ��������� API ����� �����������
get_org_api_key() {
    local org_name="$1"
    local org_id="$2"

    local key=$(yq e ".api_keys[] | select(.name == \"$org_name\") | .key" "$API_KEYS_FILE")
    if [[ -z "$key" ]]; then
        # �������� ������ API �����
        local response=$(curl -s -H "Authorization: Bearer $GRAFANA_API_TOKEN" -H "Content-Type: application/json" \
            -X POST "$GRAFANA_URL/api/auth/keys" -d "{\"name\":\"orgapikey\",\"role\":\"Admin\",\"orgId\":$org_id}")
        key=$(echo "$response" | jq -r '.key')
        if [[ $? -ne 0 || "$key" == "null" ]]; then
            log "Failed to create API key for organization $org_name."
            exit 1
        fi

        # ���������� ������ API �����
        yq e -i ".api_keys += [{\"name\": \"$org_name\", \"id\": $org_id, \"key_name\": \"orgapikey\", \"key\": \"$key\"}]" "$API_KEYS_FILE"
        log "API key created and saved for organization $org_name."
    fi

    echo "$key"
}

# ������� ��� �������� ��� ���������� �����������
create_or_update_org() {
    local org_name="$1"

    # �������� ������� �����������
    local org_id=$(echo "$current_orgs" | jq ".[] | select(.name == \"$org_name\") | .id")

    if [[ -z "$org_id" ]]; then
        # �������� �����������
        local response=$(curl -s -H "Authorization: Bearer $GRAFANA_API_TOKEN" -H "Content-Type: application/json" \
            -X POST "$GRAFANA_URL/api/orgs" -d "{\"name\": \"$org_name\"}")
        org_id=$(echo "$response" | jq -r '.orgId')
        if [[ $? -ne 0 || "$org_id" == "null" ]]; then
            log "Failed to create organization $org_name."
            exit 1
        fi
        log "Organization $org_name created with ID $org_id."
    else
        log "Organization $org_name already exists with ID $org_id."
    fi

    echo "$org_id"
}

# ������� ��� ������������� ������
sync_grafana() {
    local orgs=$(yq e '.organizations' "$CONFIG_FILE")

    for org in $(echo "$orgs" | jq -c '.[]'); do
        local org_name=$(echo "$org" | jq -r '.name')
        local org_id=$(create_or_update_org "$org_name")

        # ��������� API ����� ��� �����������
        local api_key=$(get_org_api_key "$org_name" "$org_id")

        # ������������� ���������� ������
        local datasources=$(echo "$org" | jq -c '.datasources[]?')
        for datasource in $datasources; do
            local ds_name=$(echo "$datasource" | jq -r '.name')
            local ds_path=$(echo "$datasource" | jq -r '.path')

            # �������� ��� ���������� ��������� ������
            curl -s -H "Authorization: Bearer $api_key" -H "Content-Type: application/json" \
                -X POST "$GRAFANA_URL/api/datasources" -d "{\"name\": \"$ds_name\", \"url\": \"$ds_path\"}" &> /dev/null
            if [[ $? -ne 0 ]]; then
                log "Failed to create/update datasource $ds_name in organization $org_name."
                exit 1
            fi
            log "Datasource $ds_name created/updated in organization $org_name."
        done

        # ������������� �������������
        local users=$(echo "$org" | jq -c '.users[]?')
        for user in $users; do
            local user_name=$(echo "$user" | jq -r '.name')
            local user_role=$(echo "$user" | jq -r '.role')

            # �������� ��� ���������� ������������
            curl -s -H "Authorization: Bearer $GRAFANA_API_TOKEN" -H "Content-Type: application/json" \
                -X POST "$GRAFANA_URL/api/orgs/$org_id/users" -d "{\"loginOrEmail\": \"$user_name\", \"role\": \"$user_role\"}" &> /dev/null
            if [[ $? -ne 0 ]]; then
                log "Failed to create/update user $user_name in organization $org_name."
                exit 1
            fi
            log "User $user_name with role $user_role created/updated in organization $org_name."
        done

        # ������������� ���������
        local dashboard_groups=$(echo "$org" | jq -c '.dashboard_groups[]?')
        for group in $dashboard_groups; do
            local dashboards=$(echo "$group" | jq -c '.dashboards[]?')
            for dashboard in $dashboards; do
                local dashboard_file=$(echo "$dashboard" | jq -r '.file')

                # �������� ���������
                for file in $(ls $dashboard_file); do
                    dashboard_json=$(cat "$file")
                    curl -s -H "Authorization: Bearer $api_key" -H "Content-Type: application/json" \
                        -X POST "$GRAFANA_URL/api/dashboards/db" -d "$dashboard_json" &> /dev/null
                    if [[ $? -ne 0 ]]; then
                        log "Failed to upload dashboard $file in organization $org_name."
                        exit 1
                    fi
                    log "Dashboard $file uploaded in organization $org_name."
                done
            done
        done
    done
}

sync_grafana
log "Grafana synchronization completed."
```

���� ������ ��������� ��������� ����:

1. ������ yaml-���� � ������� yq.
2. ������� �����������, ��������� ������ � ������������� � Grafana.
3. ��������� �������� � ��������� �����������.
4. �������� ��� �������� � ������.
5. ���������� API Grafana ��� �������� � ���������� ��������.

���������, ��� � ��� ����������� ����������� ����������� (`yq`, `jq`, `curl`) � ��������� ��������� ���������� `GRAFANA_API_TOKEN` � `GRAFANA_URL`.