import os
import argparse

parser = argparse.ArgumentParser(description='Update the custom log metric on your Google Cloud Sink')
parser.add_argument('--organization', type=str, help='Organizatin ID of your Google Cloud Platform')
parser.add_argument('--sink', type=str, help='The name of the sink you want to update')
args = parser.parse_args()




rule_firewall_insert = """ (resource.type="gce_firewall_rule" AND protoPayload.authorizationInfo.resourceAttributes.type="compute.firewalls" AND protoPayload.methodName:"compute.firewalls.insert" AND severity!=ERROR) """
rule_firewall_patch = """ (resource.type="gce_firewall_rule" AND protoPayload.authorizationInfo.resourceAttributes.type="compute.firewalls" AND protoPayload.methodName:"compute.firewalls.patch" AND severity!=ERROR) """
rule_firewall_delete = """ (resource.type="gce_firewall_rule" AND protoPayload.authorizationInfo.resourceAttributes.type="compute.firewalls" AND protoPayload.methodName:"compute.firewalls.delete" AND severity!=ERROR) """
rule_service_account_create_key = """ (resource.type="service_account" AND protoPayload.methodName:"CreateServiceAccountKey" AND severity!=ERROR) """
rule_service_account_delete_key = """ (resource.type="service_account" AND protoPayload.methodName:"DeleteServiceAccountKey" AND severity!=ERROR) """
rule_gce_instance_set_tags = """ (resource.type="gce_instance" AND protoPayload.methodName:"compute.instances.setTags" AND operation.first=true AND severity!=ERROR) """
rule_gce_instance_add_access_config = """ (resource.type="gce_instance" AND jsonPayload.event_subtype="compute.instances.addAccessConfig" AND jsonPayload.event_type="GCE_OPERATION_DONE" AND severity!=ERROR) """
rule_k8s_anonymous_access = """ (resource.type="k8s_cluster" AND protoPayload.response.subjects.name="system:anonymous" AND ((protoPayload.methodName:"clusterrolebindings.create" OR protoPayload.authorizationInfo.permission:"clusterrolebindings.create") OR (protoPayload.methodName:"clusterrolebindings.patch" OR protoPayload.authorizationInfo.permission:"clusterrolebindings.patch")) AND severity!=ERROR) """ 
rule_k8s_public_cluster = """ (resource.type="gke_cluster" AND protoPayload.methodName:"ClusterManager.CreateCluster" AND NOT protoPayload.request.cluster.privateClusterConfig.enablePrivateNodes:true AND protoPayload.authenticationInfo.principalEmail:* AND severity!=ERROR) """
rule_iam = """ (resource.type="project" protoPayload.methodName=SetIamPolicy protoPayload.serviceData.policyDelta.bindingDeltas.action:* severity!=ERROR) """
rule_storage_allusers = """ (protoPayload.serviceName="storage.googleapis.com" AND protoPayload.serviceData.policyDelta.bindingDeltas.member="allUsers") """


rules = {
	"rule_firewall_insert" : rule_firewall_insert,
    "rule_firewall_patch" : rule_firewall_patch,
    "rule_firewall_delete" : rule_firewall_delete,
    "rule_service_account_create_key" : rule_service_account_create_key,
    "rule_service_account_delete_key" : rule_service_account_delete_key,
    "rule_gce_instance_set_tags" : rule_gce_instance_set_tags,
    "rule_gce_instance_add_access_config" : rule_gce_instance_add_access_config,
    "rule_k8s_anonymous_access" : rule_k8s_anonymous_access,
    "rule_k8s_public_cluster" : rule_k8s_public_cluster,
    "rule_iam" : rule_iam,
    "rule_storage_allusers" : rule_storage_allusers
}

log_filter = ''
for rule in rules:
    log_filter += rules[rule].strip() + ' OR '
log_filter = log_filter.strip().rsplit(' ', 1)[0] 

cmd = 'gcloud logging sinks update ' + args.sink + ' --organization='+args.organization+' --log-filter=\'' + log_filter + '\''
print(cmd)
os.system(cmd)
