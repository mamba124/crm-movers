import time
from datetime import datetime
from src.gmail_processor import get_unread_mails
from src.common import validate_launch_time
import traceback

start_time, end_time = validate_launch_time()
current_date = str(datetime.now().date())

#logs = {current_date: {}}

if __name__ == '__main__':
    auth = False
    old_counter = -1
    while True:
        if datetime.now().hour >= start_time or datetime.now().hour <= end_time:
            try:
                get_unread_mails()
            except Exception as e:
                print(e)                   
                traceback.print_exc()
                pass    
        time.sleep(20)