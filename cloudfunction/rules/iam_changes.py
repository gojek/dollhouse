import json
import requests
import yaml
import pathlib

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

def check_whitelist(members):
	for member in reversed(members):
		if member.role in whitelist['iam']:
			members.remove(member)
			

def iam_changes(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('protoPayload').get('authenticationInfo').get('principalEmail')
	members = message.get('protoPayload').get('serviceData').get('policyDelta').get('bindingDeltas')
	members = parse_members(members)
	check_whitelist(members)

	# Alert if there is no whitelisted member
	if len(members) > 0:
		send_alert(token, url, channel, project_name, actor, members)

def send_alert(token, url, channel, project_name, actor, members):	

	parsed_member = ""
	for member in members:
		parsed_member += "*" + member.action + "* \n\t‣`Member`: " + member.member + "\n\t‣`Role`: " + member.role + "\n\n"

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#800000",
				"fallback":"["+ project_name +"] IAM Role Change Alert",
				"title":"IAM Role Change",
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

