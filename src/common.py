import os
import pandas as pd

def validate_launch_time():
    start = os.environ.get("START")
    finish = os.environ.get("FINISH")
    if not start:
        start = 16
    if not finish:
        finish = 8
    start_time = int(start)
    finish_time = int(finish)
    return start_time, finish_time


def check_table():
    if "stats.csv" not in os.listdir():
        df = pd.DataFrame(columns=['Success', 'Date', 'Link', 'Processed Time', 'Accessed Time', 'Answered/Quote was posted at', 'Name if exists'])
        df.to_csv('stats.csv', index=False)
        print("created new table")
    else:
        df = pd.read_csv("stats.csv")
    return df


def make_a_record(current_session, new_row):
    df = check_table()
    new_row_df = pd.Series({'Success': new_row.success,
                            'Date': new_row.date,
                            'Link': new_row.link,
                            'Processed Time': new_row.processed,
                            'Accessed Time': new_row.accessed,
                            'Answered/Quote was posted at': new_row.answered,
                            'Name if exists': new_row.name})
    df = df.append(new_row_df, ignore_index=True)
    df.to_csv("stats.csv", index=False)
    print("recorded!")


def make_a_yelper_record(new_row):
    ### this must be changed to online sync
    if "yelpers_stats.csv" not in os.listdir():
        df = pd.DataFrame(columns=['Success',
                                   'When quote appeared',
                                   'Link', 
                                   'Answered/Quote was posted at',
                                   'Name if exists',
                                   "Current location ZIP",
                                   "Destination ZIP",
                                   "TrekMovers District",
                                   "Moving date",
                                   "Size"])

        df.to_csv("yelpers_stats.csv", index=False)
        print("created new table")
    else:
        df = pd.read_csv("yelpers_stats.csv")
        
    new_row_df = pd.Series({'Success': new_row.success,
                            'When quote appeared': new_row.date,
                            'Link': new_row.link,
                            'Answered/Quote was posted at': new_row.answered,
                            'Name if exists': new_row.name,
                            "Current location ZIP": new_row.movefrom,
                            "Destination ZIP": new_row.moveto,
                            "TrekMovers District": new_row.district,
                            "Moving date": new_row.movewhen,
                            "Size": new_row.size,
                            "Direct?": new_row.direct})
    df = df.append(new_row_df, ignore_index=True)
    df.to_csv("yelpers_stats.csv", index=False)
    print("yelpers stats recorded!")
    
    
class RecordClass:
    def __init__(self):
        self.success = None
        self.date = None
        self.link = None
        self.processed = None
        self.accessed = None
        self.answered = None
        self.name = None
        self.movefrom = None
        self.moveto = None
        self.district = None
        self.size = None
        self.movewhen = None
        self.direct = False
    
    def assign_direct_fields(self, direct_quote):
        self.name = direct_quote.name
        self.movefrom = direct_quote.movefrom
        self.moveto = direct_quote.moveto
        self.district = direct_quote.district
        self.size = direct_quote.size
        self.movewhen = direct_quote.movewhen
        self.direct = True

    def parse_link_for_district(self):
        if "_wnBeUDshFbA3kh-MAqa6g" in self.link:
            self.district = "Trek LA"
        elif "ws6UJDDSo1cB8fc6f4A9BQ" in self.link:
            self.district = "Trek San Jose"
        elif "vKVDWIaMRSss3kZAkFbmBA" in self.link:
            self.district = "Trek Orange County"
        elif "6CV3T3cJwl9z3393c9VdVw" in self.link:
            self.district = "Trek Thousand Oaks"