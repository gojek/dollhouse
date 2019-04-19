import os

def createLoggingFirewall():
    # create firewall delete custom log metrics
    os.system('gcloud beta logging metrics create alert-firewall-delete \
                --description="this alerts if there is a deletion in a firewall rule" \
                --log-filter="resource.type=\"gce_firewall_rule\"\n\
                    \"compute.firewalls.delete\"\n\
                    \"compute.googleapis.com/resource_name\"\n\
                    \"GCE_OPERATION_DONE\"\n"')

    # create firewall insert custom log metrics
    os.system('gcloud beta logging metrics create alert-firewall-insert \
                --description="this alerts if there is a insert in a firewall rule" \
                --log-filter="resource.type=\"gce_firewall_rule\"\n\
                    \"compute.firewalls.insert\"\n\
                    \"compute.googleapis.com/resource_name\"\n\
                    \"GCE_OPERATION_DONE\"\n"')

    # create firewall patch custom log metrics
    os.system('gcloud beta logging metrics create alert-firewall-patch \
                --description="this alerts if there is a patch in a firewall rule" \
                --log-filter="resource.type=\"gce_firewall_rule\"\n\
                    \"compute.firewalls.patch\"\n\
                    \"compute.googleapis.com/resource_name\"\n\
                    \"GCE_OPERATION_DONE\"\n"')

def createLoggingServiceAccount():
    # create service account create key custom log metrics
    os.system('gcloud beta logging metrics create alert-serviceAccount-createKey \
                --description="this alerts if there is a key insert in a serviceAccount"\
                --log-filter="resource.type=\"service_account\" AND \
                    protoPayload.serviceName=\"iam.googleapis.com\" AND\
                    protoPayload.methodName=\"google.iam.admin.v1.CreateServiceAccountKey\""')

    # create service account delete key custom log metrics
    os.system('gcloud beta logging metrics create alert-serviceAccount-deleteKey \
                --description="this alerts if there is a key delete in a serviceAccount" \
                --log-filter="resource.type= \"service_account\" AND\
                    protoPayload.serviceName=\"iam.googleapis.com\" AND\
                    protoPayload.methodName=\"google.iam.admin.v1.DeleteServiceAccountKey\""')

def createLoggingIAM():
    # create IAM changes custom log metrics
    os.system('gcloud beta logging metrics create alert-iamrole \
                --description="this alerts if there is a key delete in a IAM role" \
                --log-filter="resource.type= \"project\" AND\
                    protoPayload.serviceName=\"cloudresourcemanager.googleapis.com\" AND\
                    protoPayload.methodName=\"SetIamPolicy\" AND\
                    protoPayload.serviceData.policyDelta.bindingDeltas.action=\"*\""')