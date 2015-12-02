#!/usr/bin/env python
"""
This program is to collect some AWS stuff 
"""
import boto3
import threading

from datetime import timedelta
from datetime import datetime

from local_helpers.config import accounts_db 
from local_helpers import assume_role, get_session, misc 
from local_helpers import cwl_helper

if __name__ == "__main__":
    """main"""

    """*** specify what to filter ***"""
    search_filters = []
    search_filters.append('{($.eventName = RunInstances || $.eventName = TerminateInstances)}')
    #search_filters.append('{($.eventName = Authorize* || $.eventName = Revoke*)}')
    #search_filters.append('{($.eventName = Create* || $.eventName = Delete* || $.eventName = Modify*)}')
    #search_filters.append('{($.eventName = Attach* || $.eventName = Change*)}')
    #search_filters.append('{($.eventName = Put* || $.eventName = Add* || $.eventName = Update*)}') 
    #search_filters.append('{($.eventName = Associate* || $.eventName = Submit*)}')

    """bucket to hold results"""
    output_bucket = []

    encode = 'on'
    #encode = 'off'

    """specify logGroup"""
    log_group = 'CloudTrail/DefaultLogGroup'

    """specify a startTime"""
    startTime = datetime.utcnow() - timedelta(days=2)

    """get list of available regions"""
    regions = get_session.regions()

    if regions:
       """generate output header"""
       output_bucket.append(cwl_helper.filter_log_events_header(encode))

       """go through each account and traverse each region"""
       """------------------------------------------------"""
       multi_thread = []

       """get tuple: account -> dict:, temp role creds -> dict:"""
       for account in accounts_db.accounts:
           """get temp creds from trusting roles"""
           role = assume_role.new_role(account)

           if role:
               for region in regions.get('Regions'):

                   """make an cwl type client connection"""
                   cwl = get_session.connect(
                   role, 
                   'logs', 
                   region_name=region.get('RegionName'))

                   """
                   call cwl.filter_log_events() in multithreading mode 
                   for better performance. 
                   Note: using wildcard filters in cloudwatch, you get  
                   inconsistent results.(at least with this code)
                   """
                   for search_filter in search_filters:
                       thread_call = threading.Thread(
                           target=cwl_helper.filter_log_events, 
                           args=(cwl, account, region, output_bucket, 
                                 search_filter, log_group, startTime, encode)
                       )
                       multi_thread.append(thread_call)
                       thread_call.start()

       """wait for all threads to finish"""
       for t in multi_thread:
           t.join()

       """output or export results"""
       if output_bucket:
           misc.output_lines(output_bucket)










