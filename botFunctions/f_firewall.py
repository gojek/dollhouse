from netaddr import IPAddress
from utils.config import get_value
import os

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
    print "Firewall describe command found"
    response = os.popen("python dollhouse-audit.py --account " + running_account + " --firewall --project "+ command.split()[4] + " --firewall_name " + command.split()[2]).read()
    return response


