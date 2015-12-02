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

def describe_vpcs_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "VpcName",
           "State",
           "VpcCidr",
           "VpcDefault",
           "Tenancy",
           "DhcpOptionsId"
            ))

def describe_vpcs(ec2, account, region, output_bucket):
    """continue from multithread ec2.describe_instances() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    vpc_list = ec2.describe_vpcs().get('Vpcs')
    for vpc_obj in vpc_list:
        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(region.get('RegionName')),
            misc.check_if(vpc_obj.get('VpcId')),
            misc.check_if(check_tag(vpc_obj, str('Name'))),
            misc.check_if(vpc_obj.get('State')),
            misc.check_if(vpc_obj.get('CidrBlock')),
            misc.check_if(str(vpc_obj.get('IsDefault'))),
            misc.check_if(vpc_obj.get('InstanceTenancy')),
            misc.check_if(vpc_obj.get('DhcpOptionsId'))
            )))

def describe_vpc_peering_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "PeerName",
           "RequesterOwner",
           "RequesterVpc",
           "RequesterCidr",
           "AccepterOwner",
           "AccepterVpc",
           "AccepterCidr",
           "Status",
           "PeeringID"
            ))

def describe_vpc_peering(ec2, account, region, output_bucket):
    """continue from multithread ec2.describe_instances() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    peer_list = ec2.describe_vpc_peering_connections().get('VpcPeeringConnections')
    for peer_obj in peer_list:
        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(region.get('RegionName')),
            misc.check_if(check_tag(peer_obj, str('Name'))),
            #'''redact account owner number'''
            misc.check_if('...' + str(peer_obj.get('RequesterVpcInfo').get('OwnerId')[6:])),
            misc.check_if(peer_obj.get('RequesterVpcInfo').get('VpcId')),
            misc.check_if(peer_obj.get('RequesterVpcInfo').get('CidrBlock')),
            #'''redact account owner number'''
            misc.check_if('...' + str(peer_obj.get('AccepterVpcInfo').get('OwnerId')[6:])),
            misc.check_if(peer_obj.get('AccepterVpcInfo').get('VpcId')),
            misc.check_if(peer_obj.get('AccepterVpcInfo').get('CidrBlock')),
            misc.check_if(peer_obj.get('Status').get('Message')),
            misc.check_if(peer_obj.get('VpcPeeringConnectionId')),
            )))

def describe_vpn_connections_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "VpcCidr",
           "VpnName",
           "VpnId",
           "State",
           "CutomerGwId",
           "CutomerGwAddress",
           "Type"
            ))

def describe_vpn_connections(ec2, account, region, output_bucket):
    """continue from multithread ec2.describe_instances() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    vpn_list = ec2.describe_vpn_connections().get('VpnConnections')
    for vpn_obj in vpn_list:
        '''extract VpcId from virtual private gateway information'''
        vpn_cgw = ec2.describe_vpn_gateways(
                 VpnGatewayIds =
                 [vpn_obj.get('VpnGatewayId')]
        ).get('VpnGateways')
        for cgw_attachment in vpn_cgw:
            for vpc_obj in cgw_attachment.get('VpcAttachments'):
                vpc_id = str(vpc_obj.get('VpcId'))
                '''now extract vpc cidr info'''
                vpc_obj2 = ec2.describe_vpcs(
                          VpcIds = [vpc_id]
                          ).get('Vpcs')
                for vpc_net in vpc_obj2:
                    vpc_cidr = str(vpc_net.get('CidrBlock'))

        '''need customer gateway to extract remote customer ip'''
        customer_gw = ec2.describe_customer_gateways(
                         CustomerGatewayIds = 
                         [vpn_obj.get('CustomerGatewayId')]
                         ).get('CustomerGateways')

        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(region.get('RegionName')),
            misc.check_if(vpc_id),
            misc.check_if(vpc_cidr),
            misc.check_if(check_tag(vpn_obj, str('Name'))),
            misc.check_if(vpn_obj.get('VpnConnectionId')),
            misc.check_if(vpn_obj.get('State')),
            misc.check_if(vpn_obj.get('CustomerGatewayId')),
            misc.check_if(str('/'.join(i.get('IpAddress') 
                                  for i in customer_gw))),
            misc.check_if(vpn_obj.get('Type')),
            )))

def describe_route_tables_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "RtSubnets",
           "RouteTableId",
           "RouteTableName",
           "Destination",
           "Target",
           "Status",
           "Propagated"
            ))

def rtable_q_target(route_entry):
        """
        Args:
            route_entry: (dict)
        Returns:
            string: returns route table entry destination exit point
        """
        if route_entry.get('GatewayId'): 
            return route_entry.get('GatewayId')
        elif route_entry.get('InstanceId'): 
            return route_entry.get('InstanceId')
        elif route_entry.get('VpcPeeringConnectionId'): 
            return route_entry.get('VpcPeeringConnectionId')
        else:
            return 'no-record'

def rtable_q_dest(route_entry):
        """
        Args:
            route_entry: (dict)
        Returns:
            string: returns route table destination 
        """
        if route_entry.get('DestinationCidrBlock'):
            return route_entry.get('DestinationCidrBlock')  
        elif route_entry.get('DestinationPrefixListId'):
            return route_entry.get('DestinationPrefixListId')
        else:
            return 'no-record'

def rtable_q_propagate(route_entry):
        """
        Args:
            route_entry: (dict)
        Returns:
            string: returns route propagation 
        """
        if str(
              route_entry.get('Origin')
                          ) == 'EnableVgwRoutePropagation':
            return 'True'
        else:
            return 'False'

def rtable_q_assocs(route_table):
        counter = 0
        """
        Args:
            route_entry: (dict)
        Returns:
            int: number of subnet associations 
        """
        for assoc in route_table.get('Associations'):
            if assoc.get('SubnetId'):
                counter += 1 

        return str(counter)

def describe_route_tables(ec2, account, region, output_bucket):
    """continue from multithread ec2.describe_instances() call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    rtable_list = ec2.describe_route_tables().get('RouteTables')
    for rtable_obj in rtable_list:
        #subnet_assocs = str(len(rtable_obj.get('Associations')))
        subnet_assocs = rtable_q_assocs(rtable_obj)
        r_entry_list = rtable_obj.get('Routes')
        for r_entry in r_entry_list:
            output_bucket.append(misc.format_line((
                misc.check_if(account.get('name')),
                misc.check_if(region.get('RegionName')),
                misc.check_if(rtable_obj.get('VpcId')),
                misc.check_if(subnet_assocs),
                misc.check_if(rtable_obj.get('RouteTableId')),
                misc.check_if(check_tag(rtable_obj, str('Name'))),
                misc.check_if(rtable_q_dest(r_entry)),
                misc.check_if(rtable_q_target(r_entry)),
                misc.check_if(r_entry.get('State')),
                misc.check_if(rtable_q_propagate(r_entry)),
                )))

