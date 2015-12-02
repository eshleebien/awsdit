"""
cwl helper calls.
"""
import boto3
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


def list_cloudtrails_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "trailName",
           "loggingOn",
           "cloudwatchEnabled",
           "latestDeliveryTime",
           "cloudwatchLogGroupArn",
           "cloudtrailS3BucketName",
            ))


def list_cloudtrails(cltr, account, region, output_bucket):
    """continue from multithread call
    Args: 
        cltr (object): CloudTrail client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    trail_list = None 
    try:
        trail_list = cltr.describe_trails().get('trailList')
    except Exception, e:
        error_code = e

    if trail_list:
        for trail in trail_list:
            trail_status = cltr.get_trail_status(
                       Name=trail.get('Name')
                       )
            cw_log_group = 'no-record'
            cloudwatch_enabled = 'False'
            if trail.get('CloudWatchLogsLogGroupArn'):
                cloudwatch_enabled = 'True'
                cw_log_group = re.split(":",trail.get('CloudWatchLogsLogGroupArn'))[6]

            output_bucket.append(misc.format_line((
                 misc.check_if(account.get('name')),
                 misc.check_if(region.get('RegionName')),
                 misc.check_if(trail.get('Name')),
                 misc.check_if(str(trail_status.get('IsLogging'))),
                 misc.check_if(str(cloudwatch_enabled)),
                 misc.check_if(str(trail_status.get('LatestDeliveryTime').strftime('%Y_%m_%d %I:%M %p'))),
                 misc.check_if(str(cw_log_group)),
                 misc.check_if(trail.get('S3BucketName')),
                 )))

    else:
        output_bucket.append(misc.format_line((
             misc.check_if(account.get('name')),
             misc.check_if(region.get('RegionName')),
             misc.check_if(str('not-configured')),
             misc.check_if(str('False')),
             misc.check_if(str('False')),
             misc.check_if(str('no-record')),
             misc.check_if(str('no-record')),
             misc.check_if(str('no-record')),
             )))



