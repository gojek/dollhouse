import json
import requests
import yaml
import pathlib
import ipaddress

current_directory = str(pathlib.Path(__file__).parent.absolute())
with open(current_directory + "/whitelist.yaml","r") as whitelist_file:
	whitelist = yaml.safe_load(whitelist_file)

with open(current_directory + "/config.yaml","r") as config_file:
	cfg = yaml.safe_load(config_file)

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

def check_whitelist(alloweds):
	for allowed in alloweds:
		prev_port_length = len(allowed.ports)
		for port in reversed(allowed.ports):
			item = allowed.protocol + ' ' + port
			if item in whitelist['firewall']:
				allowed.ports.remove(port)

		if (len(allowed.ports) == 0) and (len(allowed.ports) < prev_port_length):
			alloweds.pop()

def check_private_ip(sourceRanges):
	for source in reversed(sourceRanges):
		ip = source.split('/')[0]
		if ip == '0.0.0.0':
			continue
		is_private = ipaddress.ip_address(ip).is_private
		if is_private:
			sourceRanges.remove(source)

def firewall_insert(message, token, url, channel):
	project_name = message.get('resource').get('labels').get('project_id')
	actor = message.get('protoPayload').get('response').get('user')
	firewall_name = message.get('protoPayload').get('request').get('name')
	direction = message.get('protoPayload').get('request').get('direction')
	alloweds = message.get('protoPayload').get('request').get('alloweds')
	alloweds = parse_protocol(alloweds)
	check_whitelist(alloweds)
	# TODO: check for denieds
	sourceRanges = message.get('protoPayload').get('request').get('sourceRanges')
	if "PUBLIC_IP_ONLY" in cfg['configuration']:
		check_private_ip(sourceRanges)
	targetTags = message.get('protoPayload').get('request').get('targetTags')

	# Alert if there is no whitelisted protocol/port
	if (len(alloweds) > 0) and (len(sourceRanges) > 0):
		send_alert(token, url, channel, project_name, actor, firewall_name, direction, alloweds, sourceRanges, targetTags)

def send_alert(token, url, channel, project_name, actor, firewall_name, direction, alloweds, sourceRanges, targetTags):	
				
	# if str(type(output)) != "<class 'bot.commands.describe_helper.Firewall'>":
	# 	data.update({"text":str(output)})
	# 	r = requests.post(url=url, data=data)
	# 	quit()

	parsed_protocol = ""
	for protocol in alloweds:
		if protocol.ports != '':
			parsed_protocol += "`" + protocol.protocol.upper() + "`\n"
			if len(protocol.ports) > 1:
				for port in protocol.ports:
					parsed_protocol += "• " + str(port) + " \n"
			else:
				parsed_protocol += "• " + str(protocol.ports[0]) + " \n"
		else:
			parsed_protocol += "`" + protocol.protocol.upper() + "` \n"

	attachments = [
			{
				"mrkdwn_in":[
					"text",
					"value"
				],
				"color":"#36a64f",
				"fallback":"["+ project_name +"] Firewall Insert Alert",
				"title":"Firewall Insert",
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
						"title":"Firewall Name",
						"value":firewall_name
					},
					{
						"title":"Protocol",
						"value":parsed_protocol,
						"short":True
					},
					{
						"title":"Source",
						"value":str(sourceRanges),
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
