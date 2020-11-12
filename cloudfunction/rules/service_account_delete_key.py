import json
import requests

class Protocol:
	def __init__(self, protocol, ports):
		self.protocol = protocol
		self.ports = ports

def parse_protocol(alloweds):
	output = []
	for item in alloweds:
		protocol = item['IPProtocol']
		ports = item.get('ports')
		if ports is None:
			ports = ''
		output.append(Protocol(protocol, ports)) 
	return output

def service_account_delete_key(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('protoPayload').get('authenticationInfo').get('principalEmail')
	service_account_name = message.get('resource').get('labels').get('email_id')
	

	send_alert(token, url, channel, project_name, actor, service_account_name)

def send_alert(token, url, channel, project_name, actor, service_account_name):	

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#42f5e3",
				"fallback":"["+ project_name +"] Service Account DeleteKey Alert",
				"title":"Service Account DeleteKey",
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
						"title":"Service Account",
						"value":service_account_name
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

