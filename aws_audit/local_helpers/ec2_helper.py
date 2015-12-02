"""
ec2 helper calls.
"""
import boto3
import re
import time
import datetime
import dateutil.parser

from local_helpers import misc


def date_to_days(time_stamp):
    if time_stamp:
        today = datetime.datetime.now()
        create_date = datetime.datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        return str((today - create_date).days)
    else:
        return str('-1')

def ec2_resource(session):
    #print type(session)
    """continue form multithread call
    returns an ec2 resource
    Args:
        session (session.Session()): 
    """
    ec2 = session.resource('ec2')
    for instance in ec2.instances.all():
        #print instance.private_dns_name
        print instance.id


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

def describe_key_pairs_header():
    """generate output header"""
    return misc.format_line((
    "Account",
    "Region",
    "KeyName",
    "Fingerprint" 
    )) 

def describe_key_pairs(ec2, account, region, output_bucket):
    """continue from multithread ec2.describe_key_pairs() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    for key_pair in ec2.describe_key_pairs().get('KeyPairs'):
        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(region.get('RegionName')),
            misc.check_if(key_pair.get('KeyName')),
            misc.check_if(key_pair.get('KeyFingerprint'))
            )))

def describe_instances_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "ec2Id",
           "Type",
           "State",
           "ec2Name",
           "PrivateIPAddress",
           "PublicIPAddress",
           "KeyPair"
            ))

def describe_instances(ec2, account, region, output_bucket):
    """continue from multithread ec2.describe_instances() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    ec2_list =  [i for r in
                ec2.describe_instances().get('Reservations') for i in
                r.get('Instances')]

    for ec2_obj in ec2_list:
            #print ec2_obj
            output_bucket.append(misc.format_line((
                  misc.check_if(account.get('name')),
                  misc.check_if(region.get('RegionName')),
                  misc.check_if(ec2_obj.get('VpcId')),
                  misc.check_if(ec2_obj.get('InstanceId')),
                  misc.check_if(ec2_obj.get('InstanceType')),
                  misc.check_if(ec2_obj.get('State').get('Name')),
                  misc.check_if(check_tag(ec2_obj, str('Name'))),
                  misc.check_if(ec2_obj.get('PrivateIpAddress')),
                  misc.check_if(ec2_obj.get('PublicIpAddress')),
                  misc.check_if(ec2_obj.get('KeyName'))
                  )))

def security_group_list_header():
    """return header for security group list"""
    return misc.format_line((
           "Account",
            "VpcId",
            "Region",
            "GroupID",
            "Instances",
            "SG-GroupName",
            "RFC",
            "Description"))

def security_group_list(ec2, account, region, output_bucket):
    """generate list of ec2s to check agains security groups
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """

    """could not find ec2.instances() anywhere in boto3"""
    ec2_list =  [i for r in
                ec2.describe_instances().get('Reservations') for i in
                r.get('Instances')]

    """generate security group list"""
    sg_list = ec2.describe_security_groups().get('SecurityGroups')

    for sg_obj in sg_list:
        ec2count = 0
        """find out how many ec2s are using a security group"""
        for ec2_obj in ec2_list:
            for sg in ec2_obj.get('SecurityGroups'):
                if sg_obj.get('GroupId') == sg.get('GroupId'):
                    ec2count += 1

        output_bucket.append(misc.format_line((
                  misc.check_if(account.get('name')),
                  misc.check_if(sg_obj.get('VpcId')),
                  misc.check_if(region.get('RegionName')),
                  misc.check_if(sg_obj.get('GroupId')),
                  misc.check_if(str(ec2count)),
                  misc.check_if(sg_obj.get('GroupName')),
                  misc.check_if(check_tag(sg_obj, str('RFC'))),
                  misc.check_if(re.sub('[,]', '-', sg_obj.get('Description')))
                  )))

def sg_rule_sets_header():
    """returns header for sg rule sets"""
    return misc.format_line((
           "AccountId",
           "VpcId",
           "Region",
           "GroupId",
           "SG-GroupName",
           "Source",
           "FromPort",
           "ToPort",
           "Protocol"))

