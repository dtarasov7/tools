#
# https://github.com/panodata/grafana-client
#

from grafana_client import GrafanaApi
from grafana_client.client import GrafanaClientError
#from grafana_client.util import setup_logging
import sys
import os
from os import path
import yaml
import json
import re
from yaml.loader import SafeLoader
import requests
import logging
from logging.handlers import RotatingFileHandler
import argparse

__author__ = "Kalinin Oleg"
__date__ = "25.11.2022"
__status__ = "Production"

# Help
#def ext_check(expected_extension, openner):
#    def extension(filename):
#        if not filename.lower().endswith(expected_extension):
#            raise ValueError()
#        return openner(filename)
#    return extension

parser = argparse.ArgumentParser(
        description='This python script for Grafana is used to create organizations and users, to import the dashboard and set it as the homepage.')
#parser.add_argument('orgs_and_users', type=ext_check('.yaml', argparse.FileType('r')), help='users list in YAML format')
parser.add_argument('orgs_and_users', type=str, help='users list in YAML format')
parser.add_argument('dashboard', type=str, help='dashboard file in JSON format')
args = parser.parse_args()
#print(args.orgs_and_users)
print(args)

# Logging
log_file_path = 'logs.log'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s'",
    handlers=[
        #logging.FileHandler(log_file_path),
        RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=3)
        #logging.StreamHandler()
    ]
)
except_log = logging.getLogger("ex")

# Grafana auth input
#grafana_admin_user = input("Enter user name with Global Admin role: ")
#grafana_admin_passwd = input("Enter user password: ")
# Grafana path (add '/?verify=false' if https)
#grafana_url = f'http://{grafana_admin_user}:{grafana_admin_passwd}@localhost:3002/?verify=false'
grafana_url = f'http://admin:admin@localhost:3002/?verify=false'
# Grafana datasource
datasource_name = 'Victoria-Metrics'
datasource_uid = 'svoeZhilyo'
datasource_url = 'http://192.168.3.60:8481/select/0/prometheus'
datasource_basic_auth_user = 'user'
datasource_basic_auth_passwd = 'basicpassword'

# Connect to Grafana API endpoint using the `GrafanaApi` class
grafana = GrafanaApi.from_url(grafana_url)

# Check argv
try:
    print("=== Check args if set ===")
    logging.info("=== Check args if set ===")
    gf_data = sys.argv[1]
    print(f"Data from '{gf_data}' file will be used")
    logging.info(f"Data from '{gf_data}' file will be used")
except IndexError:
    print("Specify data yaml file")
    except_log.exception("Specify data yaml file")
    sys.exit(1)
try:
    gf_dashboard = sys.argv[2]
    print(f"Dashboard '{gf_dashboard}' for import")
    logging.info(f"Dashboard '{gf_dashboard}' for import")
except IndexError:
    print("Json file with dashboard no specify")
    except_log.exception("Json file with dashboard no specify")
    sys.exit(1)

# Check connection and admin credentials
try:
    print("=== Check connection to Grafana ===")
    logging.info("=== Check connection to Grafana ===")
    requests.get(grafana_url, verify=False)
    print("Connection established")
    logging.info("Connection established")
except ConnectionError:
    print("Connection refused")
    except_log.exception("Connection refused")
    sys.exit(1)
try:
    print("=== Check admin credentials ===")
    logging.info("=== Check admin credentials ===")
    get_stats = grafana.admin.stats()
    print("Authorized")
    logging.info("Authorized")
except:
    print("Unauthorized")
    except_log.exception("Unauthorized")
    sys.exit(1)

# Check if files exists
try:
    print(f"=== Check if file '{gf_data}' and {gf_dashboard} exists ===")
    logging.info(f"=== Check if file '{gf_data}' and {gf_dashboard} exists ===")
    f = open(gf_data)
    f.close()
    print("File {} exist".format(sys.argv[1]))
    logging.info("File {} exist".format(sys.argv[1]))
except FileNotFoundError:
    print(f"File '{gf_data}' does not exist!")
    except_log.exception(f"File '{gf_data}' does not exist!")
    sys.exit(1)
