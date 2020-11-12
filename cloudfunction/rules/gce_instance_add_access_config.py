import json
import requests
from googleapiclient import discovery
from google.oauth2 import service_account
from oauth2client.client import GoogleCredentials

def get_public_ip(project_name, instance_zone, instance_name):
	credentials = GoogleCredentials.get_application_default()
	service = discovery.build('compute', 'v1', credentials=credentials)
	request = service.instances().get(project=project_name, zone=instance_zone, instance=instance_name)
	response = request.execute()
	public_ip = str(response.get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP'))
	return public_ip
	

def gce_instance_add_access_config(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('jsonPayload').get('actor').get('user')
	instance_name = message.get('jsonPayload').get('resource').get('name')
	instance_zone = message.get('jsonPayload').get('resource').get('zone')
	public_ip = get_public_ip(project_name, instance_zone, instance_name)
	

	send_alert(token, url, channel, project_name, actor, instance_name, instance_zone, public_ip)

def send_alert(token, url, channel, project_name, actor, instance_name, instance_zone, public_ip):	

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#eb34d5",
				"fallback":"["+ project_name +"] GCE Instance New Public IP",
				"title":"GCE New Public IP",
				"fields":[
					{
						"title":"Project",
						"value": project_name,
						"short":True
					},
					{
						"title":"Actor",
						"value": actor,
						"short":True
					},
					{
						"title":"Instance",
						"value": instance_name,
					},
					{
						"title":"Zone",
						"value":instance_zone,
						"short":True
					},
					{
						"title":"Public IP",
						"value":public_ip,
						"short":True
					}
				],
				"footer":"dollhouse",
				"footer_icon":"https://platform.slack-edge.com/img/default_application_icon.png"
		}
	]
	
	data = {
			'token'     : token,
			'channel'   : channel,  
			'attachments': json.dumps(attachments)
	}




	requests.post(url=url, data=data)

