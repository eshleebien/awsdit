"""
code_deploy helper calls
"""
import boto3
import datetime
import dateutil.parser
import re

from local_helpers import misc

def list_apps_header():
    """generate output header"""
    return misc.format_line((
           "Account",
           "Region",
           "AppName",
           "linkedToGitHub",
           "CreateDate",
           "Age",
           "DeployGroupName",
           "RevisionType",
           "Instances",
           "serviceRoleArn"
            ))

def list_apps(codedeploy, account, region, output_bucket):
    """continue from multithread call
    Args: 
        code deploy (object): code deploy client object 
        account (dict): aws accounts 
        output_bucket (list): results bucket holder 
    Returns:
        nothing. appends results to output_bucket
    """
    app_list = None
    try:
        '''get list of apps'''
        app_list = codedeploy.list_applications().get('applications')
    except Exception, e:
        error_code = e

    if app_list:
        '''collect all info about the app'''
        for app_obj in app_list:
            app_info = codedeploy.get_application(
                             applicationName=app_obj
                             ).get('application')

            app_groups = codedeploy.list_deployment_groups(
                             applicationName=app_obj
                             ).get('deploymentGroups')
             
            for group_name in app_groups:
                dep_group = codedeploy.get_deployment_group(
                                 applicationName=app_obj,
                                 deploymentGroupName=group_name
                                 ).get('deploymentGroupInfo')

                deployments = codedeploy.list_deployments(
                                 applicationName=app_obj,
                                 deploymentGroupName=group_name
                                 ).get('deployments')
                for deployment_name in deployments:
                    instances = '<br>'.join(codedeploy.list_deployment_instances(
                                deploymentId=deployment_name
                                ).get('instancesList'))

                    output_bucket.append(misc.format_line((
                        misc.check_if(account.get('name')),
                        misc.check_if(region.get('RegionName')),
                        misc.check_if(str(app_info.get('applicationName'))),
                        misc.check_if(str(app_info.get('linkedToGitHub'))),
                        misc.check_if(str(app_info.get('createTime').strftime('%Y_%m_%d'))),
                        misc.check_if(str(misc.date_to_days(app_info.get('createTime')))),
                        misc.check_if(str(group_name)),
                        misc.check_if(str(dep_group.get('targetRevision').get('revisionType'))),
                        misc.check_if(str(instances)),
                        misc.check_if(str(dep_group.get('serviceRoleArn'))),
                        )))


