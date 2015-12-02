"""
This module is make calls to assume roles.
"""
import boto3

from local_helpers.config import accounts_db

# make sts call
sts = boto3.client('sts')

def new_role(account):
   role = None
   try:
      role = sts.assume_role(
         RoleArn=account.get('role_arn'),
         RoleSessionName=account.get('role_session_name')
      )
   except Exception, e:
       error_code = e
       #print (str(account.get('name').upper()) + " - error: " + str(e.message))

   if role:
       return role
   else:
       return None


