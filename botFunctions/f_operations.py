#This module checks if an intance is applied with a network(firewall)
#tag which already exists and added at a later point of time. 
#It also checks if an instance is given a public IP. 


import os
import json
import ast
from botFunctions import f_firewall
import datetime

def dollhouse_bot_help():
    print "bot help command found"
    response =''' *Here are the commands you can ask me:*
        ```- describe [firewall_rule_name] in [project]
        - inspect [service-account] in [project]
        - show [IAM-role] in [project]
        - what is [tag_name] in [project]
        ```
        ''' 
    return response

def get_firewall_raw_operations(operation_type,project_name,NUM_OF_INCIDENTS):
    raw_operations = os.popen('gcloud compute operations list --filter="operationType='+operation_type+ ' AND targetLink=https://www.googleapis.com/compute/v1/projects/'+project_name+'/global/firewalls/" --sort-by ~TIMESTAMP | grep -m'+str(NUM_OF_INCIDENTS + 1)+' ""').read()
    return raw_operations

def get_iam_raw_operations(NUM_OF_INCIDENTS):
    cmd = 'gcloud logging read "resource.type=project AND protoPayload.serviceName=cloudresourcemanager.googleapis.com AND protoPayload.methodName=SetIamPolicy" --format=json --limit='+str(NUM_OF_INCIDENTS)
    o = os.popen(cmd,'r')
    raw_operations = o.read()
    return raw_operations

def get_deleteKey_raw_operations(NUM_OF_INCIDENTS):
    raw_operations = os.popen("gcloud logging read \"resource.type=\"service_account\" AND protoPayload.serviceName=\"iam.googleapis.com\" AND protoPayload.methodName=\"google.iam.admin.v1.DeleteServiceAccountKey\"\" --format=json --limit="+str(NUM_OF_INCIDENTS)).read()
    return raw_operations()

def check_public_ip(instanceName, project):
    raw_instance = os.popen('gcloud compute instances describe ' + instanceName + ' --format=json').read()
    json_instance = json.loads(raw_instance)
    try:
        public_ip = str(json_instance.get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP'))
        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[" + currentTime + "] [*] DEBUG: Public IP is " + public_ip)
    except:
        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[" + currentTime + "] [*] DEBUG: No Public IP found for " + instanceName)
        public_ip = ''
    return public_ip

def key_toES(principalEmail,method, accountName,project_name,now_strftime):
    json_key = {}
    json_key['user'] = principalEmail
    json_key['method'] = method
    json_key['member'] = accountName
    json_key['project_name'] = project_name
    json_key['time'] = now_strftime
    return json_key

def iam_toES(principalEmail,action,member,project_name,role,now_strftime):
    json_iam = {}
    json_iam['user'] = principalEmail
    json_iam['method'] = action
    json_iam['member'] = member
    json_iam['project_name'] = project_name
    json_iam['role'] = role
    json_iam['time'] = now_strftime
    return json_iam
    
def firewall_toES(action_by, method,firewall_name, project_name, ports, source, now_strftime):
    json_firewall_body = {}
    json_firewall_body['user'] = action_by
    json_firewall_body['method'] = method
    json_firewall_body['firewall_name'] = firewall_name
    json_firewall_body['project_name'] = project_name
    json_firewall_body['ports'] = ports
    json_firewall_body['source'] = source
    json_firewall_body['time'] = now_strftime
    return json_firewall_body

def instanceSetTag_toES(principalEmail,resourceName,list_tags,project_name):
    json_instanceSetTag = {}
    json_instanceSetTag['user'] = principalEmail
    json_instanceSetTag['instance'] = resourceName
    json_instanceSetTag['tags'] = str(list_tags)
    json_instanceSetTag['delta'] = str(new_tags)
    json_instanceSetTag['time'] = now_strftime
    json_instanceSetTag['project_name'] = project_name
    return json_instanceSetTag

def instanceAddAccessConfig_toES(user,resourceName,public_ip, now_strftime,project_name):
    json_instanceAddAccessConfig = {}
    json_instanceAddAccessConfig['user'] = user
    json_instanceAddAccessConfig['instance'] = resourceName
    json_instanceAddAccessConfig['publicIP'] = public_ip
    json_instanceAddAccessConfig['time'] = now_strftime
    json_instanceAddAccessConfig['project_name'] = project_name
    return json_instanceSetTag
