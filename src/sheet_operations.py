import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Use credentials to create gspread client
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', SCOPE)
CLIENT = gspread.authorize(CREDS)

# Open the spreadsheet
SHEET = CLIENT.open('Betting').worksheet('Devig')  # Replace with your sheet name


def write_to_sheet(values):
    try:
        SHEET.append_row(values, value_input_option='USER_ENTERED')
    except gspread.exceptions.APIError:
        # Refresh credentials if expired
        global CLIENT
        CLIENT = gspread.authorize(CREDS)
        SHEET.append_row(values)
