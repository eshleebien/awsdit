#!/usr/bin/env python
"""
This program is to collect some AWS stuff 
"""
import boto3
import threading

from local_helpers.config import accounts_db 
from local_helpers import assume_role, get_session, misc 
from local_helpers import iam_helper

if __name__ == "__main__":
    """main"""

    """bucket to hold results"""
    output_bucket = []

    """turn on b64encode for results?: on/off"""
    """b64encode required to export results in csv format"""
    """for troubleshooting turn b64encode off"""

    encode = 'on'
    #encode = 'off'

    """probe for accounts presense by testing regions"""
    regions = get_session.regions()

    if regions:
       """generate output header"""
       output_bucket.append(iam_helper.inventory_user_policies_header(encode))

       """go through each account"""
       """------------------------------------------------"""
       multi_thread = []

       """get tuple: account -> dict:, temp role creds -> dict:"""
       for account in accounts_db.accounts:
           """get temp creds from trusting roles"""
           role = assume_role.new_role(account)

           if role:
               """make an iam type client connection"""
               iam = get_session.connect(
               role, 'iam')

               """
               call iam.list_user_policies() in multithreading mode 
               """
               thread_call = threading.Thread(
                   target=iam_helper.inventory_user_policies, 
                   args=(iam, account, output_bucket, encode))
               multi_thread.append(thread_call)
               thread_call.start()

       """wait for all threads to finish"""
       for t in multi_thread:
           t.join()

       """output or export results"""
       if output_bucket:
           misc.output_lines(output_bucket)










