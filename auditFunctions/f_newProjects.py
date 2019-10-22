import os
from botFunctions import f_slackHelper

base_dir = os.path.dirname(os.path.realpath(__file__))
difference = []

def get_todayProject():
    if os.path.isfile(base_dir + '/yesterday_projects.lst'):
        os.system('rm ' + base_dir + '/yesterday_projects.lst')

    if os.path.isfile(base_dir + '/today_projects.lst'):
        os.system('mv ' + base_dir + '/today_projects.lst ' + base_dir + '/yesterday_projects.lst')
    
    os.system("gcloud projects list | awk -F ' ' '{print $1}' | grep -v 'sys-' > " + base_dir + "/today_projects.lst")

def check_diff():
    with open(base_dir + '/today_projects.lst') as today, open(base_dir + '/yesterday_projects.lst') as yesterday:
        diff = set(today).difference(set(yesterday))
        if len(diff) != 0:
            f_slackHelper.newProjects_slack(diff)


get_todayProject()
check_diff()
