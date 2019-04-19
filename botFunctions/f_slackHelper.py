from slackclient import SlackClient
from utils.config import get_value

#get Configurations
bot_token = get_value('Configuration','dollhouse_bot_token')
running_account = get_value('Configuration','running_account')

#get Constants
slack_channel = get_value('Constants', 'SLACK_CHANNEL')

slack_client = SlackClient(bot_token)
starterbot_id = None

def firewall_insert_slack(created_by,operation_type,firewall_name,project_name,allowed,source):
    print('[*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+created_by+"* has just *"+operation_type+"ed* a firewall rule: *"+firewall_name+"* in project *"+project_name+ "*. Ports opened by this firewall rule is/are: *"+str(allowed)+"* which can be accessed from *"+str(source)+"*" )

def firewall_delete_slack(deleted_by,firewall_name,project_name):
    print('[*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+deleted_by+"* deleted firewall rule  *"+firewall_name+"* in the project *"+project_name+"*")

def iamrole_slack(principalEmail,action,member,project_name,role):
    print('[*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *"+action+"ED* *"+member+"* in project *"+project_name+ "* with role  *"+role+"*")

def createKey_slack(principalEmail, accountName, project_name):
    print('[*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *CREATED a new key* on the service Account *"+accountName+"* in project *"+project_name+ "*")

def deleteKey_slack(principalEmail,accountName,project_name):
    print('[*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, text = "*"+principalEmail+"* has just *DELETED a key* on the service Account *"+accountName+"* in project *"+project_name+ "*")

def os_command_slack(msg_timestamp,response):
    print('[*] DEBUG: slack alert sent')
    slack_client.api_call("chat.postMessage", channel=slack_channel, thread_ts = msg_timestamp, text = response)