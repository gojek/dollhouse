import json
import requests

def k8s_public_cluster(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('protoPayload').get('authenticationInfo').get('principalEmail')
	cluster_name = message.get('resource').get('labels').get('cluster_name')
	
	send_alert(token, url, channel, project_name, actor, cluster_name)

def send_alert(token, url, channel, project_name, actor, cluster_name):	

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#e1eb34",
				"fallback":"["+ project_name +"] k8s Public Cluster",
				"title":"Kubernetes Public Cluster",
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
