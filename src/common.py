import os
import pandas as pd

def validate_launch_time():
    start = os.environ.get("START")
    finish = os.environ.get("FINISH")
    if not start:
        start = 14
    if not finish:
        finish = 11
    start_time = int(start)
    finish_time = int(finish)
    return start_time, finish_time


def make_a_yelper_record(new_row):
    ### this must be changed to online sync
    if "yelpers_stats.csv" not in os.listdir():
        df = pd.DataFrame(columns=[
                                   'When quote appeared',
                                   'Link', 
                                   'Name if exists',
                                   "Current location ZIP",
                                   "Destination ZIP",
                                   "TrekMovers YELP Location",
                                   "Moving date",
                                   "Size",
                                   "Direct / Nearby"])

        df.to_csv("yelpers_stats.csv", index=False)
        print("created new table")
    else:
        df = pd.read_csv("yelpers_stats.csv")
        
    new_row_df = pd.Series({
                            'When quote appeared': new_row.date,
                            'Link': new_row.link,
                            'Name if exists': new_row.name,
                            "Current location ZIP": new_row.movefrom,
                            "Destination ZIP": new_row.moveto,
                            "TrekMovers YELP Location": new_row.district,
                            "Moving date": new_row.movewhen,
                            "Size": new_row.size,
                            "Direct / Nearby": new_row.direct})
    #if not len(df[df['Link'].str.contains(new_row.link)]):
    if new_row.link not in df['Link'].values:
        df = df.append(new_row_df, ignore_index=True)
        df.to_csv("yelpers_stats.csv", index=False)
        print("yelpers stats recorded!")
    
    
class RecordClass:
    def __init__(self):
        self.date = None
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
        
