import os
import json

def serviceAccount_identify_command(command):
    print "ServiceAccount identify command found"
    raw_logging = os.popen("gcloud logging read '"+command.split()[2].split(':')[1].split('|')[0]+" AND protoPayload.methodName=SetIamPolicy' --project " + command.split()[4] + " --format=json").read()
    json_logging = json.loads(raw_logging)
    response = str(json_logging[0].get('protoPayload').get('authenticationInfo').get('principalEmail')) + " Created this Service Account"
    return response