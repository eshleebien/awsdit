"""
process misc calls.
"""
import boto3
import socket
import json
import datetime
import dateutil.parser

def output_lines(lines):
    """output list of sorted lines"""
    for line in lines:
        print line

def format_line(line):
    """format list into a csv line"""
    return ",".join(line)

def check_if(value):
    """check if value exists"""
    if value:
       return value
    else:
       return "no-record"


def lookup(hostname):
    address = None
    try:
        address = socket.gethostbyname(hostname)
    except Exception, e:
        pass

    """check if value exists"""
    if address:
       return address
    else:
       return "no-record"

def json_pretty_print(json_dict):
    """pretty print json data"""
    return json.dumps(json_dict,
                      indent=2,
                      sort_keys=True)

def date_to_days(time_stamp):
    if time_stamp:
        today = datetime.datetime.now(dateutil.tz.tzlocal())
        return str((today - time_stamp).days)
    else:
        return str('-1')
