#!/usr/bin/env python

from grafana_api.grafana_face import GrafanaFace
import json
import os
import shutil
import requests
import time
import glob

api_list = ["eyJrIjoiN1QzVkFTOVpxcnByS3BpcWZJWGViT3JKMU9nNlJDR08iLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjF9" "eyJrIjoiOTBUTExDYXJSZzZqOEY5TXhyZHdYMndUY091azF2SlQiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjJ9" "eyJrIjoiRmpxaEs2dEozSkR6a3VnMDNobWE0VUZTZzBqMG5tNFUiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjR9" "eyJrIjoiR1pGWGxxUERXN2VXVGZHT1hCZVdrb1dTc0R1WlI4RXYiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjN9" "eyJrIjoiV0dPclV5QlNrb1QzdUxHTGhEaEc3aDNhaENpT1liSWUiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjV9" "eyJrIjoiQjVnQTdUN3BSUjcwaDJ5MnZBMEJXaEFVS1FESzVlRlciLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjZ9" "eyJrIjoiVUZxeE96ZnJWNklpT2RkOGsxbWV3WWUzZnRJdG5KN1UiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjh9" "eyJrIjoiS2hPY2tpUVFjc3hNMEFlQWhWQU5WOHkzRlZFc1RUcGEiLCJuIjoiZXhwb3J0X2ltcG9ydF9kYXNoYm9hcmRzIiwiaWQiOjd9"]
grafana_location = "10.80.252.20:3000"
backup_dir = "/data/minio/grafana/prod_dtln"
zip_date = time.strftime("%Y-%m-%d-%H:%M")

for org_api in api_list:
    grafana_api = GrafanaFace(
            auth = f"{org_api}",
            host = f'{grafana_location}'
            )
    try:
# определяем имя организации, если {org_api} не верный, то пропускаем
        get_current_organization = grafana_api.organization.get_current_organization()
        dumps_current_organization = json.dumps(get_current_organization)
        loads_current_organization = json.loads(dumps_current_organization)
        org_name = (loads_current_organization["name"].replace(' ', '_').replace('/', '_').replace(':', '').replace('[', '').replace(']', '').replace('.', ''))
        print(f"=== Org name '{org_name}' ===")
    except:
        print(f"=== API key '{org_api}' is wrong! ===")
        continue
# если каталог {org_name} существует, то архивируем его в формате {org_name}-{zip_date}.zip
    if os.path.exists(os.path.join(backup_dir, org_name)) and os.path.isdir(os.path.join(backup_dir, org_name)):
        archive_dir = f"{backup_dir}/{org_name}"
        shutil.make_archive(f"{backup_dir}/{org_name}-{zip_date}", 'zip', archive_dir)
# определяем список дашбордов в организации {org_name}
    dashboard_uid = grafana_api.search.search_dashboards()
    #print(dashboard_uid)
    dumps_dashboard_uid = json.dumps(dashboard_uid)
    loads_dashboard_uid = json.loads(dumps_dashboard_uid)
    for get_uid in range(len(loads_dashboard_uid)):
        type = loads_dashboard_uid[get_uid]["type"]
        if type == "dash-db":
            uid = loads_dashboard_uid[get_uid]["uid"]
            title = loads_dashboard_uid[get_uid]["title"]
            #print(f"Dashboard name is '{title}'")
            get_dashboard = grafana_api.dashboard.get_dashboard(uid)
            folder_name = get_dashboard['meta']['folderTitle']
# выкачиваем дашборд {title} и сохраняем с именем файла title.json в папку {folder_name}
        # удаляем из json объект 'meta' в рез-те которого нет возможности импортировать дашборд
            del get_dashboard['meta']
        # создаем каталог {org_name} и {folder_name} в backup_dir
            os.makedirs(os.path.join(backup_dir, org_name, folder_name), exist_ok=True)
        #print(get_dashboard)
            with open(f'{backup_dir}/{org_name}/{folder_name}/{title}.json', 'w', encoding='utf-8') as json_file:
                json.dump(get_dashboard, json_file, ensure_ascii=False, indent=4)
        # удаляем из json вторую строку с '"dashboard": {' и последнюю с '{' в рез-те которых нет возможности импортировать дашборд
            with open(f'{backup_dir}/{org_name}/{folder_name}/{title}.json', 'r+') as modify:
                lines = modify.readlines()
                modify.seek(0)
                modify.truncate()
                modify.writelines(lines[:1] + lines[2:])
            with open(f'{backup_dir}/{org_name}/{folder_name}/{title}.json', 'r+') as modify:
                lines = modify.readlines()
                modify.seek(0)
                modify.truncate()
                modify.writelines(lines[:-1])
            print(f"Saving dashboard '{title}' to folder '{backup_dir}/{org_name}/{folder_name}'")
# удаляем архивы оставляя n-копий
    for filename in sorted(glob.glob(os.path.join(f'{backup_dir}/{org_name}*.zip')))[:-2]:
        filename_path = os.path.join(filename)
        if filename_path:
            os.remove(filename_path)
