import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from os import getenv

creds_path = './credentials.json'
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file(creds_path, scopes=scope)
GSHEET_ID = getenv("GSHEET_ID")
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/' + GSHEET_ID + '/edit'

df = None
autocomplete_names = []

def update_data():
    global df, autocomplete_names
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url(spreadsheet_url)
        sheet = spreadsheet.get_worksheet(0)
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        autocomplete_names = sorted(df['Romaji'].tolist())
        print("Fetched the following entries:")
        print(autocomplete_names)
    except Exception as e:
        print(f"An error occurred: {e}")

def get_data():
    return df

def get_autocomplete_names():
    return autocomplete_names