import os
import json


def get_logging_status(bucket_name):
    print('[*] Geting logging status for bucket ' + bucket_name)
    res = os.popen('gsutil logging get gs://' + bucket_name + '/').read()
    logging_status = False
    if 'has no logging configuration' in res:
        print('[*] Logging status for bucket ' + bucket_name + ' : False')
    else:
        logging_status = True
        print('[*] Logging status for bucket ' + bucket_name + ' : True')
    
    return logging_status

def get_bucket_iam(bucket_name):
    raw_iam = os.popen('gsutil iam get gs://' + bucket_name).read()
    json_raw_iam = json.loads(raw_iam)

    list_to_tabulate = []
    
    for item in json_raw_iam['bindings']:
        for member in item['members']:
            linky = []
            role = item['role']
            members = member
            linky.append(role)
            linky.append(member)
            list_to_tabulate.append(linky)
    return list_to_tabulate