def describe_subnets_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "SubnetName",
           "SubnetId",
           "State",
           "FlowEnabled",
           "CidrBlock",
           "AvailableIPs",
           "DefaultForAz",
           "PublicIpOnLaunch"
            ))

def describe_subnets(ec2, account, region, output_bucket):
    """continue from multithread call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    subnet_list = ec2.describe_subnets().get('Subnets')
    for subnet_obj in subnet_list:
        """check if flow have been enabled for this subnet"""
        sub_flow_logs = None
        try:
            sub_flow_logs = ec2.describe_flow_logs(
                Filter=[ {   'Name': 'resource-id',
                             'Values': [ subnet_obj.get('SubnetId') ]
                   } ] ).get('FlowLogs')

        except Exception, e:
            error_code = e
        
        if sub_flow_logs:
            flow_enabled = str('True')
        else:
            flow_enabled = str('False')

        output_bucket.append(misc.format_line((
            misc.check_if(account.get('name')),
            misc.check_if(region.get('RegionName')),
            misc.check_if(subnet_obj.get('VpcId')),
            misc.check_if(check_tag(subnet_obj, str('Name'))),
            misc.check_if(subnet_obj.get('SubnetId')),
            misc.check_if(subnet_obj.get('State')),
            misc.check_if(flow_enabled),
            misc.check_if(subnet_obj.get('CidrBlock')),
            misc.check_if(str(subnet_obj.get('AvailableIpAddressCount'))),
            misc.check_if(str(subnet_obj.get('DefaultForAz'))),
            misc.check_if(str(subnet_obj.get('MapPublicIpOnLaunch')))
            )))

def describe_network_acls_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "VpcId",
           "NetAclName",
           "NetAclId",
           "Default",
           "RuleNumber",
           "Direction",
           "Protocol",
           "IpCidr",
           "Action"
            ))

def describe_network_acls(ec2, account, region, output_bucket):
    """continue from multithread call
    Args: 
        ec2 (object): ec2 client object 
        account (dict): aws accounts 
        region (dict): regions
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    netacl_list = ec2.describe_network_acls().get('NetworkAcls')
    for acl_obj in netacl_list:

        for rule_obj in acl_obj.get('Entries'):
            '''extract direction'''
            direction = 'inbound'
            if str(rule_obj.get('Egress')) == 'True':
               direction = 'outbound'

            output_bucket.append(misc.format_line((
                misc.check_if(account.get('name')),
                misc.check_if(region.get('RegionName')),
                misc.check_if(acl_obj.get('VpcId')),
                misc.check_if(check_tag(acl_obj, str('Name'))),
                misc.check_if(acl_obj.get('NetworkAclId')),
                misc.check_if(str(acl_obj.get('IsDefault'))),
                misc.check_if(str(rule_obj.get('RuleNumber'))),
                misc.check_if(str(direction)),
                misc.check_if(str(rule_obj.get('Protocol'))),
                misc.check_if(str(rule_obj.get('CidrBlock'))),
                misc.check_if(str(rule_obj.get('RuleAction')))
                )))

