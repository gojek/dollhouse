from utils.config import get_value
import os

def check_blacklisted_roles(role):
    roles_list = get_value('showRoles','roles').split(",")

    for item in roles_list:
        if role.lower() == item:
            return True #Role is blacklisted
        else:
            continue
            #return False #Role is not blacklisted

def check_whitelisted_domain(email):
    finalStatus = False
    whitelisted_domain_list = ['go-jek.com','go-pay.co.id','aux.go-jek.com', 'gserviceaccount.com']
    whitelisted_domain_list = whitelisted_domain_list.split(',')
    status = [email.endswith(item) for item in whitelisted_domain_list]
    if True in status:
        finalStatus = True
    return finalStatus


def iam_show_command(command):
    print "IAM command show found"
    response = os.popen("gcloud iam roles describe " + command.split()[2] + " --project " + command.split()[4]).read()
    return response