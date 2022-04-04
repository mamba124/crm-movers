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
records = RecordClass()
records.date = current_date

yelpers_records = RecordClass()
records.date = current_date

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
                    for link, profile in zip(scraped_links, scraped_profiles):
                        if link:
                            fresh_date = str(datetime.now().date())
                            if current_date != fresh_date:
                                current_date = fresh_date
                                records.date = current_date
                                yelpers_records.date = current_date
                            if not auth:
                                driver.get(link)
                                counter = 0
                            else:
                                driver.execute_script(f'''window.open("{link}","_blank");''')
                                counter += 1
                            records.processed = str(datetime.now().time())
                            records.link = link
    
    
                            print(f"process link {link} at time {datetime.now().time()}")
                            while not auth:
                                auth = login(driver, link)
                        if profile:
                            yelpers_records.success = True
                            yelpers_records.date = current_date
                            
                            yelpers_records.assign_direct_fields(profile)                        
                            make_a_yelper_record(yelpers_records)  
                    for index, handler in enumerate(driver.window_handles):
                        if index > old_counter:
                            driver.switch_to.window(handler)
                            try:
                                css = ".heading--h2__09f24__WbmpW"
                                wait(driver, 8, css)
                            except:
                                try:
                                    css = "body > yelp-react-root > div:nth-child(1) > div.messenger-container__09f24__qt8O4 > div > div.messenger_left__09f24__qGRD1.border-color--default__09f24__JbNoB > div.messenger_left_middle__09f24__uFP6q.border-color--default__09f24__JbNoB > div > div.padding-t2__09f24__Y6duA.padding-r3__09f24__eaF7p.padding-b2__09f24__F0z5y.padding-l3__09f24__IOjKY.border--top__09f24__exYYb.border-color--default__09f24__NPAKY > div > div > h4"
                                    wait(driver, 2, css)
                                except:
                                    continue
                            success, t1, t2, name = get_opportunity(driver)
                            print(f"Successful? {success}") # TODO when I open a tab I must distinguish tabs and their success
                            records.success = success
                            records.name = name
                            yelpers_records.success = success
                            records.accessed = str(t1)
                            records.answered = str(t2)
                            make_a_record(index, records)
                            make_a_yelper_record(yelpers_records)
                            print(f"Accessed at {t1}")
                            print(f"Answered at {t2}")
                            now = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")                      
                            if index >= 17:
                                raise Exception("Too many tabs")
                    old_counter = index
                        
            except Exception as e:
                print(e)
                if "Message: Failed to decode response from marionette" in str(e):
                    user="californiaexperessmail@gmail.com"
                    mail = create_message(to=user, message_text="Attention, something terrible happened with WebDriver! Please, restart bot manually")
                    service = build_service()
                    send_message(service, mail, user="californiaexperessmail@gmail.com")
                    raise Exception("No marionette for some reasons")
                if "Too many tabs" in str(e):
                    user="californiaexperessmail@gmail.com"
                    mail = create_message(to=user, message_text="Attention, Too many tabs on WebDriver. Bot restarts automatically..")
                    service = build_service()
                    send_message(service, mail, user="californiaexperessmail@gmail.com")
                    raise Exception("Too many tabs")                    
                traceback.print_exc()
                if "cookies.pickle" in os.listdir():
                    os.remove("cookies.pickle")
                pass
            
        time.sleep(10)