import os
import time
import re
from slackclient import SlackClient
import math
import ast
import json
from netaddr import IPAddress
import datetime
from elasticsearch import Elasticsearch
from utils.config import get_value
from botFunctions import f_firewall, f_iam, f_operations, f_serviceAccount, f_slackHelper

# Get Configuration Value
eshost = get_value('Configuration','elasticsearch_host')
esport = get_value('Configuration','elasticsearch_port')
bot_token = get_value('Configuration','dollhouse_bot_token')
running_account = get_value('Configuration','running_account')

# Get Constant Value
RTM_READ_DELAY = int(get_value('Constants','RTM_READ_DELAY')) # 1 second delay between reading from RTM
FIREWALL_DESCRIBE_COMMAND = get_value('Constants','FIREWALL_DESCRIBE_COMMAND')
IAM_ROLE_DESCRIBE_COMMAND = get_value('Constants','IAM_ROLE_DESCRIBE_COMMAND')
SERVICEACCONT_IDENTIFY_COMMAND = get_value('Constants','SERVICEACCONT_IDENTIFY_COMMAND')
HELP_COMMAND= get_value('Constants','HELP_COMMAND')
COMMAND_REGEX = get_value('Constants','COMMAND_REGEX')
MENTION_REGEX = get_value('Constants','MENTION_REGEX') #get group 2
PROJECT_REGEX = get_value('Constants','PROJECT_REGEX') #get group 3
OPERATION_REGEX = get_value('Constants','OPERATION_REGEX') #get group 3
ALERT_TYPE_REGEX = get_value('Constants','ALERT_TYPE_REGEX')
SERVICEACCOUNT_REGEX = get_value('Constants','SERVICEACCOUNT_REGEX')
ONE_ALERT = float(get_value('Constants','ONE_ALERT'))
slack_channel = get_value('Constants', 'SLACK_CHANNEL')

# Variable Initiation
global es 
es = Elasticsearch([{'host': eshost, 'port': esport}])
now = datetime.datetime.now()
now_strftime = now.strftime("%Y-%m-%d")
slack_client = SlackClient(bot_token) # instantiate Slack client
starterbot_id = None # starterbot's user ID in Slack: value is assigned after the bot starts up
list_of_operations = []


# Parses a list of events coming from the Slack RTM API to find bot commands.
# If a bot command is found, this function returns a tuple of command and channel.
# If its not found, then this function returns None, None.
def parse_bot_commands(slack_events):
    for event in slack_events:
        try:
            if event["type"] == "message" and not "this-doesnt-exist" in event:
                project_name, alert_threshold, operation_type, alert_type = parse_direct_mention(event["attachments"][0]["text"])
                handle_command(project_name, alert_threshold, operation_type, alert_type)
                return project_name, alert_threshold, operation_type, alert_type
        except:
            try:
                print event
                if event["type"] == "message" and not "subtype" in event:
                    command = event["text"]  
                    handle_os_command(command,event["ts"],event["channel"])                 
                    print ("[*] DEBUG: command is: \n" + command)
                    return command,event["ts"],event["channel"],None
            except:
                continue        
    return None, None, None, None


# Finds a direct mention (a mention that is at the beginning) in message text
# and returns the user ID which was mentioned. If there is no direct mention, returns None
def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    project_name = re.search(PROJECT_REGEX, message_text)
    operation_type = re.search(OPERATION_REGEX,message_text)
    alert_type = re.search(ALERT_TYPE_REGEX,message_text)

    global ALERT_THRESHOLD, PROJECT_NAME, OPERATION_TYPE, ALERT_TYPE
    ALERT_THRESHOLD = ast.literal_eval(matches.group(2).strip())
    PROJECT_NAME = str(project_name.group(3)).strip()

    if str(alert_type.group(0)) == 'iamrole':
        print('[*] DEBUG: iamrole')
        OPERATION_TYPE = 'iamrole'
        ALERT_TYPE = 'iamrole'
        return (PROJECT_NAME, ALERT_THRESHOLD, OPERATION_TYPE, ALERT_TYPE)

    elif str(alert_type.group(0)) == 'firewall':
        print('[*] DEBUG: firewall')
        ALERT_TYPE = 'firewall'
        OPERATION_TYPE = str(operation_type.group(3)).strip()
        return (PROJECT_NAME, ALERT_THRESHOLD, OPERATION_TYPE, ALERT_TYPE)

    elif str(alert_type.group(0)) == 'serviceAccount':
        print('[*] DEBUG: serviceAccount')
        serviceAccount_operation = re.search(SERVICEACCOUNT_REGEX,message_text)
        ALERT_TYPE = str(serviceAccount_operation.group(3)).strip()
        OPERATION_TYPE = 'null'
        return (PROJECT_NAME, ALERT_THRESHOLD, OPERATION_TYPE, ALERT_TYPE)

    return (PROJECT_NAME, ALERT_THRESHOLD, OPERATION_TYPE)

