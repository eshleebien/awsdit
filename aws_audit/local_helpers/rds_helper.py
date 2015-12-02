"""
rds helper calls
"""
import boto3
import re

from local_helpers import misc

def rds_resource(session):
    #print type(session)
    """continue form multithread call
    returns an rds resource
    Args:
        session (session.Session()): 
    """
    rds = session.resource('rds')


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
               tag_value = re.sub('[,]', '/', tag_value)
               return tag_value
               continue
    if not rfctag:
        return str("no-record")

def check_port(port):
    """return port value"""
    """port value == None, means -1 or any"""
    if str(port) == 'None':
       return '-1'
    else:
       return port

def check_proto(proto):
    """return proto value"""
    """proto value == -1, means all protocols"""
    if str(proto) == '-1':
       return 'all'
    else:
       return proto

def describe_rds_instances_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "rdsId",
           "Type",
           "PubliclyAccessible",
           "rdsAddress",
           "rdsIP",
           "ListenPort"
            ))

def describe_rds_instances(rds, account, region, output_bucket):
    """continue from multithread call
    Args: 
        rds (object): rds client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    rds_list = rds.describe_db_instances().get('DBInstances')

    for rds_obj in rds_list:
        #print rds_obj
        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(region.get('RegionName')),
            misc.check_if(rds_obj.get('DBSubnetGroup').get('VpcId')),
            misc.check_if(rds_obj.get('DBInstanceIdentifier')),
            misc.check_if(rds_obj.get('DBInstanceClass')),
            misc.check_if(str(rds_obj.get('PubliclyAccessible'))),
            misc.check_if(rds_obj.get('Endpoint').get('Address')),
            misc.lookup(rds_obj.get('Endpoint').get('Address')),
            misc.check_if(str(rds_obj.get('Endpoint').get('Port')))
            )))


def sg_rule_sets_by_rds_header():
    """returns header for sg rule sets"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "rdsId",
           "PubliclyAccessible",
           "rdsAddress",
           "ListenPort",
           "GroupID",
           "GroupName",
           "Source",
           "StartPort",
           "EndPort",
           "Protocol"))

def sg_rule_sets_by_rds(rds, ec2, account, region, output_bucket):
    """generate list of security group rule sets by rds instance 
    Args: 
        rds (object): rds client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    """generate list of rds instances"""
    rds_list = rds.describe_db_instances().get('DBInstances')

    """generate list of security groups to get rule set details"""
    sg_list = ec2.describe_security_groups().get('SecurityGroups')

    for sg_obj in sg_list:
        """find out how many rdss are using a security group"""
        for rds_obj in rds_list:
            for rdssg in rds_obj.get('VpcSecurityGroups'):
                """check if security group is associated to rds instance"""
                if sg_obj.get('GroupId') == rdssg.get('VpcSecurityGroupId'):
                    
                    """move on to rule entries"""
                    for rule in sg_obj.get('IpPermissions'):
                        """cidr as source"""
                        for cidr in rule.get('IpRanges'):
                            if cidr.get('CidrIp'):
                                output_bucket.append(misc.format_line((
                                    misc.check_if(account.get('name')),
                                    misc.check_if(region.get('RegionName')),
                                    misc.check_if(rds_obj.get('DBSubnetGroup').get('VpcId')),
                                    misc.check_if(rds_obj.get('DBInstanceIdentifier')),
                                    misc.check_if(str(rds_obj.get('PubliclyAccessible'))),
                                    misc.check_if(rds_obj.get('Endpoint').get('Address')),
                                    misc.check_if(str(rds_obj.get('Endpoint').get('Port'))),
                                    misc.check_if(sg_obj.get('GroupId')),
                                    misc.check_if(sg_obj.get('GroupName')),
                                    misc.check_if(str(cidr.get('CidrIp'))),
                                    misc.check_if(str(check_port(rule.get('FromPort')))),
                                    misc.check_if(str(check_port(rule.get('ToPort')))),
                                    misc.check_if(str(check_proto(rule.get('IpProtocol'))))
                                    )))

                        """security groups as source"""
                        for group in rule.get('UserIdGroupPairs'):
                            if group.get('GroupId'):
                                output_bucket.append(misc.format_line((
                                    misc.check_if(account.get('name')),
                                    misc.check_if(region.get('RegionName')),
                                    misc.check_if(rds_obj.get('DBSubnetGroup').get('VpcId')),
                                    misc.check_if(rds_obj.get('DBInstanceIdentifier')),
                                    misc.check_if(str(rds_obj.get('PubliclyAccessible'))),
                                    misc.check_if(rds_obj.get('Endpoint').get('Address')),
                                    misc.check_if(str(rds_obj.get('Endpoint').get('Port'))),
                                    misc.check_if(sg_obj.get('GroupId')),
                                    misc.check_if(sg_obj.get('GroupName')),
                                    misc.check_if(group.get('GroupId')),
                                    misc.check_if(str(check_port(rule.get('FromPort')))),
                                    misc.check_if(str(check_port(rule.get('ToPort')))),
                                    misc.check_if(str(check_proto(rule.get('IpProtocol'))))
                                    )))



