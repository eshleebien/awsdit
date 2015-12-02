#!/usr/bin/env python
"""
This program is to collect some AWS stuff 
"""
import boto3
import threading

from local_helpers.config import accounts_db 
from local_helpers import assume_role, get_session, misc 
from local_helpers import s3_helper

if __name__ == "__main__":
    """main"""

    """bucket to hold results"""
    output_bucket = []

    """probe for accounts presense by testing regions"""
    regions = get_session.regions()

    if regions:
       """generate output header"""
       output_bucket.append(s3_helper.list_buckets_header())

       """go through each account and traverse each region"""
       """------------------------------------------------"""
       multi_thread = []

       """get tuple: account -> dict:, temp role creds -> dict:"""
       for account in accounts_db.accounts:
           """get temp creds from trusting roles"""
           role = assume_role.new_role(account)

           if role:
               """make an s3 type client connection"""
               s3 = get_session.connect(
               role, 's3')

               """
               call s3.list_buckets() in multithreading mode 
               """
               thread_call = threading.Thread(
                    target=s3_helper.list_buckets, 
                    args=(s3, account, output_bucket))
               multi_thread.append(thread_call)
               thread_call.start()

       """wait for all threads to finish"""
       for t in multi_thread:
           t.join()

       """output or export results"""
       if output_bucket:
           misc.output_lines(output_bucket)










