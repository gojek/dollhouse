import json
import requests

def parse_tags(tags):
	parsed_tags = ''
	for tag in tags:
		parsed_tags += '• ' + tag + '\n'
	return parsed_tags
	

def gce_instance_set_tags(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('protoPayload').get('authenticationInfo').get('principalEmail')
	instance_name = message.get('protoPayload').get('resourceName').split('/')[-1]
	tags = message.get('protoPayload').get('request').get('tags')
	parsed_tags = parse_tags(tags)
	

	send_alert(token, url, channel, project_name, actor, instance_name, parsed_tags)

def send_alert(token, url, channel, project_name, actor, instance_name, parsed_tags):	

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#eb34d5",
				"fallback":"["+ project_name +"] GCE Instance Set Tags Alert",
				"title":"GCE Instance Tags",
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
						"title":"Tags",
						"value":parsed_tags
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

