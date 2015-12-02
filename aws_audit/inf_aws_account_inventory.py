#!/usr/bin/env python
"""
This program is to collect some AWS stuff 
"""
import boto3
import threading
import re

from local_helpers.config import accounts_db 
from local_helpers import assume_role, get_session, misc 

if __name__ == "__main__":
    """main"""

    """test connection"""
    regions = get_session.regions()

    if regions:
       """generate output header"""
       print '{0},{1}'.format(str('Account'),str('Number'))

       """go through each account info"""
       """------------------------------------------------"""
       for account in accounts_db.accounts:
           """get temp creds from trusting roles"""
           try:
               role = assume_role.new_role(account)
           except Exception, e:
               error_code = e
               #print e

           if role:
               print '{0},{1}'.format(
                         account.get('name'),
                         ('...'+str(re.split(":",account.get('role_arn'))[4])[6:])
                     ) 




