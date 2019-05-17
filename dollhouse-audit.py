import json
import os
import ast
import argparse
from elasticsearch import Elasticsearch
import requests
import datetime
from tabulate import tabulate
import time
from auditFunctions import f_storage
import pdb

parser = argparse.ArgumentParser(description='GCP Audit Tool')
parser.add_argument("--account", dest="account", help="account to run this tool with -> ex: youremail@gmail.com")
parser.add_argument("--es", dest="elasticsearch", help="formats to json and pushes to elastic search", required=False)
parser.add_argument("--firewall", help="run firewall rules check",required=False, action='store_true')
parser.add_argument("--iam", help="run IAM Users & Service Accounts check", required=False, action='store_true')
parser.add_argument("--bucket", help="run bucket check", required=False, action='store_true')
parser.add_argument("--project", dest="project", help="query specific project", required=False)
parser.add_argument("--firewall_name", dest="firewall_name", help="query specific firewall name", required=False)

args = parser.parse_args()
gcloud_path = "gcloud" #"/usr/bin/gcloud"
cmd_set_acccount = "%s config set account %s" % (gcloud_path, args.account)
project_list = []
instances = []
if args.elasticsearch:
	global es 
	es = Elasticsearch([{'host': args.elasticsearch, 'port': 9200}])
else:
	pass
now = datetime.datetime.now()
now_strftime = now.strftime("%Y-%m-%d")


def get_project_list():

	if args.project:
		project_list.append(args.project)
	else:
		os.popen(cmd_set_acccount)

		# command get all projects in json format
		cmd_projects = "%s projects list --format=json" % (gcloud_path)
		# get all projects in json format and assign it to a variable `projects`
		projects = json.loads(os.popen(cmd_projects).read())

		print "[*] Collecting Project list from GCP"
		# append the projectId to a dict `project_list`
		for project in projects:
			project_list.append(project.get('projectId'))

		# print the number of projects in GCP
		print "[*] Found %s projects in GCP" % (len(project_list))

	return project_list

def getIAMUsers(project_name):
	cmd = "%s projects get-iam-policy %s --format=json --quiet" % (gcloud_path, project_name)
	raw_IAMUsers = os.popen(cmd).read()

	iam_list_serviceAccount = []
	iam_list_user = []
	iam_list_serviceAccount_user = []
	iam_list_user_user = []
	iam_list_serviceAccount_user_unique = []
	iam_list_user_user_unique = []
	iam_list_serviceAccount_tabulate = []
	iam_list_user_tabulate = []
	
	

	if "Enabling" not in raw_IAMUsers:
		try:
			iam_users = json.loads(raw_IAMUsers)
			
			raw_iam_users = iam_users.get('bindings')
			for i in range(len(raw_iam_users)):
				for x in range(len(raw_iam_users[i].get('members'))):
					iam_json_user = {}
					iam_json_serviceAccount = {}
					if 'serviceAccount' in raw_iam_users[i].get('members')[x]:
						iam_json_serviceAccount['role'] = str(raw_iam_users[i].get('role').split('roles/')[1])
						iam_json_serviceAccount['user'] = str(raw_iam_users[i].get('members')[x].split('serviceAccount:')[1])
						iam_list_serviceAccount.append(iam_json_serviceAccount)
					elif 'user' in raw_iam_users[i].get('members')[x]:
						iam_json_user['role'] = str(raw_iam_users[i].get('role').split('roles/')[1])
						iam_json_user['user'] = str(raw_iam_users[i].get('members')[x].split('user:')[1])
						iam_list_user.append(iam_json_user)

			for i in range(len(iam_list_serviceAccount)):
				iam_list_serviceAccount_user.append(iam_list_serviceAccount[i].get('user'))
			iam_list_serviceAccount_user_unique = list(set(iam_list_serviceAccount_user))

			print """
+----------------------------------------------+
| ______________Service Accounts______________ |
+----------------------------------------------+"""	
			for i in range(len(iam_list_serviceAccount_user_unique)):
				currentAccount = str(iam_list_serviceAccount_user_unique[i])
				for x in range(len(iam_list_serviceAccount)):
					if iam_list_serviceAccount[x].get('user') == currentAccount:
						linky = []
						json_serviceAccount = {}
						json_serviceAccount['project_name'] = str(project_name)
						json_serviceAccount['user'] = currentAccount
						json_serviceAccount['role'] = iam_list_serviceAccount[x].get('role')
						json_serviceAccount['scan_time'] = now_strftime
						if args.elasticsearch:
							es.index(index='dollhouse', doc_type='dollhouse_serviceAccount', body=json_serviceAccount)
						linky.append(currentAccount)
						linky.append(iam_list_serviceAccount[x].get('role'))
						iam_list_serviceAccount_tabulate.append(linky)

					else:
						continue
			print tabulate(iam_list_serviceAccount_tabulate, ["User", "Role"], tablefmt="grid")

			print """
+---------------------------------------+
| ______________IAM Users______________ |
+---------------------------------------+"""
			for i in range(len(iam_list_user)):
				iam_list_user_user.append(iam_list_user[i].get('user'))
			iam_list_user_user_unique = list(set(iam_list_user_user))


			for i in range(len(iam_list_user_user_unique)):
				currentAccount = str(iam_list_user_user_unique[i])
				for x in range(len(iam_list_user)):
					if iam_list_user[x].get('user') == currentAccount:
						linky = []
						json_iam = {}
						json_iam['project_name'] = str(project_name)
						json_iam['user'] = currentAccount
						json_iam['role'] = iam_list_user[x].get('role')
						json_iam['scan_time'] = now_strftime
						if args.elasticsearch:
							es.index(index='dollhouse', doc_type='dollhouse_IAM', body=json_iam)
						linky.append(currentAccount)
						linky.append(iam_list_user[x].get('role'))
						iam_list_user_tabulate.append(linky)
					else:
						continue
			print tabulate(iam_list_user_tabulate, ["User", "Role"], tablefmt="grid")
			return iam_users

		except:
			print "[-] Problem getting IAM Users for Project: %s" % (project_name)
			return None

