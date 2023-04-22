import os

import flask
import google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from application.shared.helpers import credentials_to_dict
from application.tools.GoogleSheetsTool import GoogleSheetsBatchUpdateTool, GoogleSheetsCreateTool, GoogleSheetsGetTool, \
    GoogleSheetsValuesBatchUpdateTool, AppScriptUpdateTool, AppScriptRunScriptTool
from application.tools.GoogleSheetsToolWrapper import GoogleSheetsToolWrapper, AppScriptToolWrapper

dirname = os.path.dirname(__file__)
client_secrets_filename = os.path.join(dirname, '../../.env/client_secrets.json')
token_filename = os.path.join(dirname, '../../.env/token.json')

SCOPES = ['https://www.googleapis.com/auth/script.projects']

def get_local_cred():
    creds = None
    if os.path.exists('../../.env/token.json'):
        creds = Credentials.from_authorized_user_file('../../.env/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_filename, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_filename, 'w') as token:
            token.write(creds.to_json())
    return creds
def get_oauth_cred():
    creds = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    flask.session['credentials'] = credentials_to_dict(creds)

    if creds.refresh_token is 'None' or '' and 'refresh_token' in flask.session:
        creds.refresh_token = flask.session['refresh_token']

    return creds
def get_appscript_service():
    return build('script', 'v1', credentials=get_oauth_cred())

def get_sheets_service():
    return build('sheets', 'v4', credentials=get_oauth_cred())


def load_tools():
    tools = []

    # App Script Version
    service = get_appscript_service()
    tools.append(AppScriptUpdateTool(api_wrapper=AppScriptToolWrapper(service=service)))
    tools.append(AppScriptRunScriptTool(api_wrapper=AppScriptToolWrapper(service=service)))

    # # Original Version
    # service = get_sheets_service()
    # tools.append(GoogleSheetsCreateTool(api_wrapper=GoogleSheetsToolWrapper(service=service)))
    # tools.append(GoogleSheetsGetTool(api_wrapper=GoogleSheetsToolWrapper(service=service)))
    # tools.append(GoogleSheetsValuesBatchUpdateTool(api_wrapper=GoogleSheetsToolWrapper(service=service)))
    return tools
