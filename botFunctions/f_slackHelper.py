import datetime
from slackclient import SlackClient
from utils.config import get_value
import os

#get Configurations
bot_token = get_value('Configuration','dollhouse_bot_token')
running_account = get_value('Configuration','running_account')

#get Constants
slack_channel = get_value('Constants', 'SLACK_CHANNEL')

slack_client = SlackClient(bot_token)
starterbot_id = None

def firewall_insert_slack(created_by,operation_type,firewall_name,project_name,allowed,source):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+created_by+"* has just *"+operation_type+"ed* a firewall rule: *"+firewall_name+"* in project *"+project_name+ "*. Ports opened by this firewall rule is/are: *"+str(allowed)+"* which can be accessed from *"+str(source)+"*" )

def firewall_delete_slack(deleted_by,firewall_name,project_name):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+deleted_by+"* deleted firewall rule  *"+firewall_name+"* in the project *"+project_name+"*")

def iamrole_slack(principalEmail,action,member,project_name,role):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *"+action+"ED* *"+member+"* in project *"+project_name+ "* with role  *"+role+"*")

def createKey_slack(principalEmail, accountName, project_name):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *CREATED a new key* on the service Account *"+accountName+"* in project *"+project_name+ "*")

def deleteKey_slack(principalEmail,accountName,project_name):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *DELETED a key* on the service Account *"+accountName+"* in project *"+project_name+ "*")

def os_command_slack(msg_timestamp,response):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, thread_ts = msg_timestamp, text = response)

def instanceSetTag_slack(principalEmail,resourceName,list_tags,project_name):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *MODIFIED* instance tags for *"+resourceName+"* in project *"+project_name+ "*. Current Tag is *" + str(list_tags) + "*")

def instanceAddAccessConfig_slack(user,resourceName,project_name,list_tags,public_ip):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+user+"* has just *Added Access Config* for *"+resourceName+"* in project *"+project_name+ "* with *Public IP: " + str(public_ip) + "*. Network Tags are *" + str(list_tags) + "*")

def newProjects_slack(diff):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = '*New Google Cloud Projects* ```' + str(diff) + '```')

def k8Anonymous_create_slack(principalEmail,bindingName,access,project_name,role,cluster_name):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *CREATED* a cluster binding: *"+bindingName+"* given to *"+access+ "* on cluster *"+cluster_name+"* in project *"+project_name+"* with role *"+role+"*")

def k8Anonymous_patch_slack(principalEmail,bindingName,access,project_name,role,cluster_name):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *UPDATED* a cluster binding: *"+bindingName+"* given to *"+access+ "* on cluster *"+cluster_name+"* in project *"+project_name+"* with role *"+role+"*")