try:
    f = open(gf_data)
    f.close()
    print("File {} exist".format(sys.argv[2]))
    logging.info("File {} exist".format(sys.argv[2]))
except FileNotFoundError:
    print(f"File '{gf_dashboard}' does not exist!")
    except_log.exception(f"File '{gf_dashboard}' does not exist!")
    sys.exit(1)

# Check YAML data
with open(f"{gf_data}", "r") as f:
    check_yaml_file = yaml.load(f, Loader=SafeLoader)
    f.close()
print("=== Check YAML data ===")
logging.info("=== Check YAML data ===")
if 'orgs' in check_yaml_file:
    pass
else:
    print("The list of organizations is not defined")
    logging.error("The list of organizations is not defined")
    sys.exit(1)
try:
    for k, v in check_yaml_file["orgs"]:
        if 'users' not in v:
            print("The users list is not defined")
except ValueError as ex:
        print("The users list is not defined")
        except_log.exception(f"ERROR: {ex}")
        sys.exit(1)
print("YAML checked\n")
logging.info("YAML checked")

### Create Orgs and Users
with open(f"{gf_data}", "r") as f:
    yaml_file = yaml.load(f, Loader=SafeLoader)
    new_users = [] # Get a list of new login names
    new_orgs = [] # Get a list new organization names
    for data in yaml_file["orgs"]:
        org_name = data["org_name"]
        new_orgs.append(org_name)
        print("=== Add organization(s) ===")
        logging.info("=== Add organization(s) ===")
        try:
            ## Create organization
            grafana.organization.create_organization(
                organization={"name": '{0}'.format(org_name)})
            # Get Org new ID
            org_id = int(grafana.organization.find_organization(org_name)['id'])
            print(f"Organization with name '{org_name}' and id '{org_id}' added!")
            logging.info(f"Organization with name '{org_name}' and id '{org_id}' added!")
        except GrafanaClientError as ex:
            if ex.status_code == 409:
                # Get existe Org ID
                org_id = int(grafana.organization.find_organization(org_name)['id'])
                print(f"Organization with name '{org_name}' and id '{org_id}' already exists!")
                logging.info(f"Organization with name '{org_name}' and id '{org_id}' already exists!")
            else:
                print(f"ERROR: {ex}")
                except_log.exception(f"ERROR: {ex}")
        ## Create datasource
        grafana.organizations.switch_organization(org_id)
        print(f"=== Add datasource to '{org_name}' organization ===")
        logging.info(f"=== Add datasource to '{org_name}' organization ===")
        if not datasource_basic_auth_user:
            datasource_data = {"name": "{0}".format(datasource_name), "uid": "{0}".format(datasource_uid), "type": "prometheus", "url": "{0}".format(datasource_url), "access": "proxy", "basicAuth": false}
        else:
            datasource_data = {"name": "{0}".format(datasource_name), "uid": "{0}".format(datasource_uid), "type": "prometheus", "url": "{0}".format(datasource_url), "access": "proxy", "basicAuth": True, "isDefault": True, "basicAuthUser": "{0}".format(datasource_basic_auth_user), "secureJsonData": {"basicAuthPassword": "{0}".format(datasource_basic_auth_passwd)}}
        try:
            grafana.datasource.create_datasource(datasource_data)
            print(f"Datasource added!")
            logging.info(f"Datasource added!")
        except GrafanaClientError as ex:
            if ex.status_code == 409:
                datasource_id = int(grafana.datasource.get_datasource_id_by_name(datasource_name)['id'])
                #print(datasource_id)
                # Update datasource data if need
                grafana.datasource.update_datasource(datasource_id,datasource_data)
                print("Datasource with the same name already exists! Data updated!")
                logging.info("Datasource with the same name already exists! Data updated!")
            else:
                print(f"ERROR: {ex}")
                except_log.exception(f"ERROR: {ex}")
        ## Create user
        print(f"=== Add user(s) to '{org_name}' organization ===")
        logging.info(f"=== Add user(s) to '{org_name}' organization ===")
        # Get username and password of new users
        users_list = data["users"]
        added_users = [] # Get added users list
        for user in users_list:
            #added_users = []
            user_name = user['username'].lower()
            new_users.append(user_name)
            added_users.append(user_name)
            # Add user
            try:
                grafana.admin.create_user({"name": "{0}".format(user_name), "email": "{0}".format(user_name), "login": "{0}".format(user_name), "password": "{0}".format(user_name), "OrgId": org_id })
                print(f"User with name '{user_name}' added!")
                logging.info(f"User with name '{user_name}' added!")
            except GrafanaClientError as ex:
                if ex.status_code == 412:
                    # Add user to other Orgs
                    user_id = grafana.users.find_user(user_name)['id']
                    user_orgs = grafana.users.get_user_organisations(user_id)#['orgId']
                    for user_org in user_orgs:
                        t = int(user_org['orgId'])
                        n = user_org['name']
                        if t != org_id:
                            #print(f"User with name '{user_name}' already exists in this organization!")
                        #else:
                            try:
                                user_data = {"loginOrEmail": "{0}".format(user_name),"role": "Viewer"}
                                grafana.organizations.organization_user_add(org_id, user_data)
                                print(f"User with name '{user_name}' added!")
                                logging.info(f"User with name '{user_name}' added!")
                            except GrafanaClientError as ex:
                                if ex.status_code == 409:
                                    pass
                                else:
                                    print(f"ERROR: {ex}")
                                    except_log.exception(f"ERROR: {ex}")
                    print(f"User with name '{user_name}' already exists!")
                    logging.info(f"User with name '{user_name}' already exists!")
        ## Delete users
        # Get list added users
        added_users_list = []
        for uu in added_users:
            aa = int(grafana.users.find_user(uu)['id'])
            added_users_list.append(aa)
        #print(added_users_list)
        # Get list current users in current Org
        org_current_user_list = []
        grafana.organizations.switch_organization(org_id)
        current_organization_users = grafana.organization.get_current_organization_users()
        for current_user in current_organization_users:
            cc = int(current_user['userId'])
            org_current_user_list.append(cc)
        #print(org_current_user_list)
        # Diff between added users and current users and deleting
        diff_added_current_lists = []
        for dd in org_current_user_list:
            if dd not in added_users_list:
                diff_added_current_lists.append(dd)
        #print(diff_added_current_lists)
                if dd != 1: # exclude id 1 (Admin)
                    del_user_name = grafana.users.get_user(dd)['name']
                    print(f"User '{del_user_name}' deleted from organization '{org_name}'!")
                    logging.info(f"User '{del_user_name}' deleted from organization '{org_name}'!")
                    grafana.organization.delete_user_current_organization(dd)
        ## Import dashboard json file
        print(f"=== Import dashboard '{gf_dashboard}' to '{org_name}' organization ===")
        logging.info(f"=== Import dashboard '{gf_dashboard}' to '{org_name}' organization ===")
        # Swith to Org
        grafana.organizations.switch_organization(org_id)
        # Create or update a dashboard
        dashboard_file = open(f"{gf_dashboard}", "r")
        json_data = json.load(dashboard_file)
        dashboard_file.close()
        dashboard_data = {'dashboard': json_data, 'overwrite': True}
        dashboard_permissions_data = {"items": [{"role": "Viewer","permission": 1}]}
        try:
            update_dashboard = grafana.dashboard.update_dashboard(dashboard_data)
            print("Dashboard imported!")
            logging.info("Dashboard imported!")
        except GrafanaClientError as ex:
            if ex.status_code != 200:
                print(f"ERROR: {ex}")
                except_log.exception(f"ERROR: {ex}")
        dashboard_id = int(update_dashboard['id'])
        dashboard_uid = update_dashboard['uid']
        # Set permissions
        try:
            grafana.dashboard.update_dashboard_permissions(dashboard_id, dashboard_permissions_data)
            print("Permissions for role Viewer added!")
            logging.info("Permissions for role Viewer added!")
        except GrafanaClientError as ex:
            if ex.status_code != 200:
                print(f"ERROR: {ex}")
                except_log.exception(f"ERROR: {ex}")
        # Set default home page
        print(f"=== Set dashboard '{gf_dashboard}' like home dashboard ===")
        logging.info(f"=== Set dashboard '{gf_dashboard}' like home dashboard ===")
