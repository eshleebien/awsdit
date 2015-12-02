"""
elb helper calls.
"""
import boto3
import re

from local_helpers import misc

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

def get_ec2s(ids_list):
    """get list of attached ec2 ids"""
    ec2ids_list = []
    for ec2id in ids_list:
        ec2ids_list.append(ec2id.get('InstanceId'))

    #ec2id = '||'.join(ec2ids_list)
    ec2id = '<br>'.join(ec2ids_list)

    if str(ec2id):
       return ec2id
    else:
       return 'no-record'

def describe_elb_instances_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "elbName",
           "Scheme",
           "IPAddress",
           "dnsName",
           "elbPort",
           "elbProto",
           "backInstances",
           "instancePort",
           "instanceProto")) 

def describe_elb_instances(elb, account, region, output_bucket):
    """continue from multithread call
    Args: 
        elb (object): elb client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    elb_list = elb.describe_load_balancers().get('LoadBalancerDescriptions')

    for elb_obj in elb_list:
        #print elb_obj
        """dns lookup fqdn"""
        elb_ip = misc.lookup(elb_obj.get('DNSName'))
        """get list of attached ec2 ids"""
        ec2id = get_ec2s(elb_obj.get('Instances'))

        for elb_listener in elb_obj.get('ListenerDescriptions'):
 
            output_bucket.append(misc.format_line((
                misc.check_if(account.get('name')),
                misc.check_if(region.get('RegionName')),
                misc.check_if(elb_obj.get('VPCId')),
                misc.check_if(elb_obj.get('LoadBalancerName')),
                misc.check_if(elb_obj.get('Scheme')),
                misc.check_if(elb_ip),
                misc.check_if(elb_obj.get('DNSName')),
                misc.check_if(str(elb_listener.get('Listener').get('LoadBalancerPort'))),
                misc.check_if(elb_listener.get('Listener').get('Protocol')),
                misc.check_if(ec2id),
                misc.check_if(str(elb_listener.get('Listener').get('InstancePort'))),
                misc.check_if(elb_listener.get('Listener').get('InstanceProtocol'))
                )))


def sg_rule_sets_by_elb_header():
    """returns header for sg rule sets"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "elbName",
           "Scheme",
           "IPAddress",
           "dnsName",
           "GroupID",
           "GroupName",
           "Source",
           "StartPort",
           "EndPort",
           "Protocol"))

def sg_rule_sets_by_elb(elb, ec2, account, region, output_bucket):
    """generate list of security group rule sets by elb instance 
    Args: 
        elb (object): elb client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    """generate list of elb instances"""
    elb_list = elb.describe_load_balancers().get('LoadBalancerDescriptions')

    """generate list of security groups to get rule set details"""
    sg_list = ec2.describe_security_groups().get('SecurityGroups')

    for sg_obj in sg_list:
        """find out how many elbs are using a security group"""
        for elb_obj in elb_list:
            for elbsg in elb_obj.get('SecurityGroups'):
                """check if security group is associated to elb instance"""
                if sg_obj.get('GroupId') == elbsg:
                    
                    elb_ip = misc.lookup(elb_obj.get('DNSName')) 
                    """move on to rule entries"""
                    for rule in sg_obj.get('IpPermissions'):
                        """cidr as source"""
                        for cidr in rule.get('IpRanges'):
                            if cidr.get('CidrIp'):
                                output_bucket.append(misc.format_line((
                                    misc.check_if(account.get('name')),
                                    misc.check_if(region.get('RegionName')),
                                    misc.check_if(elb_obj.get('VPCId')),
                                    misc.check_if(elb_obj.get('LoadBalancerName')),
                                    misc.check_if(elb_obj.get('Scheme')),
                                    misc.check_if(elb_ip),
                                    misc.check_if(elb_obj.get('DNSName')),
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
                                    misc.check_if(elb_obj.get('VPCId')),
                                    misc.check_if(elb_obj.get('LoadBalancerName')),
                                    misc.check_if(elb_obj.get('Scheme')),
                                    misc.check_if(elb_ip),
                                    misc.check_if(elb_obj.get('DNSName')),
                                    misc.check_if(sg_obj.get('GroupId')),
                                    misc.check_if(sg_obj.get('GroupName')),
                                    misc.check_if(group.get('GroupId')),
                                    misc.check_if(str(check_port(rule.get('FromPort')))),
                                    misc.check_if(str(check_port(rule.get('ToPort')))),
                                    misc.check_if(str(check_proto(rule.get('IpProtocol'))))
                                    )))




