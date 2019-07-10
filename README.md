# AWS-IAM-Report
Python code that uses the Boto3 SDK to retrieve specified information about your IAM users in AWS

My goal with this code was to automate a credential report from IAM to retrieve the following information:
1. Which users don't have MFA enabled
2. Which users have console access
3. Which users have access keys, and how old those keys are

**Note: If you haven't run this script in 4 hours or so it will take 10 seconds to produce, if it passes error checking

This script could be useful to run regular audits on a AWS account, and serves as a template for retrieving more IAM information.
Many thanks to Balaji R. for his help with this code.
