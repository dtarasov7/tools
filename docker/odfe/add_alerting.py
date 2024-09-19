#!/usr/bin/env python

__author__ = "Kalinin Oleg"
__date__ = "06.06.2023"
__status__ = "Production"

import yaml
from yaml.loader import SafeLoader
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open('/opt/nfs-client/scripts/dtln-prod/odfe/add_alerting.yml', 'r') as f:
    yaml_file = yaml.load(f, Loader=SafeLoader)
    for notif in yaml_file["notifications"]:
        name = notif["name"]
        is_enable = notif["enable"]
        description = notif["description"]
        webhook_url = notif["webhook"]["url"]
        # create notifications
        #print(f"=== Создаем канал для уведомлений [{name}] ===")
        notif_json_data = {
            "config_id": name,
            "name": name,
            "config": {
              "name": name,
              "description": description,
              "config_type": "webhook",
              "is_enabled": is_enable,
              "webhook": {
                "url" : webhook_url,
                "header_params" : {
                  "Content-Type" : "application/json"
                },
              }
            }
          }
        try:
           response = requests.post('https://localhost:9200/_plugins/_notifications/configs/', auth=('admin','fofffff'), verify=False, json=notif_json_data)
           #print(response)
           response.raise_for_status()
           if response.status_code == 200:
               print(f"=== Создаем канал для уведомлений [{name}] ===")
        except requests.exceptions.HTTPError as err:
           if response.status_code == 409:
               print(f"=== Канал для уведомлений [{name}] уже существует ===\n*** Обновляем данные ***")
               try:
                  response = requests.put('https://localhost:9200/_plugins/_notifications/configs/name', auth=('admin','fofffff'), verify=False, json=notif_json_data)
                  #print(response)
                  response.raise_for_status()
               except requests.exceptions.HTTPError as err:
                  raise SystemExit(err)
                  sys.exit()
           else:
               raise SystemExit(err)
               sys.exit()

    for monit in yaml_file["monitors"]:
        name = monit["name"]
        enabled = monit["enabled"]
        schedule_interval = monit["schedule"]["interval"]
        schedule_unit = monit["schedule"]["unit"]
        indices = monit["indices"]
        range_from = monit["range"]["from"]
        query = monit["query"]
        trigger_name = monit["triggers"]["name"]
        trigger_severity = monit["triggers"]["severity"]
        action_name = monit["triggers"]["actions"]["name"]
        action_channel = monit["triggers"]["actions"]["notification_channel"]
        action_msg = monit["triggers"]["actions"]["message_template"]
        trigger_condition = monit["triggers"]["condition"]
        # check if monitor existe
        json_check_data = {
            "query": {
              "match" : {
                "monitor.name": name
              }
            }
        }
        try:
           response = requests.get('https://10.80.252.13:9200/_plugins/_alerting/monitors/_search', auth=('admin','fofffff'), verify=False, json=json_check_data)
           if json.loads(response.text)['hits']['total']['value'] != 0:
               print(f"=== Монитор [{name}] уже существует ===")
               continue
           response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
           raise SystemExit(ex)
           sys.exit()
        # create monitor
        print(f"=== Создаем монитор [{name}] ===")
        json_data = {
            "type": "monitor",
            "name": name,
            "monitor_type": "query_level_monitor",
            "enabled": enabled,
            "schedule": {
              "period": {
                "interval": schedule_interval,
                "unit": schedule_unit
                }
              },
            "inputs" : [{
              "search": {
                "indices" : indices,
                "query": {
                  "size": 0,
                  "query": {
                      "bool": {
                          "filter": [{
                                  "range": {
                                      "@timestamp": {
                                          "gte": range_from,
                                          "lte": "{{period_end}}",
                                          "format": "epoch_millis"
                                      }
                                  }
                              },
                                  query
                          ],
                          "adjust_pure_negative": 'true'
                      }
                  },
                  "aggregations": {}
                }
               }
              }],
            "triggers": [{
              "name": trigger_name,
              "severity": trigger_severity,
              "condition": {
                "script": {
                  "source": trigger_condition,
                  "lang": "painless"
                }
              },
              "actions": [{
                "name": action_name,
                "destination_id": action_channel,
                "message_template": {
                  "source": action_msg,
                    "lang": "mustache"
                  },
                "throttle_enabled": 'false',
                "subject_template": {
                  "source": "",
                  "lang": "mustache"
                  }
                }]
              }
            ]
          }
        try:
           response = requests.post('https://10.80.252.13:9200/_plugins/_alerting/monitors', auth=('admin','fofffff'), verify=False, json=json_data)
           #print(response)
           response.raise_for_status()
        except requests.exceptions.HTTPError as err:
           raise SystemExit(err)
           sys.exit()