def sg_rule_sets(ec2, account, region, output_bucket):
    """generate list of security group rule sets 
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """

    """generate security group list"""
    sg_list = ec2.describe_security_groups().get('SecurityGroups')

    for sg_obj in sg_list:
        for rule in sg_obj.get('IpPermissions'):
            """cidr as source"""
            for cidr in rule.get('IpRanges'):
                if cidr.get('CidrIp'):
                    output_bucket.append(misc.format_line((
                        misc.check_if(account.get('name')),
                        misc.check_if(sg_obj.get('VpcId')),
                        misc.check_if(region.get('RegionName')),
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
                        misc.check_if(sg_obj.get('VpcId')),
                        misc.check_if(region.get('RegionName')),
                        misc.check_if(sg_obj.get('GroupId')),
                        misc.check_if(sg_obj.get('GroupName')),
                        misc.check_if(group.get('GroupId')),
                        misc.check_if(str(check_port(rule.get('FromPort')))),
                        misc.check_if(str(check_port(rule.get('ToPort')))),
                        misc.check_if(str(check_proto(rule.get('IpProtocol'))))
                        )))

def sg_rule_sets_by_ec2_header():
    """returns header for sg rule sets"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "ec2Id",
           "State",
           "ec2Name",
           "PrivateIPAddress",
           "PublicIPAddress",
           "GroupID",
           "GroupName",
           "Source",
           "StartPort",
           "EndPort",
           "Protocol"))

def sg_rule_sets_by_ec2(ec2, account, region, output_bucket):
    """generate list of security group rule sets by ec2 instance 
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """

    """could not find ec2.instances() anywhere in boto3"""
    ec2_list =  [i for r in
                ec2.describe_instances().get('Reservations') for i in
                r.get('Instances')]

    """generate security group list"""
    sg_list = ec2.describe_security_groups().get('SecurityGroups')

    for sg_obj in sg_list:
        """find out how many ec2s are using a security group"""
        for ec2_obj in ec2_list:
            for ec2sg in ec2_obj.get('SecurityGroups'):
                if sg_obj.get('GroupId') == ec2sg.get('GroupId'):
                    """move on to rule entries"""
                    for rule in sg_obj.get('IpPermissions'):
                        """cidr as source"""
                        for cidr in rule.get('IpRanges'):
                            if cidr.get('CidrIp'):
                                output_bucket.append(misc.format_line((
                                    misc.check_if(account.get('name')),
                                    misc.check_if(region.get('RegionName')),
                                    misc.check_if(sg_obj.get('VpcId')),
                                    misc.check_if(ec2_obj.get('InstanceId')),
                                    misc.check_if(ec2_obj.get('State').get('Name')),
                                    misc.check_if(check_tag(ec2_obj, str('Name'))),
                                    misc.check_if(ec2_obj.get('PrivateIpAddress')),
                                    misc.check_if(ec2_obj.get('PublicIpAddress')),
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
                                    misc.check_if(sg_obj.get('VpcId')),
                                    misc.check_if(ec2_obj.get('InstanceId')),
                                    misc.check_if(ec2_obj.get('State').get('Name')),
                                    misc.check_if(check_tag(ec2_obj, str('Name'))),
                                    misc.check_if(ec2_obj.get('PrivateIpAddress')),
                                    misc.check_if(ec2_obj.get('PublicIpAddress')),
                                    misc.check_if(sg_obj.get('GroupId')),
                                    misc.check_if(sg_obj.get('GroupName')),
                                    misc.check_if(group.get('GroupId')),
                                    misc.check_if(str(check_port(rule.get('FromPort')))),
                                    misc.check_if(str(check_port(rule.get('ToPort')))),
                                    misc.check_if(str(check_proto(rule.get('IpProtocol'))))
                                    )))


def sg_rule_sets_by_ec2_with_role_header():
    """returns header for sg rule sets"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "ec2Id",
           "Role",
           "State",
           "ec2Name",
           "PrivateIPAddress",
           "PublicIPAddress",
           "GroupID",
           "GroupName",
           "Source",
           "StartPort",
           "EndPort",
           "Protocol"))

