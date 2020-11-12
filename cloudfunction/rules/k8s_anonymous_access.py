import json
import requests

def k8s_anonymous_access(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('protoPayload').get('authenticationInfo').get('principalEmail')
	cluster_name = message.get('protoPayload').get('response').get('metadata').get('name')
	role = message.get('protoPayload').get('response').get('roleRef').get('name')
	
	send_alert(token, url, channel, project_name, actor, cluster_name, role)

def send_alert(token, url, channel, project_name, actor, cluster_name, role):	

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#e1eb34",
				"fallback":"["+ project_name +"] k8s System Anonymous",
				"title":"Kubernetes System Anonymous Access",
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
						"title":"Cluster",
						"value": cluster_name,
						"short":True
					},
					{
						"title":"Role",
						"value":role,
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

