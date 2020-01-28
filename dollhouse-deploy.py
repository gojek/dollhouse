import argparse
import os
import json
import pdb
import time
from stackdriver import logging, monitoring

parser = argparse.ArgumentParser(description='Implements dollhouse in a project')
parser.add_argument('-p', '--project', dest="projectName", type=str, help='Name of the GCP Project')
parser.add_argument('-d', '--directory', dest="baseDirectory", type=str, help='Directory you are working on')
parser.add_argument("--logserviceAccount", dest="logserviceAccount", help="write custom metrics on serviceAccount", required=False, action='store_true')
parser.add_argument("--logfirewall", dest="logfirewall", help="write custom metrics on firewall", required=False, action='store_true')
parser.add_argument("--loginstance", dest="loginstance", help="write custom metrics on instance", required=False, action='store_true')
parser.add_argument("--createslack", dest="createslack", help="creates a new slack notification", required=False, action='store_true')
parser.add_argument("--logiam", dest="logiam", help="write custom metrics on iam", required=False, action='store_true')
parser.add_argument("--stackdriverfirewall", dest="stackdriverfirewall", help="deploy firewall stackdriver alerting policy", required=False, action='store_true')
parser.add_argument("--stackdriverserviceAccount", dest="stackdriverserviceAccount", help="deploy service account stackdriver alerting policy", required=False, action='store_true')
parser.add_argument("--stackdriveriam", dest="stackdriveriam", help="deploy iam role stackdriver alerting policy", required=False, action='store_true')
parser.add_argument("--stackdriverinstance", dest="stackdriverinstance", help="deploy instance stackdriver alerting policy", required=False, action='store_true')
parser.add_argument("--logk8anonymous", dest="logk8anonymous", help="write custom metrics on k8 anonymous access", required=False, action='store_true')
parser.add_argument("--stackdriverk8anonymous", dest="stackdriverk8anonymous", help="deploy k8 anonymous request alerting policy", required=False, action='store_true')
args = parser.parse_args()

os.system("gcloud config set project " + args.projectName)
time.sleep(5)

def create_custom_metric():
  if args.logfirewall:
    logging.createLoggingFirewall()

  if args.logserviceAccount:
    logging.createLoggingServiceAccount()

  if args.logiam:
    logging.createLoggingIAM()

  if args.loginstance:
    logging.createLoggingInstance()

  if args.logk8anonymous:
    logging.createLoggingK8AnonymousAccess()

def create_slack_notification(project_name, base_directory):
  if args.createslack:
    monitoring.create_slack()

  #grabs the channel ID of a project
  channelID = os.popen("gcloud alpha monitoring channels list | grep '#sec-stackdrv-ignore' -A1 | grep 'notificationChannels' | awk -F '/' '{print $NF}'").read().strip()
  print "channelID is " + channelID

  #CREATING MONITORING POLICIES
  if args.stackdriverfirewall:
    monitoring.firewall_delete(project_name,channelID)
    monitoring.firewall_insert(project_name,channelID)
    monitoring.firewall_patch(project_name,channelID)

  if args.stackdriverserviceAccount:
    monitoring.serviceAccount_create(project_name,channelID)
    monitoring.serviceAccount_delete(project_name,channelID)
    monitoring.serviceAccount_createKey(project_name,channelID)
    monitoring.serviceAccount_deleteKey(project_name, channelID)

  if args.stackdriveriam:
    monitoring.iamrole(project_name,channelID)

  if args.stackdriverinstance:
    monitoring.instanceSetTag(project_name, channelID)
    monitoring.instanceAddAccessConfig(project_name, channelID)

  if args.stackdriverk8anonymous:
    monitoring.k8AnonymousCreate(project_name,channelID)
    monitoring.k8AnonymousPatch(project_name,channelID)

  print "[+] Dollhouse Deployment: Done "

if __name__ == "__main__":
  create_custom_metric()
  create_slack_notification(args.projectName, args.baseDirectory)