def sg_rule_sets_by_ec2_with_role(ec2, account, region, output_bucket):
    """generate list of security group rule sets by ec2 instance 
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """

    """could not find ec2.instances() anywhere in boto3"""
    ec2_list =  [i for r in
                ec2.describe_instances().get('Reservations') for i in
                r.get('Instances')]

    """generate security group list"""
    sg_list = ec2.describe_security_groups().get('SecurityGroups')


    for sg_obj in sg_list:
       """find out how many ec2s are using a security group"""
       for ec2_obj in ec2_list:
          """check if ec2 is attached to a role"""
          if ec2_obj.get('IamInstanceProfile'):
             ec2_role = re.split('/',ec2_obj.get('IamInstanceProfile').get('Arn'))[1]
             for ec2sg in ec2_obj.get('SecurityGroups'):
                 if sg_obj.get('GroupId') == ec2sg.get('GroupId'):
                    """move on to rule entries"""
                    for rule in sg_obj.get('IpPermissions'):
                        """cidr as source"""
                        for cidr in rule.get('IpRanges'):
                            if cidr.get('CidrIp'):
                                output_bucket.append(misc.format_line((
                                    misc.check_if(account.get('name')),
                                    misc.check_if(region.get('RegionName')),
                                    misc.check_if(sg_obj.get('VpcId')),
                                    misc.check_if(ec2_obj.get('InstanceId')),
                                    misc.check_if(ec2_role),
                                    misc.check_if(ec2_obj.get('State').get('Name')),
                                    misc.check_if(check_tag(ec2_obj, str('Name'))),
                                    misc.check_if(ec2_obj.get('PrivateIpAddress')),
                                    misc.check_if(ec2_obj.get('PublicIpAddress')),
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
                                    misc.check_if(sg_obj.get('VpcId')),
                                    misc.check_if(ec2_obj.get('InstanceId')),
                                    misc.check_if(ec2_role),
                                    misc.check_if(ec2_obj.get('State').get('Name')),
                                    misc.check_if(check_tag(ec2_obj, str('Name'))),
                                    misc.check_if(ec2_obj.get('PrivateIpAddress')),
                                    misc.check_if(ec2_obj.get('PublicIpAddress')),
                                    misc.check_if(sg_obj.get('GroupId')),
                                    misc.check_if(sg_obj.get('GroupName')),
                                    misc.check_if(group.get('GroupId')),
                                    misc.check_if(str(check_port(rule.get('FromPort')))),
                                    misc.check_if(str(check_port(rule.get('ToPort')))),
                                    misc.check_if(str(check_proto(rule.get('IpProtocol'))))
                                    ))) 

def describe_snapshots_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "SnapshotId",
           "Age",
           "CreateDate",
           "Size",
           "Encrypted",
           "Description"
            ))

def describe_snapshots(ec2, account, region, output_bucket):
    """continue from multithread describe_snapshots() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    '''extract owner_id from role'''
    owner_id = str(re.split(':',account.get('role_arn'))[4])

    '''get list of snapshots owned by owner_id'''
    snap_list =  ec2.describe_snapshots(OwnerIds=[owner_id]).get('Snapshots')

    for snap_obj in snap_list:
            output_bucket.append(misc.format_line((
                  misc.check_if(account.get('name')),
                  misc.check_if(region.get('RegionName')),
                  misc.check_if(str(snap_obj.get('SnapshotId'))),
                  misc.check_if(str(misc.date_to_days(snap_obj.get('StartTime')))),
                  misc.check_if(str(snap_obj.get('StartTime').strftime('%Y_%m_%d'))),
                  misc.check_if(str(snap_obj.get('VolumeSize'))),
                  misc.check_if(str(snap_obj.get('Encrypted'))),
                  #'''get rid of commas if present'''
                  misc.check_if(str(re.sub('[,]','', snap_obj.get('Description')))),
                  )))

def describe_images_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "ImageId",
           "State",
           "Age",
           "Public",
           "Name"
            ))

def describe_images(ec2, account, region, output_bucket):
    """continue from multithread describe_snapshots() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    '''extract owner_id from role'''
    owner_id = str(re.split(':',account.get('role_arn'))[4])

    '''get list of amis owned by owner_id'''
    ami_list =  ec2.describe_images(Owners=[owner_id]).get('Images')

    for ami_obj in ami_list:
            output_bucket.append(misc.format_line((
                  misc.check_if(account.get('name')),
                  misc.check_if(region.get('RegionName')),
                  misc.check_if(str(ami_obj.get('ImageId'))),
                  misc.check_if(str(ami_obj.get('State'))),
                  misc.check_if(str(date_to_days(ami_obj.get('CreationDate')))),
                  misc.check_if(str(ami_obj.get('Public'))),
                  #'''get rid of commas if present'''
                  misc.check_if(str(re.sub('[,]','', ami_obj.get('Name')))),
                  )))


