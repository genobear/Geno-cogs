import os
import gspread
from tabulate import tabulate
from oauth2client.service_account import ServiceAccountCredentials

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(ROOT_DIR, 'client.json'), scope)
client = gspread.authorize(creds)

sheet = client.open('INS').sheet1
sheetDetails = sheet.get_all_values()
IDColumn = sheet.col_values(2)

discordID = input("Enter discord ID : ") #This would be the !scan userID command

if discordID in IDColumn:
    for a in sheetDetails:
        if a[1] == discordID:
            print(tabulate([["Servers Found on:","Joined at:","Known Names:"],
                            [a[2],a[3],a[5]]],headers='firstrow',tablefmt='psql'))
            #print("User " + str(a[0]) + " is in these discords :\n" + a[2])
else:
    print("User not in database")