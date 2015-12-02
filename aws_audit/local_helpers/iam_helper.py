"""
iam helper calls.
"""
import boto3
import base64
import json
import re
import datetime
import dateutil.parser

from local_helpers import misc

def is_password_set(iam, username):
    """"check if user password login profile exists"""
    login_prof = {}
    try:
        login_prof = iam.get_login_profile(UserName=username)
    except Exception, e:
        pass

    if login_prof:
        return str('Yes')
    else:
        return str('No') 
    
def count_active_keys(iam, username):
    """count active access keys for user"""
    key_count = 0
    for access_key in iam.list_access_keys(
        UserName=username).get('AccessKeyMetadata'):
        if access_key.get('Status') == "Active":
            key_count += 1

    return str(key_count)
    
def mfa_enabled(iam, username):
    """find out if mfa is enabled"""
    if iam.list_mfa_devices(UserName=username).get('MFADevices'):
        return "TRUE"
    else:
        return "FALSE"

def list_groups_for_user(iam, username):
    """return list of user group memberships""" 
    gp_list = []
    for group in iam.list_groups_for_user(UserName=username).get('Groups'):
        gp_list.append(str(group.get('GroupName')))

    #return '||'.join(gp_list)
    return '<br>'.join(gp_list)

def list_user_policies_for_user(iam, username):
    """return list of user policies for user"""
    user_policy_list = []
    for policy in iam.list_user_policies(UserName=username).get('PolicyNames'):
        user_policy_list.append(str(policy))

    return '<br>'.join(user_policy_list)


def inventory_access_keys_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "UserName",
           "Key_ID",
           "Age",
           "CreationDate",
           "Status",
           "DaysLastUsed",
           "LastUsed",
           "ServiceName")) 

def inventory_access_keys(iam, account, output_bucket):
    """continue from multithread call
    Args: 
        iam (object): iam client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """

    """get list of keys from the list of users"""
    for user in iam.list_users().get('Users'):
        for key in iam.list_access_keys(
                   UserName=user.get('UserName')).get('AccessKeyMetadata'):

            """find out which keys have been used"""
            last_used = iam.get_access_key_last_used(
                        AccessKeyId=key.get('AccessKeyId')).get('AccessKeyLastUsed')

            key_lastused = None
            key_lastused_days = None
            key_service = None
            """get info for active keys"""
            if last_used.get('LastUsedDate'):
                key_lastused = last_used.get('LastUsedDate').strftime('%Y_%m_%d') 
                key_lastused_days = misc.date_to_days(last_used.get('LastUsedDate'))
                key_service = last_used.get('ServiceName')
            else:
                """mark inactive keys"""
                key_lastused = 'Never'
                key_lastused_days = '-1'
                key_service = 'N/A'

            output_bucket.append(misc.format_line((
                misc.check_if(account.get('name')),
                misc.check_if(user.get('UserName')),
                misc.check_if(key.get('AccessKeyId')),
                misc.check_if(str(misc.date_to_days(key.get('CreateDate')))),
                misc.check_if(key.get('CreateDate').strftime('%Y_%m_%d')),
                misc.check_if(key.get('Status')),
                misc.check_if(str(key_lastused_days)),
                misc.check_if(key_lastused),
                misc.check_if(key_service),
                )))

def inventory_users_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "UserName",
           "CreateDate",
           "PasswordSet",
           "PasswordLastUsed",
           "ActiveAccessKeys",
           "MFA",
           "GroupMemberships",
           "UserPolicies"))

