from distutils.util import execute
from http.client import responses
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate

#for creds
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#SCANNER GSHEET CREDS
scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(ROOT_DIR, 'client.json'), scope)
client = gspread.authorize(creds)

folder_id = '1VFKzwum9X1j7BrLJCCfjZ_2bCIZHPplY'

response = client.files().list().execute()

print(responses)