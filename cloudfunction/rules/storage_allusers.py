import json
import requests
import yaml
import pathlib
import fnmatch

current_directory = str(pathlib.Path(__file__).parent.absolute())
with open(current_directory + "/whitelist.yaml","r") as ymlfile:
	whitelist = yaml.safe_load(ymlfile)

class Member:
	def __init__(self, action, role, member):
		self.action = action
		self.role = role
		self.member = member

def parse_members(members):
	output = []
	for item in members:
		action = item['action']
		role = item['role']
		member = item['member']
		output.append(Member(action, role, member)) 
	return output

def check_whitelist(resource_name):
	for whitelisted_resource in whitelist['bucket']:
		matches = fnmatch.filter(list(resource_name.split(' ')),whitelisted_resource)
		if len(matches) > 0:
			return True

def storage_allusers(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('protoPayload').get('authenticationInfo').get('principalEmail')
	members = message.get('protoPayload').get('serviceData').get('policyDelta').get('bindingDeltas')
	members = parse_members(members)
	resource_name = message.get('protoPayload').get('resourceName').split('projects/_/')[1]
	whitelisted = check_whitelist(resource_name)

	if not whitelisted:
		send_alert(token, url, channel, project_name, actor, members, resource_name)

def send_alert(token, url, channel, project_name, actor, members, resource_name):	

	parsed_member = ""
	for member in members:
		parsed_member += "*" + member.action + "* \n\t‣`Member`: " + member.member + "\n\t‣`Role`: " + member.role + "\n\n"

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#e37b3b",
				"fallback":"["+ project_name +"] Cloud Storage Public Bucket Alert",
				"title":"Cloud Storage Public Bucket",
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
						"title":"Resource",
						"value": resource_name,
						"short":True
					},
					{
						"title":"Changes",
						"value": parsed_member,
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