def inventory_users(iam, account, output_bucket):
    """continue from multithread call
    Args: 
        iam (object): iam client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    users_list = iam.list_users().get('Users')

    for user in users_list:
        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(user.get('UserName')),
            misc.check_if(user.get('CreateDate').strftime('%Y_%m_%d')),
            misc.check_if(is_password_set(iam, user.get('UserName'))),
            misc.check_if(misc.date_to_days(user.get('PasswordLastUsed'))),
            misc.check_if(count_active_keys(iam, user.get('UserName'))),
            misc.check_if(mfa_enabled(iam, user.get('UserName'))),
            misc.check_if(list_groups_for_user(iam, user.get('UserName'))),
            misc.check_if(list_user_policies_for_user(iam, user.get('UserName'))),
            )))


def inventory_managed_policies_header(encode):
    """generate output header"""
    if encode == 'on':
        return misc.format_line((
           base64.b64encode(str("Account")),
           base64.b64encode(str("AttachLevel")),
           base64.b64encode(str("ObjectName")),
           base64.b64encode(str("PolicyName")),
           base64.b64encode(str("Policy"))
           ))
    else:
        return misc.format_line((
           str("Account"),
           str("AttachLevel"),
           str("ObjectName"),
           str("PolicyName"),
           str("Policy")
           ))

def inventory_managed_policies(iam, account, output_bucket, encode):
    """continue from multithread call
    Args: 
        iam (object): iam client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
        
    """
    policy_list = iam.list_policies(
                  OnlyAttached=True).get('Policies')
    
    for policy in policy_list:
        policy_body = iam.get_policy_version(
                      PolicyArn=policy.get('Arn'),
                      VersionId=policy.get('DefaultVersionId')
        ).get('PolicyVersion').get('Document')
        
        policy_body = misc.json_pretty_print(policy_body)
        """get list of groups using this policy"""
        policy_groups = iam.list_entities_for_policy(
                        PolicyArn=policy.get('Arn')).get('PolicyGroups')
        """get list of roles using this policy"""
        policy_roles = iam.list_entities_for_policy(
                        PolicyArn=policy.get('Arn')).get('PolicyRoles')
        """get list of users using this policy"""
        policy_users = iam.list_entities_for_policy(
                        PolicyArn=policy.get('Arn')).get('PolicyUsers')

        if policy_groups:
            for group_entity in policy_groups:
                if encode == 'on':
                    output_bucket.append(misc.format_line((
                        misc.check_if(base64.b64encode(account.get('name'))),
                        misc.check_if(base64.b64encode(str('group_policy'))),
                        misc.check_if(base64.b64encode(group_entity.get('GroupName'))),
                        misc.check_if(base64.b64encode(policy.get('PolicyName'))),
                        misc.check_if(base64.b64encode(str('<pre>' + policy_body + '</pre>'))),
                    )))
                else:
                    output_bucket.append(misc.format_line((
                        misc.check_if(account.get('name')),
                        misc.check_if(str('group_policy')),
                        misc.check_if(group_entity.get('GroupName')),
                        misc.check_if(policy.get('PolicyName')),
                        misc.check_if(str(policy_body)),
                    )))

        if policy_roles:
            for role_entity in policy_roles:
                if encode == 'on':
                    output_bucket.append(misc.format_line((
                        misc.check_if(base64.b64encode(account.get('name'))),
                        misc.check_if(base64.b64encode(str('role_policy'))),
                        misc.check_if(base64.b64encode(role_entity.get('RoleName'))),
                        misc.check_if(base64.b64encode(policy.get('PolicyName'))),
                        misc.check_if(base64.b64encode(str('<pre>' + policy_body + '</pre>'))),
                    )))
                else:
                    output_bucket.append(misc.format_line((
                        misc.check_if(account.get('name')),
                        misc.check_if(str('role_policy')),
                        misc.check_if(role_entity.get('RoleName')),
                        misc.check_if(policy.get('PolicyName')),
                        misc.check_if(str(policy_body)),
                    )))

        if policy_users:
            for user_entity in policy_users:
                if encode == 'on':
                    output_bucket.append(misc.format_line((
                        misc.check_if(base64.b64encode(account.get('name'))),
                        misc.check_if(base64.b64encode(str('user_policy'))),
                        misc.check_if(base64.b64encode(user_entity.get('UserName'))),
                        misc.check_if(base64.b64encode(policy.get('PolicyName'))),
                        misc.check_if(base64.b64encode(str('<pre>' + policy_body + '</pre>'))),
                    )))
                else:
                    output_bucket.append(misc.format_line((
                        misc.check_if(account.get('name')),
                        misc.check_if(str('user_policy')),
                        misc.check_if(user_entity.get('UserName')),
                        misc.check_if(policy.get('PolicyName')),
                        misc.check_if(str(policy_body)),
                    )))


def inventory_role_policies_header(encode):
    """generate output header"""
    if encode == 'on':
        return misc.format_line((
           base64.b64encode(str("Account")),
           base64.b64encode(str("RoleType")),
           base64.b64encode(str("RoleName")),
           base64.b64encode(str("PolicyName")),
           base64.b64encode(str("Policy"))
           ))
    else:
        return misc.format_line((
           str("Account"),
           str("RoleType"),
           str("RoleName"),
           str("PolicyName"),
           str("Policy")
           ))

def inventory_role_policies(iam, account, output_bucket, encode):
    """continue from multithread call
    Args: 
        iam (object): iam client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
        
    """
    role_list = iam.list_roles().get('Roles')
    for role in role_list:
        assume_role_policy = misc.json_pretty_print(role.get('AssumeRolePolicyDocument'))

        """trust relationship policy"""
        if encode == 'on':
            output_bucket.append(misc.format_line((
                misc.check_if(base64.b64encode(account.get('name'))),
                misc.check_if(base64.b64encode(str('iam:trust_policy'))),
                misc.check_if(base64.b64encode(role.get('RoleName'))),
                misc.check_if(base64.b64encode(role.get('Arn'))),
                misc.check_if(base64.b64encode(str('<pre>' + assume_role_policy + '</pre>'))),
            )))
        else:
            output_bucket.append(misc.format_line((
                misc.check_if(account.get('name')),
                misc.check_if(str('iam:trust_policy')),
                misc.check_if(role.get('RoleName')),
                misc.check_if(role.get('Arn')),
                misc.check_if(str(assume_role_policy)),
            )))

        """pull out inline role policies"""
        policies = iam.list_role_policies(
                   RoleName=role.get('RoleName')).get('PolicyNames')

        for policy_name in policies:
            policy = misc.json_pretty_print(
                         iam.get_role_policy(
                         RoleName=role.get('RoleName'),
                         PolicyName=policy_name
                         ).get('PolicyDocument')
                     )

            """inline role policy entry"""
            if encode == 'on':
                output_bucket.append(misc.format_line((
                    misc.check_if(base64.b64encode(account.get('name'))),
                    misc.check_if(base64.b64encode(str('iam:inline_policy'))),
                    misc.check_if(base64.b64encode(role.get('RoleName'))),
                    misc.check_if(base64.b64encode(str(policy_name))),
                    misc.check_if(base64.b64encode(str('<pre>' + policy + '</pre>'))),
                )))
            else:
                output_bucket.append(misc.format_line((
                    misc.check_if(account.get('name')),
                    misc.check_if(str('iam:inline_policy')),
                    misc.check_if(role.get('RoleName')),
                    misc.check_if(str(policy_name)),
                    misc.check_if(str(policy)),
                )))


def inventory_group_policies_header(encode):
    """generate output header"""
    if encode == 'on':
        return misc.format_line((
           base64.b64encode(str("Account")),
           base64.b64encode(str("GroupName")),
           base64.b64encode(str("PolicyName")),
           base64.b64encode(str("Policy"))
           ))
    else:
        return misc.format_line((
           str("Account"),
           str("GroupName"),
           str("PolicyName"),
           str("Policy")
           ))

def inventory_group_policies(iam, account, output_bucket, encode):
    """continue from multithread call
    Args: 
        iam (object): iam client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
        
    """
    group_list = iam.list_groups().get('Groups')
    for group in group_list:
        """pull out inline group policies"""
        policies = iam.list_group_policies(
                   GroupName=group.get('GroupName')).get('PolicyNames')
       
        for policy_name in policies:
            policy = misc.json_pretty_print(
                         iam.get_group_policy(
                         GroupName=group.get('GroupName'),
                         PolicyName=policy_name
                         ).get('PolicyDocument')
                     )
       
            """inline group policy entry"""
            if encode == 'on':
                output_bucket.append(misc.format_line((
                    misc.check_if(base64.b64encode(account.get('name'))),
                    misc.check_if(base64.b64encode(group.get('GroupName'))),
                    misc.check_if(base64.b64encode(str(policy_name))),
                    misc.check_if(base64.b64encode(str('<pre>' + policy + '</pre>'))),
                )))
            else:
                output_bucket.append(misc.format_line((
                    misc.check_if(account.get('name')),
                    misc.check_if(group.get('GroupName')),
                    misc.check_if(str(policy_name)),
                    misc.check_if(str(policy)),
                )))

def inventory_user_policies_header(encode):
    """generate output header"""
    if encode == 'on':
        return misc.format_line((
           base64.b64encode(str("Account")),
           base64.b64encode(str("UserName")),
           base64.b64encode(str("PolicyName")),
           base64.b64encode(str("Policy"))
           ))
    else:
        return misc.format_line((
           str("Account"),
           str("UserName"),
           str("PolicyName"),
           str("Policy")
           ))

def inventory_user_policies(iam, account, output_bucket, encode):
    """continue from multithread call
    Args: 
        iam (object): iam client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
        
    """
    user_list = iam.list_users().get('Users')
    for user in user_list:
        """pull out inline user policies"""
        policies = iam.list_user_policies(
                   UserName=user.get('UserName')).get('PolicyNames')

        for policy_name in policies:
            policy = misc.json_pretty_print(
                         iam.get_user_policy(
                         UserName=user.get('UserName'),
                         PolicyName=policy_name
                         ).get('PolicyDocument')
                     )
        
            """inline user policy entry"""
            if encode == 'on':
                output_bucket.append(misc.format_line((
                    misc.check_if(base64.b64encode(account.get('name'))),
                    misc.check_if(base64.b64encode(user.get('UserName'))),
                    misc.check_if(base64.b64encode(str(policy_name))),
                    misc.check_if(base64.b64encode(str('<pre>' + policy + '</pre>'))),
                )))
            else:
                output_bucket.append(misc.format_line((
                    misc.check_if(account.get('name')),
                    misc.check_if(user.get('UserName')),
                    misc.check_if(str(policy_name)),
                    misc.check_if(str(policy)),
                )))




