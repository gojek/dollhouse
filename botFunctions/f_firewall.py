from netaddr import IPAddress
from utils.config import get_value
import os
import json
import datetime

def check_IP_private(source):
    counter = 0
    source_range1 = source[1:][:-1]
    source_range2 = source_range1.replace("'","")
    source_range3 = source_range2.replace(",","")
    list_source_range = source_range3.split()

    for sources in list_source_range:
        ip_to_check = sources.split('/')[0]
        is_private = IPAddress(ip_to_check).is_private()
        if is_private is True:
            continue
        else:
            counter = counter + 1

    if counter > 0:
        return False
    else:
        return True

def check_port_range(ports):
    #if port is a range
    if '-' in ports:
        if 'tcp' in ports:
            prange_begin = ports.split('tcp')[1].split('-')[0]
            prange_end = ports.split('tcp')[1].split('-')[1]
            return range(int(prange_begin),int(prange_end)+1)

        elif 'udp' in ports:
            prange_begin = ports.split('udp')[1].split('-')[0]
            prange_end = ports.split('udp')[1].split('-')[1]
            return range(int(prange_begin),int(prange_end)+1)

    #if it is a single port
    else:
        return False

def check_whitelisted_ports(ports_list):
    rval = False
    whitelisted_ports = get_value('noShowPorts', 'ports').split(',')


    for item in ports_list:
        abc = check_port_range(item)
        if abc is False:
            if item in whitelisted_ports:
                rval = True # port is whitelisted
            else:
                rval = False # port is not whitelisted
                break
        else:
            #check if it is TCP or UDP
            if item.startswith('tcp'):
                abc = ['tcp' + str(s) for s in abc]
            elif item.startswith('udp'):
                abc = ['udp' + str(s) for s in abc]

            return check_whitelisted_ports(abc)

    return rval

def firewall_describe_command(command,running_account):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: Firewall describe command found')
    response = os.popen("python dollhouse-audit.py --account " + running_account + " --firewall --project "+ command.split()[4] + " --firewall_name " + command.split()[2]).read()
    return response

def what_is_command(command,running_account):
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[' + currentTime + '] [*] DEBUG: WHAT IS command found')
    response = ''
    check_existence = os.popen("gcloud compute firewall-rules list --format=json | grep " + command.split()[3]).read()
    if check_existence is not '':
        tmp_json = os.popen('gcloud compute firewall-rules list --format=json').read()
        tmp_json = json.loads(tmp_json)

        for i in tmp_json:
            try:
                if str(i['targetTags'][0]) == str(command.split()[3]):
                    response = str(i['name'])
            except:
                pass

    if response == '':
        response = '*' + str(command.split()[3]) + '* is not a firewall tag'
        return response
    else:
        response = '@dollhouse describe ' + str(command.split()[3]) + ' in ' + str(command.split()[5])
        return firewall_describe_command(response,running_account)
