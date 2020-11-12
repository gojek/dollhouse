import requests
import json
from googleapiclient import discovery
from googleapiclient.http import BatchHttpRequest
from google.oauth2 import service_account
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)

class Instance:
	def __init__(self, name, ip):
		self.name = name
		self.ip = ip

class Firewall:
	def __init__(self, project, name, sourceRanges, allowed, targetTags, direction, affected_instances):
		self.project = project
		self.name = name
		self.sourceRanges = sourceRanges
		self.allowed = allowed
		self.targetTags = targetTags
		self.direction = direction
		self.affected_instances = affected_instances

class Protocol:
	def __init__(self, protocol, ports):
		self.protocol = protocol
		self.ports = ports

def describe(firewall_name, project_name):
	try:
		request = service.firewalls().get(project=project_name, firewall=firewall_name)
		response = request.execute()
		
		sourceRanges = response.get('sourceRanges')
		allowed = response.get('allowed')
		if allowed is None:
			raise Exception('422, Egress Direction')

		targetTags = response.get('targetTags')
		direction = response.get('direction')

		# Parse the allowed ports
		allowed = parse_protocol(allowed)

		# If targetTags is empty, the firewall rule is applied to all instances
		if targetTags is None:
			affected_instances = 'All Instances'
		else:
			affected_instances = get_affected_instances(project_name, targetTags)
		
		output = Firewall(project_name, firewall_name, sourceRanges, allowed, targetTags, direction, affected_instances)
		return output
	except Exception as e:
		return(e)

def parse_protocol(allowed):
	output = []
	for item in allowed:
		protocol = item['IPProtocol']
		ports = item.get('ports')
		if ports is None:
			ports = ''
		output.append(Protocol(protocol, ports)) 
	return output

def list_zones(project_name):
	request = service.zones().list(project=project_name)
	response = request.execute()
	zones = [zone['name'] for zone in response['items']]
	return zones	

def get_affected_instances(project_name, targetTags):
	affected_instances = []
	instances_list = []
	zones = list_zones(project_name)

	batch = service.new_batch_http_request()

	for zone in zones:
		batch.add(service.instances().list(project=project_name, zone=zone))

	batch.execute()

	for i in batch._responses:
		if json.loads(batch._responses[i][1]).get('items') is not None:
			for instance in json.loads(batch._responses[i][1]).get('items'):
				instances_list.append(instance)

	for tag in targetTags:
		for instance in instances_list:
			if (instance.get('tags').get('items') is not None) and (tag in instance.get('tags').get('items')):
				instance_name = instance['name']
				try:
					instance_ip = "`" + str(instance.get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP')) + "`"
					if instance.get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP') is None:
						instance_ip = ''
				except:
					instance_ip = ''
				affected_instances.append(Instance(instance_name, instance_ip))

	return affected_instances

def describe_reply_message(url, token, channel, thread_ts, output):	
	data = {
			'token'     : token,
			'channel'   : channel,    
			'thread_ts' : thread_ts
	}
				
	if 'commands.describe_helper.Firewall' not in str(type(output)):
		data.update({"text":str(output)})
		r = requests.post(url=url, data=data)
		quit()


	parsed_affected_instances = ""
	if output.affected_instances == 'All Instances':
		parsed_affected_instances = '`All Instances`'
	else:
		for instance in output.affected_instances:
			parsed_affected_instances += "• " + instance.name + " " + instance.ip + " \n"

	parsed_protocol = ""
	for protocol in output.allowed:
		if protocol.ports != '':
			parsed_protocol += "`" + protocol.protocol + "`\n"
			if len(protocol.ports) > 1:
				for port in protocol.ports:
					parsed_protocol += "• " + str(port) + " \n"
			else:
				parsed_protocol += "• " + str(protocol.ports[0]) + " \n"
		else:
			parsed_protocol += "`" + protocol.protocol + "` \n"

	attachments =  [
		{
			"mrkdwn_in": ["text","value"],
			"color": "#36a64f",
			"fallback": "Query for " + output.name,
			"fields": [
				{
					"title": "Project",
					"value": output.project,
					"short": True
				},
				{
					"title": "Name",
					"value": output.name,
					"short": True
				},      
				{
					"title": "Direction",
					"value": output.direction,
					"short": True
				},
				{
					"title": "Protocol",
					"value": parsed_protocol,
					"short": True
				},
				{
					"title": "Source",
					"value": str(output.sourceRanges),
					"short": True
				},
				{
					"title": "Affected Instances",
					"value": parsed_affected_instances
				}
			],
			"footer": "dollhouse",
			"footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png"
		}
	]


	data.update({"attachments": json.dumps(attachments)})
	r = requests.post(url=url, data=data)
