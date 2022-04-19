import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

def upload_crm(content):
    credentials = ServiceAccountCredentials.from_json_keyfile_name('secret_files/credentials_driver_trek.json', scope)
    client = gspread.authorize(credentials)
    
    spreadsheet = client.open('Bot CRM dump')
    client.import_csv(spreadsheet.id, data=content)
    print("document updated!")


def validate_launch_time():
    start = os.environ.get("START")
    finish = os.environ.get("FINISH")
    if not start:
        start = 00
    if not finish:
        finish = 00
    start_time = int(start)
    finish_time = int(finish)
    return start_time, finish_time


def make_a_yelper_record(new_row):
    ### this must be changed to online sync
    if "yelpers_stats.csv" not in os.listdir():
        df = pd.DataFrame(columns=['When quote appeared',
                                   'Time quote appeared',
                                   "Direct / Nearby",
                                   'Link', 
                                   'Name if exists',
                                   "Current location ZIP",
                                   "Destination ZIP",
                                   "TrekMovers YELP Location",
                                   "Size",
                                   "Moving date"
                                   ])

        df.to_csv("yelpers_stats.csv", index=False)
        print("created new table")
    else:
        df = pd.read_csv("yelpers_stats.csv")
    if "Time quote appeared" not in df.columns:
        df.insert(1, "Time quote appeared", None)
    new_row_df = pd.Series({'When quote appeared': new_row.date,
                            "Time quote appeared": new_row.time,
                            "Direct / Nearby": new_row.direct,
                            'Link': new_row.link,
                            'Name if exists': new_row.name,
                            "Current location ZIP": new_row.movefrom,
                            "Destination ZIP": new_row.moveto,
                            "TrekMovers YELP Location": new_row.district,
                            "Size": new_row.size,
                            "Moving date": new_row.movewhen
                            })
    
    if new_row.link not in df['Link'].values:
        df = df.append(new_row_df, ignore_index=True)
        #df = df.sort_values(by="When quote appeared", ascending=False)
        df = df.iloc[::-1].reset_index(drop=True)
        df.to_csv("yelpers_stats.csv", index=False)   

        print("yelpers stats recorded!")        
        with open('yelpers_stats.csv', 'r') as file_obj:
            content = file_obj.read()
            upload_crm(content)        
        df = df.iloc[::-1].reset_index(drop=True)
        df.to_csv("yelpers_stats.csv", index=False)              
        

    
    
class RecordClass:
    def __init__(self):
        self.date = None
        self.time = None
        self.link = None
        self.name = None
        self.movefrom = None
        self.moveto = None
        self.district = None
        self.size = None
        self.movewhen = None
        self.direct = None
    
    def assign_fields(self, quote):
        self.name = quote.name
        self.movefrom = quote.movefrom
        self.moveto = quote.moveto
        self.district = quote.district
        self.size = quote.size
        self.movewhen = quote.movewhen
        self.link = quote.link
        self.direct = quote.direct
        
