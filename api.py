import time
from datetime import datetime
from src.gmail_processor import get_unread_mails
from src.common import validate_launch_time, RecordClass, make_a_yelper_record
import traceback

start_time, end_time = validate_launch_time()
current_date = str(datetime.now().date())

yelpers_records = RecordClass()
yelpers_records.date = current_date

#logs = {current_date: {}}

if __name__ == '__main__':
    auth = False
    old_counter = -1
    while True:
        if datetime.now().hour >= start_time or datetime.now().hour <= end_time:
            try:
                scraped_profiles = get_unread_mails()
                if scraped_profiles:
                    for profile in scraped_profiles:
                        fresh_date = str(datetime.now().date())
                        if current_date != fresh_date:
                            current_date = fresh_date
                            yelpers_records.date = current_date
                        yelpers_records.assign_fields(profile)    
                        make_a_yelper_record(yelpers_records)                    
            except Exception as e:
                print(e)                   
                traceback.print_exc()
                pass    
        time.sleep(20)