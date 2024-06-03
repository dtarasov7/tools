#!/usr/bin/env python

"""Grafana dashboard exporter"""

import json
import os
import requests
import subprocess
import time
import shutil
from zipfile import ZipFile
from os.path import basename

HOST = 'http://admin:admin@localhost:3000'
API_KEY = '<api_key>'
DIR = 'exported-dashboards/'
DIR_IMPORT = 'imported-dashboards/'

def main():
    headers = {'Authorization': 'Bearer %s' % (API_KEY,)}
    response = requests.get('%s/api/search?query=&' % (HOST,), headers=headers)
    response.raise_for_status()
    dashboards = response.json()
    timestr = time.strftime("%m%d%Y")

    if os.path.exists(DIR) and os.path.isdir(DIR):
        shutil.rmtree(DIR)

    if not os.path.exists(DIR):
        os.makedirs(DIR)

    for d in dashboards:
        print ("Saving: " + d['title'])
        response = requests.get('%s/api/dashboards/%s' % (HOST, d['uri']), headers=headers)
        data = response.json()['dashboard']
        dash = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        name = data['title'].replace(' ', '_').replace('/', '_').replace(':', '').replace('[', '').replace(']', '')
        tmp = open(DIR + name + '-' + timestr + '.json', 'w')
        tmp.write(dash)
        tmp.write('\n')
        tmp.close()

    if os.path.exists(DIR_IMPORT) and os.path.isdir(DIR_IMPORT):
        shutil.rmtree(DIR_IMPORT)

    if not os.path.exists(DIR_IMPORT):
        os.makedirs(DIR_IMPORT)

    subprocess.run("for filename in exported-dashboards/*.json; do new=$(echo $filename|sed 's,exported-dashboards/,,g') && cat $filename | jq 'del(.id)' > imported-dashboards/$new; done && grep -L dashboard imported-dashboards/*.json | xargs rm", shell=True)

    with ZipFile('imported-dashboards' + '-' + timestr + '.zip', 'w') as zipObj:
       for folderName, subfolders, filenames in os.walk(DIR_IMPORT):
           for filename in filenames:
               filePath = os.path.join(folderName, filename)
               zipObj.write(filePath, basename(filePath))

if __name__ == '__main__':
    main()