#        home_dashboard = {"theme": "", "homeDashboardId": dashboard_id, "timezone": 'browser'}
#        headers = {"X-Grafana-Org-Id": "{0}".format(org_id)}
        try:
            grafana.organizations.organization_preference_update(theme="", home_dashboard_id=dashboard_id, timezone="browser")
#            grafana_url = grafana_url.replace('/?verify=false', '')
#            set_home = requests.put(f"{grafana_url}/api/org/preferences/", verify=False, json=home_dashboard, headers=headers)
#            set_home.raise_for_status()
            print(f"Dashboard set for all users in the organization '{org_name}'!\n")
            logging.info(f"Dashboard set for all users in the organization '{org_name}'!")
        except GrafanaClientError as ex:
            if ex.status_code != 200:
                print(f"ERROR: {ex}")
                except_log.exception(f"ERROR: {ex}")

### Delete Orgs and Users
## Get all users id
#all_users = grafana.users.search_users()
##print(all_users)
#all_users_list = []
#for all in all_users:
#    u = int(all['id'])
#    all_users_list.append(u)
#all_users_list.remove(1) # id=1 it is admin
##print(all_users_list)
## Get a list name of existing Orgs
#exist_orgs = grafana.organizations.list_organization()
#orgs_list = []
#for org in exist_orgs:
#    org_name = org.get("name")
#    orgs_list.append(org_name)
## Exclude [Mm]ain.* Org
#exclude_main_org = re.compile(r'[Mm]ain.*$')
#regex_org = [main for main in orgs_list if not exclude_main_org.match(main)]
##print(regex_org)
## Get a list of all users in all Orgs
#users_list = []
#for uo in regex_org:
#    org_id = int(grafana.organization.find_organization(uo)['id'])
#    exist_users = grafana.organizations.organization_user_list(org_id)
#    for u_id in exist_users:
#        user_login = int(u_id.get('userId'))
#        users_list.append(user_login)
#users_list.remove(1)
##print(users_list)
## Diff between all exist users and new users
#diff_users_list = []
#for d in all_users_list:
#    if d not in users_list:
#        diff_users_list.append(d)
##print(diff_users_list)
## Get user ID for delete
#print("=== Delet user(s) without organization ===")
#logging.info("=== Delet user(s) without organization ===")
#if diff_users_list:
#    for du in diff_users_list:
#        delete_user_name = grafana.users.get_user(du)['name']
#        try:
#            grafana.admin.delete_user(du)
#            print(f"User with name '{delete_user_name}' and id '{du}' deleted from system!")
#            logging.info(f"User with name '{delete_user_name}' and id '{du}' deleted from system!")
#        except:
#            print(f"Couldn't delete user with name '{delete_user_name}'")
#            except_log.exception(f"Couldn't delete user with name '{delete_user_name}'")
#else:
#    print("No user(s) for deleting")
#    logging.info("No user(s) for deleting")
## Diff between exist Orgs and new Orgs
#diff_list_orgs = []
#for d in regex_org:
#    if d not in new_orgs:
#        diff_list_orgs.append(d)
##print(diff_list_orgs)
## Get Org ID for delete
#print("=== Delet organization(s) not included in the new list ===")
#logging.info("=== Delet organization(s) not included in the new list ===")
#if diff_list_orgs:
#    for o in diff_list_orgs:
#        delete_org_id = int(grafana.organization.find_organization(o)['id'])
#        try:
#            grafana.organizations.delete_organization(delete_org_id)
#            print(f"Organization with name '{o}' and id '{delete_org_id}' deleted!")
#            logging.info(f"Organization with name '{o}' and id '{delete_org_id}' deleted!")
#        except:
#            print(f"Couldn't delete organization with name '{o}'")
#            except_log.exception(f"Couldn't delete organization with name '{o}'")
#else:
#    print("No organization(s) for deleting")
#    logging.info("No organization(s) for deleting")
