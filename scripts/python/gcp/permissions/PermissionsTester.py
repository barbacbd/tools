from google.oauth2 import service_account
from googleapiclient.discovery import build
from colorama import Fore, Style
import os
import argparse

'''GCP Permission Tester

Environment variable GOOGLE_APPLICATION_CREDENTIALS should contain the path to the 
gcp account information required. 

The user should project a project and a list of permissions to test against. The
permisisons that are valid are printed out in green while missing permissions are 
printed in red. 
'''

def print_with_color(color, text):
    '''Print out the data with color'''
    print(color + text + Style.RESET_ALL)


parser = argparse.ArgumentParser(
    prog='PermissionsTester',
    description='Determines what permissions are valid from the list provided by the user'
)
parser.add_argument('project', type=str, help='GCP Project ID')
parser.add_argument('--permissions', type=str, nargs='+', help='list of permissions to test against')
args = parser.parse_args()

credentials = service_account.Credentials.from_service_account_file(
    filename=os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
service = build(
    "cloudresourcemanager", "v1", credentials=credentials
)

permissions = {"permissions": args.permissions}

request = service.projects().testIamPermissions(
    resource=args.project, body=permissions
)


returned = request.execute()
returnedPermissions = returned.get('permissions', [])
if returnedPermissions:
    retPermStr = '\n'.join(returnedPermissions)
    print_with_color(Fore.GREEN, retPermStr)

missingPermissions = list(set(args.permissions).difference(set(returnedPermissions)))
if missingPermissions:
    missPermStr = '\n'.join(missingPermissions)
    print_with_color(Fore.RED, missPermStr)
