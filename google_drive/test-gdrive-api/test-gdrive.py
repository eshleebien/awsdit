#!/usr/bin/env python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload
import os

CLIENT_SECRET = 'client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/drive.file'

store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
    creds = tools.run_flow(flow, store, tools.argparser.parse_args([]))

drive_service = build('drive', 'v2', http=creds.authorize(Http()))

# AWS Automated-Reports Folder
body = {'title': '', 'mimeType': 'application/vnd.google-apps.spreadsheet',
  'parents': [{'kind': "drive#fileLink",'id': "Your-folder-ID-Goes-here"}]
}

#dirpath = '/var/log/aws-audit/'
dirpath = './'
for f in os.listdir(dirpath):
    if f.endswith(".csv"):
        FILEPATH = dirpath + f
        FILENAME = f
        try:
            media_body = MediaFileUpload(FILEPATH, mimetype='text/csv', resumable=True)
            body['title'] = FILENAME
            # Insert a file
            file = drive_service.files().insert(body=body, media_body=media_body).execute()

        except HttpError, error:
            print error

        time.sleep(2)
