import boto3
import json
import csv
import time
from datetime import date
from datetime import datetime

# create a session to retrieve 'admin' credentials from ~/.aws/credentials
session = boto3.Session(profile_name='admin')

# create a low-level client with the iam service
iam = session.client('iam')

# Get the credential report from the client
def get_cred_report():
    x = 0
    status = ""
    try:
        while iam.generate_credential_report()['State'] != "COMPLETE":
            time.sleep(10) #increasing the timeout as frequently checking results in 503 error.
            x += 1
            # If no credentail report is delivered within this time fail the check.
            if x > 10:
                status = "Fail: no Credential Report available."
                break
        if "Fail" in status: # if the string "Fail" is in the status variable
            return status # return "Fail..." error and end function
        response = iam.get_credential_report()

        cred_report_csv = response['Content'].decode('utf-8') # decode from utf-8 to string
        report = [] # blank dictionary

        #DictReader reads the CSV file and separates strings by commas (delimiter)
        reader = csv.DictReader(cred_report_csv.splitlines(), delimiter=',')

        for row in reader: # for every row in the dictionary...
            report.append(row) # append a row at a time to the "report" dictionary
        return report # once you've made it through every row in reader, end this function
    except Exception as e:
        print("encountered Error with generate_credential_report: " + str(e))
        if (str(e).find('Rate exceeded') != -1):
            print('seems like the generateCredentialReport throttling error. So just download the report...')
            response = iam.get_credential_report()
            cred_report_csv = response['Content'].decode('utf-8')
            report = []
            reader = csv.DictReader(cred_report_csv.splitlines(), delimiter=',')
            for row in reader:
                report.append(row)
            return report

# Store the output of this function in report
report = get_cred_report()

report_string = ''''''

# Print report in JSON format, with 4 spaces for indentation, then store as a string
report_string = ('{\n"report": ' + json.dumps(report, indent=4) + '\n}\n')

data = json.loads(report_string)

print('\n*** Custom IAM Credential Report ***')

print('\nThe following users do not have MFA enabled: ')
for user in data['report']: # for every object in this report..
    if user['mfa_active'] == 'false': # if this user doesn't have MFA enabled..
        print(user['user']) # print their name

print('\nThe following users have console access: ')
for user in data['report']:
    if user['password_last_used'] != 'N/A':
        print(user['user'])

# get today's date, no time
date_format = "%Y-%m-%d"
now_date = (datetime.now().date()) # returns just the date as datetime.date type

print('\nThe following users have access keys (key age in parenthesis): ')
for user in data['report']:
    if user['access_key_1_active'] == 'true': # if this user has an access key..
        last_rotated_unicode = user['access_key_1_last_rotated'] # get the date it was last rotated (unicode)
        last_rotated_date = datetime.strptime(last_rotated_unicode, '%Y-%m-%dT%H:%M:%S+00:00').date() #convert to datetime.date format
        difference = (now_date - last_rotated_date) # calculate the difference in days between 2 dates
        print(user['user'] + ' (' + str(difference.days) + ' days)') # print the username and how old their key is in days
print('\n')
