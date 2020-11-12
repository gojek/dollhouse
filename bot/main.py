from flask import Flask, jsonify, request

app = Flask(__name__)

import re
import os
import json
from threading import Thread

# for production, use the below imports
from commands.describe_helper import describe, describe_reply_message
from commands.idenfity_helper import identify, identify_reply_message
from commands.what_is_helper import what_is, what_is_reply_message


# # for vscode debugging, use the below imports
# from bot.commands.describe_helper import describe, describe_reply_message
# from bot.commands.idenfity_helper import identify, identify_reply_message
# from bot.commands.what_is_helper import what_is, what_is_reply_message

token = os.environ['SLACK_TOKEN']
url 	= 'https://slack.com/api/chat.postMessage'
pattern = r".+\s(describe|identify|what is|show)\s([@\.a-zA-Z0-9_-]+)\s(in)\s([a-zA-Z0-9_-]+)\s?$"
pattern = re.compile(pattern)

def process_message(request_json):
	request_json = json.loads(request_json)
	channel = request_json['event']['channel']
	# If the message is part of a thread slack message
	if request_json['event'].get('thread_ts'):
		thread_ts = request_json['event']['thread_ts']
	else:
		thread_ts = request_json['event']['event_ts']
	
	pattern_match = pattern.match(request_json['event']['text'])


	if pattern_match:
		command = pattern_match[1]
		if command == 'describe':
			firewall_name 	= pattern_match[2]
			project_name 	= pattern_match[4]
			output 			= describe(firewall_name, project_name)
			describe_reply_message(url, token, channel, thread_ts, output)
		elif command == 'identify':
			service_account_name = pattern_match[2]
			project_name 	= pattern_match[4]
			# Broken googleapis. Not Implemented!!!
			# output = identify(service_account_name, project_name)
			quit()
		elif command == 'what is':
			tag = pattern_match[2]
			project_name 	= pattern_match[4]
			output = what_is(tag, project_name)
			what_is_reply_message(url,token,channel,thread_ts,output)


	else:
		output = 'Malformed Command! Check your syntax!'

@app.route('/slack/events', methods=['POST'])
def verification():
	request.data = json.loads(request.data)
	if request.data['token'] == os.environ['VERIFICATION_TOKEN']:
		challenge = request.data.get('challenge')

		# Verify the challenge from slack
		if challenge is not None:
			return jsonify({"challenge":request.data['challenge']})

		# Spawn thread to process the data
		else:
			t = Thread(target=process_message, args=(json.dumps(request.data),))
			t.start()
			return jsonify({"status":"Success"})
		
	else:
		return jsonify({"status":"Fail", "reason":"Verification Failed!"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=6921)