def handle_command(project_name, alert_threshold, operation_type, alert_type):
    NUM_OF_INCIDENTS = int(math.ceil(ALERT_THRESHOLD/ONE_ALERT))
    get_operations(project_name,NUM_OF_INCIDENTS, operation_type, alert_type)

def handle_os_command(command,msg_timestamp,channel):
    response = None
    if command.startswith(FIREWALL_DESCRIBE_COMMAND):
        response = f_firewall.firewall_describe_command(command, running_account)
    elif command.startswith(IAM_ROLE_DESCRIBE_COMMAND):
        response = f_iam.iam_show_command(command)
    elif command.startswith(SERVICEACCONT_IDENTIFY_COMMAND):
        response = f_serviceAccount.serviceAccount_identify_command(command)
    elif command.startswith(HELP_COMMAND):
        response = f_operations.dollhouse_bot_help()  
        
    # Sends the response back to the channel
    slack_client.api_call("chat.postMessage", channel=slack_channel, thread_ts = msg_timestamp, text = response)


def get_operations(project_name, NUM_OF_INCIDENTS, operation_type, alert_type):
    os.system("gcloud config set project " + project_name)

    if alert_type == 'firewall':
        raw_operations = f_operations.get_firewall_raw_operations(operation_type,project_name,NUM_OF_INCIDENTS)
        
        for line in raw_operations.split('\n')[1:-1]:
            list_of_operations.append(line.split()[0])

        for operation in list_of_operations:
            raw_operation_desc = os.popen('gcloud compute operations describe '+operation+ ' --format=json').read()
            json_operation_desc = json.loads(raw_operation_desc)
            firewall = json_operation_desc.get('targetLink').split('/')[-1]

            if operation_type == 'insert' or operation_type == 'patch':
                firewallRules = os.popen("gcloud compute firewall-rules describe " + firewall + " --format=json").read()
                print "+++++++++++++++++++++++.  DEBUG  ++++++++++++++++++++++++++"
                print('[*] DEBUG: ' + str(type(firewallRules)))
                print firewallRules
                print "+++++++++++++++++++++++.  DEBUG  ++++++++++++++++++++++++++"

                json_firewallRules = json.loads(firewallRules)

                firewall_name = json_firewallRules.get('name')
                source = str(ast.literal_eval(json.dumps(json_firewallRules.get('sourceRanges'))))
                allowed = str(ast.literal_eval(json.dumps(json_firewallRules.get('allowed'))))
                created_by = json_operation_desc.get('user')
                
                ports_list = []
                for methods in json_firewallRules['allowed']:
                    for ports in methods['ports']:
                        ports_list.append(str(methods['IPProtocol']) + str(ports))

                whitelisted_firewall = f_firewall.check_whitelisted_ports(ports_list)
                if whitelisted_firewall == False:
                    print("[*] DEBUG: Port " + str(ports_list) + " is not whitelisted")
        
                    is_private = f_firewall.check_IP_private(source)
                    if is_private == False:
                        print("[*] DEBUG: IP " + source + " is public")
                        # send alert to slack
                        f_slackHelper.firewall_insert_slack(created_by,operation_type,firewall_name,project_name,str(allowed),str(source))
                        # push to ES
                        json_firewall_body = f_operations.firewall_toES(created_by,operation_type,firewall_name,project_name,str(allowed),str(source),now_strftime)
                        es.index(index='dollhouse', doc_type='alert_firewall', body=json_firewall_body)

                    else: 
                        print("[*] DEBUG:  IP " + source + " is private")
                        continue
                else:
                    print("[*] DEBUG: Port " + str(ports_list) + " is whitelisted")

            elif operation_type == 'delete':
                deleted_by = json_operation_desc.get('user')
                firewall_name = json_operation_desc.get('targetLink').split('/')[-1]
                
                #Codeblock to check if the firewall has been alerted on slack. Querying if this present
                #on elasticseach. If yes then alert the delete else silence it. This is to reduce the 
                #amount of delete firewall alerts which clutters slack channel.

                res = es.search(index='dollhouse', body={"query":{"bool":{"must":[{"match_all":{}},{"match_phrase":{"_type":{"query":"alert_firewall"}}},{"match_phrase":{"firewall_name":{"query":firewall_name}}},{"match_phrase":{"method":{"query":"insert"}}}],"must_not":[]}}})
                if res.get('hits').get('total') >= 1:

                    # send alert to slack
                    f_slackHelper.firewall_delete_slack(deleted_by,firewall_name,project_name)
                    # Push to Elasticsearch
                    json_firewall_body = f_operations.firewall_toES(deleted_by,'delete',firewall_name,project_name,'','',now_strftime)
                    es.index(index='dollhouse', doc_type='alert_firewall', body=json_firewall_body)
                else:
                    print("[*] DEBUG: " + firewall_name + " alert is suppressed")

    
    elif alert_type == 'iamrole':
        raw_operations = f_operations.get_iam_raw_operations()
        json_raw_operations = json.loads(raw_operations)

        for ops in json_raw_operations:
            principalEmail = str(ops.get('protoPayload').get('authenticationInfo').get('principalEmail'))
            list_of_IAMactions = ops.get('protoPayload').get('serviceData').get('policyDelta').get('bindingDeltas')
            for actions in list_of_IAMactions:
                action =  str(actions.get('action'))
                if action == 'REMOVE':
                    action = 'REMOV'
                member = str(actions.get('member'))
                role =  str(actions.get('role'))
                blacklisted_role = f_iam.check_blacklisted_roles(role)
                if blacklisted_role == True:
                    print("[*] DEBUG: Role " + role + " is blacklisted")
                    #send to slack
                    f_slackHelper.iamrole_slack(principalEmail,action,member,project_name,role)
                    # Push to Elasticsearch
                    json_iam = f_operations.iam_toES(principalEmail,action,member,project_name,role,now_strftime)
                    es.index(index='dollhouse', doc_type='alert_IAM', body=json_iam)
                else:
                    print("[*] DEBUG: Role " + role + " is not blacklisted")


    elif alert_type == 'createKey':
        print('[*] DEBUG: createKey')
        raw_operations = os.popen("gcloud logging read \"resource.type=\"service_account\" AND protoPayload.serviceName=\"iam.googleapis.com\" AND protoPayload.methodName=\"google.iam.admin.v1.CreateServiceAccountKey\"\" --format=json --limit="+str(NUM_OF_INCIDENTS)).read()
        json_raw_operations = json.loads(raw_operations)

        for ops in json_raw_operations:
            principalEmail = str(ops.get('protoPayload').get('authenticationInfo').get('principalEmail'))
            accountName = str(ops.get('resource').get('labels').get('email_id'))
            
            # send alert to slack
            f_slackHelper.createKey_slack(principalEmail,accountName,project_name)
            #Push to Elasticsearch
            json_key = f_operations.key_toES(principalEmail,'create',accountName,project_name,now_strftime)
            es.index(index='dollhouse', doc_type='alert_serviceAccount', body=json_key)


    elif alert_type == 'deleteKey':
        print('[*] DEBUG: deleteKey')
        raw_operations = f_operations.get_deleteKey_raw_operations(NUM_OF_INCIDENTS)
        json_raw_operations = json.loads(raw_operations)

        for ops in json_raw_operations:
            principalEmail = str(ops.get('protoPayload').get('authenticationInfo').get('principalEmail'))
            accountName = str(ops.get('resource').get('labels').get('email_id'))
            # send alert to slack
            f_slackHelper.deleteKey_slack(principalEmail,accountName,project_name)
            #Push to Elasticsearch
            json_key = f_operations.key_toES(principalEmail,'delete',accountName,project_name,now_strftime)
            es.index(index='dollhouse', doc_type='alert_serviceAccount', body=json_key)

if __name__ == "__main__":
    os.system("gcloud config set account " + running_account)
    if slack_client.rtm_connect(with_team_state=False):
        print("dollhouse-bot connected and running!")
 
        while True:
            project_name, alert_threshold, operation_type, alert_type = parse_bot_commands(slack_client.rtm_read())
            command = parse_bot_commands(slack_client.rtm_read())
            list_of_operations = []
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