def get_instances_by_project(project_name):

	# command to get all instances in a `project_name`
	cmd = "%s compute instances list --project=%s --format=json --quiet" % (gcloud_path, project_name)

	print "[*] Getting instances for Project: '%s'" % (project_name)
	# get all instances and print save it to a variable `raw_instances`
	raw_instances = os.popen(cmd).read()

	if "Enabling" not in raw_instances:
		try:
			instances = json.loads(raw_instances)
			return instances
		except:
			print "[-] Problem getting instances for Project: %s" % (project_name)
			return None

def get_firewall_rules():


	for project_name in project_list:
		cmd = "%s compute firewall-rules list --project=%s --format=json --quiet" % (gcloud_path, project_name)
		print "+---------------------------------------------------++---------------------------------------------------+"
		print "					\033[1m  %s  \033[0m 				" % (project_name)
		print "+---------------------------------------------------++---------------------------------------------------+"
		raw_firewall = os.popen(cmd).read()

		if "Enabling" not in raw_firewall:
			try:
				instances = get_instances_by_project(project_name)
				if args.iam:
					print "[*] Getting IAM Users for Project: '%s'" % (project_name)
					time.sleep(2)
					iam_users = getIAMUsers(project_name)

				if args.firewall:
					print "[*] Getting firewall rules for Project: '%s'" %(project_name)
					time.sleep(2)
					firewall = json.loads(raw_firewall)
					query_firewall(firewall,project_name,instances)
				
				if args.bucket:
					print('[*] Getting Buckets for Project: ' + project_name)
					time.sleep(2)
					audit_storage(project_name)
				else: 
					continue
				
			except:
				print "[-] Problem getting firewall-rules for Project: %s" % (project_name)

