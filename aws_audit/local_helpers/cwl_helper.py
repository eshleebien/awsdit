"""
cwl helper calls.
"""
import boto3
import base64
import re
import time
import datetime
import dateutil.parser
import json

from local_helpers import misc


def date_to_days(time_stamp):
    if time_stamp:
        today = datetime.datetime.now()
        create_date = datetime.datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        return str((today - create_date).days)
    else:
        return str('-1')

def check_tag(obj, tag_name):
    """
    returns tag_name values if tag_name exist
    Args: 
        obj (dict): list of tags
        tag_name (string): tag name value
    Returns:
        tag_name values (string)
    """
    rfctag = None
    if obj.get('Tags'):
        for tag in obj.get('Tags'):
             if tag.get('Key') == tag_name:
               tag_value = tag.get('Value')
               #tag_value = re.sub('[,]', ' / ', tag_value)
               tag_value = re.sub('[,]', ' <br> ', tag_value)
               return tag_value
               continue
    if not rfctag:
        return str("no-record")

def filter_log_events_header(encode):
    """generate output header"""
    if encode == 'on':
        return misc.format_line((
           base64.b64encode(str("Account")),
           base64.b64encode(str("Region")),
           base64.b64encode(str("eventName")),
           base64.b64encode(str("eventTime")),
           base64.b64encode(str("arn")),
           base64.b64encode(str("sourceAddress")),
           base64.b64encode(str("requestParameters")),
           base64.b64encode(str("responseElements"))
            ))
    else:
        return misc.format_line((
           "Account",
           "Region",
           "eventName",
           "eventTime",
           "arn",
           "sourceAddress",
           "requestParameters",
           "responseElements"
            ))


def filter_log_events(cwl, account, region, output_bucket, search_filter, log_group, startTime, encode):
    """continue from multithread call
    Args: 
        cwl (object): CloudWatchLog client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
        search_filter (str filter): filter search params 
        log_group (str): logGroup name to search 
        startTime (date): start time for search 
        encode (str): on/off encoding 
    Returns:
        nothing. appends results to output_bucket
    """
    search_logGroup = None
    try:
        search_logGroup = cwl.filter_log_events(
                         logGroupName = log_group,
                         filterPattern = search_filter,
                         startTime = int(time.mktime(startTime.timetuple()))
                         )
    except Exception, e:
        error_code = e
        #print e

    if search_logGroup:
       for message in search_logGroup.get('events'):
           event_name = (json.loads(message.get('message'))).get('eventName')
           event_time = (json.loads(message.get('message'))).get('eventTime')
           arn = (json.loads(message.get('message'))).get('userIdentity').get('arn')
           source_address = (json.loads(message.get('message'))).get('sourceIPAddress')
           request_param = misc.json_pretty_print((json.loads(message.get('message'))).get('requestParameters'))
           response_elem = misc.json_pretty_print((json.loads(message.get('message'))).get('responseElements'))

           if encode == 'on':
               output_bucket.append(misc.format_line((
                   misc.check_if(base64.b64encode(account.get('name'))),
                   misc.check_if(base64.b64encode(region.get('RegionName'))),
                   misc.check_if(base64.b64encode(event_name)),
                   misc.check_if(base64.b64encode(str(event_time))),
                   misc.check_if(base64.b64encode(misc.check_if(arn))),
                   misc.check_if(base64.b64encode(str(source_address))),
                   misc.check_if(base64.b64encode(str('<pre>' + request_param + '</pre>'))),
                   misc.check_if(base64.b64encode(str('<pre>' + response_elem + '</pre>'))),
                   )))
           else:
               output_bucket.append(misc.format_line((
                   misc.check_if(account.get('name')),
                   misc.check_if(region.get('RegionName')),
                   misc.check_if(event_name),
                   misc.check_if(str(event_time)),
                   misc.check_if(arn),
                   misc.check_if(str(source_address)),
                   misc.check_if(str('<pre>' + request_param + '</pre>')),
                   misc.check_if(str('<pre>' + response_elem + '</pre>')),
                   )))



