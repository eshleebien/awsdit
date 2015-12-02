
# AWSDIT
Internal and external threats combined with human security configuration errors can potentially increase the operational, reputational, financial, and compliance risks of your organization “in” the cloud. AWS provides a comprehensive set of core security controls to mitigate many of these risks, but more often than not such controls tend to be misunderstood by unseasoned and seasoned AWS practitioners alike. 

Budgetary pressure is a universally understood constraint.  While commercial security tools exist to audit your AWS environments, these tools can be prohibitively expensive.  Organizations need a way to quickly answer many of the questions that could potentially put infrastructure at risk due to human error and misconfigurations. 

Enable your organization to quickly find a needle in the Amazon AWS haystack and answer the most common security questions, including: security group misconfigurations, unapproved security groups, inventory of all security groups, inventory of all security rule sets, inventory of all security rule sets per AWS service, orphaned access keys, IAM policy inventories, unnecessary assignments of roles to AWS services, open exposure of RDS instances, S3 policies and ACLs inventory etc.  If you can imagine in, you can visualize it!

This project illustrates the basics of taking periodic AWS configuration snapshots by integrating the AWS SDK for Python (boto) with Google Sheets and Google Apps Script to deliver internal security and compliance teams auditing insights through a technology that they all already use and understand: Google Apps.


## Architecture

![image](https://github.com/ndoit/awsdit/blob/master/google_drive/docs/images/awsdit-arch.png)

SAMPLE: <a href="https://goo.gl/qLTBFy" target="_blank">AWS Access Key Inventory</a>

# Quick Start Guides
- <a href=https://github.com/ndoit/awsdit/blob/master/aws_audit/docs/quickstart.rst>Setup AWS IAM Policies and Roles</a>
- <a href=https://github.com/ndoit/awsdit/blob/master/google_drive/docs/quickstart.rst>Setup for Google Drive API Client</a>
- <a href=https://github.com/ndoit/awsdit/blob/master/google_apps_script/docs/quickstart.rst>Data Representation with Google Apps Script</a>
- <a href=https://github.com/ndoit/awsdit/blob/master/aws_audit/>AWS Data Collection</a>



# Project Resources
- <a href=https://github.com/ndoit/awsdit> Source Code </a>
- <a href=https://github.com/ndoit/awsdit/issues> Issues </a>



