import requests
import json
from googleapiclient import discovery
from google.oauth2 import service_account
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)

def what_is(tag, project_name):
	try:
		tags = set()
		request = service.firewalls().list(project=project_name)
		while request is not None:
			response = request.execute()
			try:
				for item in response['items']:
					try:
						for t in item['targetTags']:
							tags.add(t)
					except:
						pass
			except:
				pass
			request = service.firewalls().list_next(previous_request=request, previous_response=response)

		if tag in tags:
			output = '✅ ' + tag + ' is a firewall tag'
		else:
			output = '❌ ' + tag + ' is not a firewall tag'
		return output
	except Exception as e:
		return(e)

def what_is_reply_message(url, token, channel, thread_ts, output):	

	data = {
			'token'     : token,
			'channel'   : channel,    
			'thread_ts' : thread_ts,
	}
				
	if 'firewall tag' not in output:
		data.update({"text":str(output)})
		requests.post(url=url, data=data)
		quit()

	data.update({"text":output})
	requests.post(url=url, data=data)
