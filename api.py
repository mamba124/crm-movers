import time
import logging
import os
from datetime import datetime
from src.source_work import login, get_opportunity, wait
from src.preprocess_driver import initialize_driver
from src.gmail_processor import get_unread_mails, create_message, send_message, build_service
from src.common import validate_launch_time, make_a_record, RecordClass, make_a_yelper_record
import traceback

start_time, end_time = validate_launch_time()
current_date = str(datetime.now().date())

yelpers_records = RecordClass()
yelpers_records.date = current_date

#logs = {current_date: {}}

if __name__ == '__main__':
    auth = False
    driver = initialize_driver()
    old_counter = -1
    while True:
        if datetime.now().hour >= start_time or datetime.now().hour <= end_time:
            try:
                scraped_links, scraped_profiles = get_unread_mails()
                if scraped_links:
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