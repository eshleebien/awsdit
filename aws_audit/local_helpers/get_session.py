"""
module to make client calls.
"""
import boto3

from local_helpers import assume_role
from local_helpers.config import accounts_db

def regions():
    """generate list of regions from first account"""
    role = assume_role.new_role(accounts_db.accounts[0])
    if role:
          ec2 = boto3.client('ec2', region_name='us-east-1', 
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'), 
                 aws_session_token=role.get('Credentials').get('SessionToken')
                 )
          return ec2.describe_regions()

    
def connect(role, client_type, **args):
   """module to connect client to different services
   Args: 
        role (dict): role object 
        client_type (string): type of connection 
    Returns:
        temporary role credentials.
    """
   if role:
      if client_type == 'ec2':
          if 'region_name' in args:
              region = args.get('region_name')
              del args['region_name']
          else:
              region = 'us-east-1'
          return boto3.client('ec2', region_name=region, 
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'), 
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)

      if client_type == 'rds':
          if 'region_name' in args:
              region = args.get('region_name')
              del args['region_name']
          else:
              region = 'us-east-1'
          return boto3.client('rds', region_name=region,
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)

      if client_type == 'elb':
          if 'region_name' in args:
              region = args.get('region_name')
              del args['region_name']
          else:
              region = 'us-east-1'
          return boto3.client('elb', region_name=region,
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)

      if client_type == 'iam':
          if 'region_name' in args:
              """iam is not region bound"""
              del args['region_name']
          return boto3.client('iam', 
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)

      if client_type == 's3':
          if 'region_name' in args:
              """s3 is not region bound"""
              del args['region_name']
          return boto3.client('s3',
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)

      if client_type == 'codedeploy':
          if 'region_name' in args:
              region = args.get('region_name')
              del args['region_name']
          else:
              region = 'us-east-1'
          return boto3.client('codedeploy', region_name=region,
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)

      if client_type == 'logs':
          if 'region_name' in args:
              region = args.get('region_name')
              del args['region_name']
          else:
              region = 'us-east-1'
          return boto3.client('logs', region_name=region,
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)

      if client_type == 'cloudtrail':
          if 'region_name' in args:
              region = args.get('region_name')
              del args['region_name']
          else:
              region = 'us-east-1'
          return boto3.client('cloudtrail', region_name=region,
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)


def task_session(role, **args):
   """module to connect to different task sessions"""
   if role:
      return boto3.session.Session(
                 aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                 aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'), 
                 aws_session_token=role.get('Credentials').get('SessionToken'),
                 **args)
