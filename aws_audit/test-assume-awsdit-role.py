#!/usr/bin/env python

# Example code to assume a role within a sitting account

import re
import boto
from boto.utils import get_instance_metadata

#local call to instance metadata and extract account number from iam info
account_number = str(re.split(":",(get_instance_metadata()['iam']['info']['InstanceProfileArn']))[4])

#or to test remote aws account
#account_number = '<12-digit-aws-account-number>'

# make sts call
sts = boto.connect_sts()

desired_role = 'awsdit-role'
role_description = 'awsditRoleTest'

role = sts.assume_role('arn:aws:iam::{0}:role/{1}'.format(account_number, desired_role), role_description)

## make a connection to an AWS service such as below, and continue with your normal code.
#EC2
ec2 = boto.connect_ec2(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#RDS
rds = boto.connect_rds(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#ELB
elb = boto.connect_elb(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#IAM
iam = boto.connect_iam(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#S3
s3 = boto.connect_s3(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#SQS
sns = boto.connect_sqs(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#SNS
sns = boto.connect_sns(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#VPC
vpc = boto.connect_vpc(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)

#R53
r53 = boto.connect_route53(role.credentials.access_key, role.credentials.secret_key, security_token=role.credentials.session_token)
