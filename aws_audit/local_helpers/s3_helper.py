"""
s3 helper calls
"""
import boto3
import base64
import json
import re

from local_helpers import misc

def s3_resource(session):
    #print type(session)
    """continue form multithread call
    returns an s3 resource
    Args:
        session (session.Session()): 
    """
    s3 = session.resource('s3')

def list_buckets_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "WebAccess",
           "BucketName",
           "Url"
            ))

def list_buckets(s3, account, output_bucket):
    """continue from multithread call
    Args: 
        s3 (object): s3 client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    s3_bucket_list = s3.list_buckets().get('Buckets')

    for s3_obj in s3_bucket_list:
        site = []
        try:
            site = s3.get_bucket_website(Bucket=s3_obj.get('Name'))
        except Exception, e:
            error_code = e 

        if site:
            site_enabled = 'true'
        else:
            site_enabled = 'false'

        url = 'https://{0}.s3.amazonaws.com'.format(    
                str(s3_obj.get('Name'))
                )
            
        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(site_enabled),
            misc.check_if(s3_obj.get('Name')),
            misc.check_if(url),
            )))

def list_bucket_acls_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "BucketName",
           "Source",
           "Permission"
            ))

def list_bucket_acls(s3, account, output_bucket):
    """continue from multithread call
    Args: 
        s3 (object): s3 client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    s3_bucket_list = s3.list_buckets().get('Buckets')

    for s3_obj in s3_bucket_list:
        grants = []
        try:
            grants = s3.get_bucket_acl(Bucket=s3_obj.get('Name')).get('Grants')
        except Exception, e:
            error_code = e
        
        if grants: 
            for grant in grants:
                if grant.get('Grantee').get('DisplayName'):
                    output_bucket.append(misc.format_line((
                        misc.check_if(account.get('name')),
                        misc.check_if(s3_obj.get('Name')),
                        misc.check_if(grant.get('Grantee').get('DisplayName')),
                        misc.check_if(grant.get('Permission'))
                    )))

                if grant.get('Grantee').get('URI'):
                    output_bucket.append(misc.format_line((
                        misc.check_if(account.get('name')),
                        misc.check_if(s3_obj.get('Name')),
                        misc.check_if(grant.get('Grantee').get('URI')),
                        misc.check_if(grant.get('Permission'))
                    )))

def list_bucket_policies_header(encode):
    """generate output header"""
    if encode == 'on': 
        return misc.format_line((
            base64.b64encode(str("Account")),
            base64.b64encode(str("BucketName")),
            base64.b64encode(str("PolicyType")),
            base64.b64encode(str("Policy"))
            ))
    else: 
        return misc.format_line((
            str("Account"),
            str("BucketName"),
            str("PolicyType"),
            str("Policy")
            ))

def list_bucket_policies(s3, account, output_bucket, encode):
    """continue from multithread call
    Args: 
        s3 (object): s3 client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    s3_bucket_list = s3.list_buckets().get('Buckets')
    for s3_obj in s3_bucket_list:
        bucket_policy = []
        """get bucket policy if defined """
        try:
            bucket_policy = s3.get_bucket_policy(Bucket=s3_obj.get('Name')).get('Policy')
        except Exception, e:
            error_code = e
        
        if bucket_policy:
            if encode == 'on':
                output_bucket.append(misc.format_line((
                    misc.check_if(base64.b64encode(account.get('name'))),
                    misc.check_if(base64.b64encode(s3_obj.get('Name'))),
                    misc.check_if(base64.b64encode('s3:bucket_policy')),
                    misc.check_if(base64.b64encode(
                              '<pre>' + 
                              misc.json_pretty_print(json.loads(bucket_policy)) + 
                              '</pre>'))
                )))
            else:
                output_bucket.append(misc.format_line((
                    misc.check_if(account.get('name')),
                    misc.check_if(s3_obj.get('Name')),
                    misc.check_if(str('s3:bucket_policy')),
                    misc.check_if(
                              misc.json_pretty_print(json.loads(bucket_policy))) 
                )))

def list_potential_exposed_files_header():
    """generate output header"""
    #return misc.format_line((
    print misc.format_line((
           "Account",
           "Permission",
           "Grantee",
           "Url"
            ))

def list_potential_exposed_files(s3, account, output_bucket):
    """continue from multithread call
    Args: 
        s3 (object): s3 client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    s3_bucket_list = s3.list_buckets().get('Buckets')

    for s3_obj in s3_bucket_list:
        object_list = []
        try:
            object_list = s3.list_objects(Bucket=s3_obj.get('Name'))
        except Exception, e:
            error_code = e

        try:
            for obj_keys in object_list.get('Contents'):
                obj_acl_list = s3.get_object_acl(
                     Bucket=s3_obj.get('Name'),
                     Key=obj_keys.get('Key')
                ).get('Grants')

                if obj_acl_list:
                    for obj_acl in obj_acl_list:
                        if 'AllUsers' in str(obj_acl.get('Grantee')):
                            #output_bucket.append(misc.format_line((
                            url = 'http://{0}.s3.amazonaws.com/{1}'.format( 
                                    str(s3_obj.get('Name')),
                                    str(obj_keys.get('Key'))
                                    )
                            print (misc.format_line((
                                misc.check_if(account.get('name')),
                                misc.check_if(obj_acl.get('Permission')),
                                misc.check_if('AllUsers'),
                                misc.check_if(url),
                                )))
        except Exception, e:
            error_code = e






