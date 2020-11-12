import os
import base64
import json

# for running in cloud function use these imports
from rules.firewall_insert import firewall_insert
from rules.firewall_patch import firewall_patch
from rules.firewall_delete import firewall_delete
from rules.service_account_create_key import service_account_create_key
from rules.service_account_delete_key import service_account_delete_key
from rules.gce_instance_set_tags import gce_instance_set_tags
from rules.gce_instance_add_access_config import gce_instance_add_access_config
from rules.k8s_anonymous_access import k8s_anonymous_access
from rules.k8s_public_cluster import k8s_public_cluster
from rules.iam_changes import iam_changes
from rules.storage_allusers import storage_allusers

# # for vscode use these imports
# from cloudfunction.rules.firewall_insert import firewall_insert
# from cloudfunction.rules.firewall_patch import firewall_patch
# from cloudfunction.rules.firewall_delete import firewall_delete
# from cloudfunction.rules.service_account_create_key import service_account_create_key
# from cloudfunction.rules.service_account_delete_key import service_account_delete_key
# from cloudfunction.rules.gce_instance_set_tags import gce_instance_set_tags
# from cloudfunction.rules.gce_instance_add_access_config import gce_instance_add_access_config
# from cloudfunction.rules.k8s_anonymous_access import k8s_anonymous_access
# from cloudfunction.rules.k8s_public_cluster import k8s_public_cluster
# from cloudfunction.rules.iam_changes import iam_changes
# from cloudfunction.rules.storage_allusers import storage_allusers


token 	= os.environ['SLACK_TOKEN']
url 	= 'https://slack.com/api/chat.postMessage'
channel = os.environ['SLACK_CHANNEL']

def receive_request(event, context):
	"""Triggered from a message on a Cloud Pub/Sub topic.
	Args:
		 event (dict): Event payload.
		 context (google.cloud.functions.Context): Metadata for the event.
	"""
	pubsub_message = base64.b64decode(event['data']).decode('utf-8')
	parse_message(pubsub_message)
	print(pubsub_message)

def parse_message(message):

	message = json.loads(message)
	# Firewall Insert
	try:
		if (message.get('resource').get('type')=='gce_firewall_rule') and (message.get('protoPayload').get('authorizationInfo')[0].get('resourceAttributes').get('type')=='compute.firewalls') and ('compute.firewalls.insert' in message.get('protoPayload').get('methodName')) :
			firewall_insert(message, token, url, channel)
			print('Firewall Insert')
	except:
		pass

	# Firewall Patch
	try:
		if (message.get('resource').get('type')=='gce_firewall_rule') and (message.get('protoPayload').get('authorizationInfo')[0].get('resourceAttributes').get('type')=='compute.firewalls') and ('compute.firewalls.patch' in message.get('protoPayload').get('methodName')) :
			firewall_patch(message, token, url, channel)
			print('Firewall Patch')
	except:
		pass

	# Firewall Delete
	try:
		if (message.get('resource').get('type')=='gce_firewall_rule') and (message.get('protoPayload').get('authorizationInfo')[0].get('resourceAttributes').get('type')=='compute.firewalls') and ('compute.firewalls.delete' in message.get('protoPayload').get('methodName')) :
			firewall_delete(message, token, url, channel)
			print('Firewall Delete')
	except:
		pass

	# Service Account Create Key
	try:
		if (message.get('resource').get('type')=='service_account') and ('CreateServiceAccountKey' in message.get('protoPayload').get('methodName')) :
			service_account_create_key(message, token, url, channel)
			print('Service Account CreateKey')
	except:
		pass

	# Service Account Delete Key
	try:
		if (message.get('resource').get('type')=='service_account') and ('DeleteServiceAccountKey' in message.get('protoPayload').get('methodName')) :
			service_account_delete_key(message, token, url, channel)
			print('Service Account DeleteKey')
	except:
		pass

	# GCE Instance Set Tags
	try:
		if (message.get('resource').get('type')=='gce_instance') and ('compute.instances.setTags' in message.get('protoPayload').get('methodName')) and (message.get('operation').get('first')==True) :
			gce_instance_set_tags(message, token, url, channel)
			print('GCE Instance Set Tags')
	except:
		pass

	# GCE Instance Add Access Config
	try:
		if (message.get('resource').get('type')=='gce_instance') and ('compute.instances.addAccessConfig' in message.get('jsonPayload').get('event_subtype')) and (message.get('jsonPayload').get('event_type')=='GCE_OPERATION_DONE') :
			gce_instance_add_access_config(message, token, url, channel)
			print('GCE Instance Add Access Config')
	except:
		pass

	# Kubernetes Role Binding System Anonymous
	try:
		subjects = message.get('protoPayload').get('response').get('subjects')
		system_anonymous = ["system:anonymous" in subject['name'] for subject in subjects]
		if (message.get('resource').get('type')=="k8s_cluster" and (True in system_anonymous) and (('clusterrolebindings.create' in message.get('protoPayload').get('methodName')) or ('clusterrolebindings.patch' in message.get('protoPayload').get('methodName'))) ):
			k8s_anonymous_access(message, token, url, channel)
			print('Kubernetes Role Binding System Anonymous')
	except:
		pass

	# Kubernetes Public Cluster
	try:
		if (message.get('resource').get('type')=="gke_cluster" and ('ClusterManager.CreateCluster' in message.get('protoPayload').get('methodName')) ):
			k8s_public_cluster(message, token, url, channel)
			print('Kubernetes Public Cluster')
	except:
		pass

	# IAM Changes
	try:
		if ( (message.get('resource').get('type')=="project" and (message.get('protoPayload').get('methodName'))=='SetIamPolicy') and len(message.get('protoPayload').get('serviceData').get('policyDelta').get('bindingDeltas')) ) > 0:
			iam_changes(message, token, url, channel)
			print('IAM Changes')
	except:
		pass

	# Cloud Storage Permission Changes
	try:
		members = message.get('protoPayload').get('serviceData').get('policyDelta').get('bindingDeltas')
		allUsers = ["allUsers" in member['member'] for member in members]
		if (message.get('protoPayload').get('serviceName')=='storage.googleapis.com' and (True in allUsers)):
			storage_allusers(message, token, url, channel)
			print('Cloud Storage Permission Changes')
	except:
		pass