def query_firewall(firewall,project_name,instances):
	for i in range(len(firewall)):
		json_body = {}
		instance_name_list = []
		instance_ip_list = []
		json_body['scan_time'] = now_strftime
		json_body['project_name'] = project_name
		
		if args.firewall_name:
			if firewall[i].get('name') == args.firewall_name:
				print "Name: " + firewall[i].get('name')
				json_body['firewall_name'] = firewall[i].get('name')
				print "Direction: " + firewall[i].get('direction')
				json_body['direction'] = firewall[i].get('direction')
				if str(firewall[i].get('direction')) == 'INGRESS':
					try:
						print "Source Range: " + str(ast.literal_eval(json.dumps(firewall[i].get('sourceRanges'))))
						json_body['source_range'] = str(ast.literal_eval(json.dumps(firewall[i].get('sourceRanges')))) 
					except:
						print "Source Tags: " + str(ast.literal_eval(json.dumps(firewall[i].get('sourceTags'))))
						json_body['source_tags'] = str(ast.literal_eval(json.dumps(firewall[i].get('sourceTags'))))
					try:
						print "Allowed: " + str(ast.literal_eval(json.dumps(firewall[i].get('allowed'))))
						json_body['allowed'] = str(ast.literal_eval(json.dumps(firewall[i].get('allowed'))))
					except:
						print "Denied: " + str(ast.literal_eval(json.dumps(firewall[i].get('denied'))))
						json_body['denied'] = str(ast.literal_eval(json.dumps(firewall[i].get('denied'))))
				try:
					firewall_tag = str(ast.literal_eval(json.dumps(firewall[i].get('targetTags'))))[2:-2]
					print "Tag: " + firewall_tag
					json_body['tag'] = firewall_tag
					print "+---------------------------------------------------+"
					print "		Affected Instances 				"
					print "+---------------------------------------------------+"
					for x in range(len(instances)):
						try:
							for k in range(len(instances[x].get('tags').get('items'))):
								if str(ast.literal_eval(json.dumps(instances[x].get('tags').get('items')[k]))) == firewall_tag:
									try:
										print instances[x].get('name') + "\t\t" + instances[x].get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP')
										instance_name_list.append(instances[x].get('name'))
										instance_ip_list.append(instances[x].get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP'))
									except:
										print instances[x].get('name')
										instance_name_list.append(instances[x].get('name'))
										instance_ip_list.append('N/A')

						except:
							pass
					json_body['instance_name'] = instance_name_list
					json_body['public_ip'] = instance_ip_list
					print "-----------------------------------------------------\n\n\n"
				
				except:
					print "+---------------------------------------------------+"
					print "		Affected Instances 				"
					print "+---------------------------------------------------+"
					print "*** APPLIED TO ALL ***\n\n\n"
					# WIP : NEED TO PUT ALL INSTANCE NAMES HERE
					json_body['instance_name'] = "APPLIED TO ALL"
			else:
				continue
		else:
			print "Name: " + firewall[i].get('name')
			json_body['firewall_name'] = firewall[i].get('name')
			print "Direction: " + firewall[i].get('direction')
			json_body['direction'] = firewall[i].get('direction')
			if str(firewall[i].get('direction')) == 'INGRESS':
				try:
					print "Source Range: " + str(ast.literal_eval(json.dumps(firewall[i].get('sourceRanges'))))
					json_body['source_range'] = str(ast.literal_eval(json.dumps(firewall[i].get('sourceRanges')))) 
				except:
					print "Source Tags: " + str(ast.literal_eval(json.dumps(firewall[i].get('sourceTags'))))
					json_body['source_tags'] = str(ast.literal_eval(json.dumps(firewall[i].get('sourceTags'))))
				try:
					print "Allowed: " + str(ast.literal_eval(json.dumps(firewall[i].get('allowed'))))
					json_body['allowed'] = str(ast.literal_eval(json.dumps(firewall[i].get('allowed'))))
				except:
					print "Denied: " + str(ast.literal_eval(json.dumps(firewall[i].get('denied'))))
					json_body['denied'] = str(ast.literal_eval(json.dumps(firewall[i].get('denied'))))
			try:
				firewall_tag = str(ast.literal_eval(json.dumps(firewall[i].get('targetTags'))))[2:-2]
				print "Tag: " + firewall_tag
				json_body['tag'] = firewall_tag
				print "+---------------------------------------------------+"
				print "		Affected Instances 				"
				print "+---------------------------------------------------+"
				for x in range(len(instances)):
					try:
						for k in range(len(instances[x].get('tags').get('items'))):
							if str(ast.literal_eval(json.dumps(instances[x].get('tags').get('items')[k]))) == firewall_tag:
								try:
									print instances[x].get('name') + "\t\t" + instances[x].get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP')
									instance_name_list.append(instances[x].get('name'))
									instance_ip_list.append(instances[x].get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP'))
								except:
									print instances[x].get('name')
									instance_name_list.append(instances[x].get('name'))
									instance_ip_list.append('N/A')

					except:
						pass
				json_body['instance_name'] = instance_name_list
				json_body['public_ip'] = instance_ip_list
				print "-----------------------------------------------------\n\n\n"
			
			except:
				print "+---------------------------------------------------+"
				print "		Affected Instances 				"
				print "+---------------------------------------------------+"
				print "*** APPLIED TO ALL ***\n\n\n"
				# WIP : NEED TO PUT ALL INSTANCE NAMES HERE
				json_body['instance_name'] = "APPLIED TO ALL"

		
		if args.elasticsearch:
			es.index(index='dollhouse', doc_type='dollhouse_firewall', body=json_body)
		else:
			continue


def audit_storage(project_name):
	bucket_list = os.popen('gsutil ls').read()

	for item in bucket_list.split():
		bucket_name = str(item).split('://')[1].split('/')[0]
		print('###########################################################')
		print('########## ' + bucket_name + ' ##########')
		print('###########################################################')
		logging_status = f_storage.get_logging_status(bucket_name)

		list_to_tabulate = f_storage.get_bucket_iam(bucket_name)
		print tabulate(list_to_tabulate, ["Role", "User"], tablefmt="grid")

if __name__ == "__main__":

	get_project_list()
	get_firewall_rules()
