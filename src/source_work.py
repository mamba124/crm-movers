import time
import json
from datetime import datetime 
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NEXT_BUTTON = "#modal-portal-container > div:nth-child(2) > div > div > div > div > div.border-color--default__09f24__JbNoB > div > div > div.padding-t4__09f24__Y6aGL.padding-r4__09f24__PQlH_.padding-b4__09f24__q6U6q.padding-l4__09f24__XrHdl.border-color--default__09f24__NPAKY.text-align--left__09f24__ju_Ri > div > div:nth-child(2) > div > button" 
RADIO_BUTTON = "#how_do_you_want_to_get_more_information--3"
NAME_SELECTOR = "body > yelp-react-root > div:nth-child(1) > div.messenger-container__09f24__qt8O4 > div > div.messenger_right__09f24__fndbc.border--left__09f24__Lt8WF.border-color--default__09f24__JbNoB > div > div > div.u-flex__09f24__rt07y.u-flex-column__09f24__m6LIn.u-flex-item__09f24__YuSEF.border-color--default__09f24__JbNoB > div.messenger_right_top__09f24__ZxW58.u-padding-t3.u-padding-b3.border--bottom__09f24__Yl28T.border-color--default__09f24__JbNoB > div > div > div > div.arrange-unit__09f24__rqHTg.arrange-unit-fill__09f24__CUubG.border-color--default__09f24__NPAKY > div.user-passport-info.border-color--default__09f24__NPAKY > span > a"
OPTION_BUTTON = "div.margin-r3__09f24__ppHm0:nth-child(2) > button"
#SEND_BUTTON = "#modal-portal-container > div:nth-child(2) > div > div > div > div > div.border-color--default__09f24__JbNoB > div > div > div.padding-t4__09f24__Y6aGL.padding-r4__09f24__PQlH_.padding-b4__09f24__q6U6q.padding-l4__09f24__XrHdl.border-color--default__09f24__NPAKY.text-align--left__09f24__ju_Ri > div > div:nth-child(3) > button"
SEND_BUTTON = "div.margin-r3__09f24__ppHm0:nth-child(2) > button:nth-child(1)"
ANSWER_BUTTON = ".button--wide__09f24__dKiSe"
with open("secret_files/user_info.json", "r") as f:
    credentials = json.load(f)


def wait(driver, time, element):
    WebDriverWait(driver, time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, element)))


def login(driver, link):
    wait(driver, 3, ".css-lf8rwb")
    dog_check(driver)
    email_element = driver.find_elements("name", "email")
    pass_element = driver.find_elements("name", "password")
    if email_element and pass_element:
        email_element[0].send_keys(credentials["username"])
        pass_element[0].send_keys(credentials["password"])
        driver.find_elements("tag name", "button")[0].click()
        print(f"Authenticated at time {datetime.now().time()}")
        element = "#logo > a"
        wait(driver, 5, element)
        time.sleep(2)
        return True


def get_opportunity(driver):
    dog_check(driver)
    time.sleep(0.1)
    success = False
    t1 = datetime.now().time()
    t2 = None
    print(f"Accessed at {datetime.now().time()}")
    try:
        driver.find_element("css selector", SEND_BUTTON).click()        
        name = driver.find_elements("css selector", NAME_SELECTOR)
        navigate_through_button_menu(driver)            
    
        message_text = build_message(name)
        message = driver.find_element("name", "introduce_yourself_send_message")
        message.send_keys(message_text)       
        
        driver.find_element("css selector", ANSWER_BUTTON).click()
        t2 = datetime.now().time()
        logging.info(f"Answered at {datetime.now().time()}")
        print(f"Answered at {datetime.now().time()}")
        success = True
    except Exception as ex:
        print(ex)
        quote_time = driver.find_elements("css selector", "body > yelp-react-root > div > div.messenger-container__09f24__qt8O4 > div > div.messenger_right__09f24__fndbc.border--left__09f24__Lt8WF.border-color--default__09f24__JbNoB > div > div > div.u-flex__09f24__rt07y.u-flex-column__09f24__m6LIn.u-flex-item__09f24__YuSEF.border-color--default__09f24__JbNoB > div.project-description-container__09f24__zySxi.u-flex-item__09f24__YuSEF.messenger-right.border-color--default__09f24__JbNoB > div > div > div.messages-grouped-by-time-view_group_time-sent__09f24__lCCiu.border-color--default__09f24__NPAKY > p")
        if quote_time:
            quote_time_string = f"Quote appeared at the time {quote_time[0].text}"
            t2 = quote_time[0].text
        else:
            quote_time_string = ""
        logging.info(f"Opportunity has expired, no dialogue window found.{quote_time_string}")
        print(f"Opportunity has expired, no dialogue window found.{quote_time_string}")
    return success, t1, t2, name


def navigate_through_button_menu(driver):
    time.sleep(0.2)
    driver.find_element("css selector", RADIO_BUTTON).click()
    time.sleep(0.2)


def build_message(name):
    if name:
        message_text = f"Hi, {name[0].text}! Thank you for contacting California Express Movers."
    else:
        message_text = "Hi! Thank you for contacting California Express Movers."
    return message_text


def dog_check(driver):
    try:
        wait(driver, 8, element="#logo > a")
    finally:    
        html = driver.find_elements("css selector", "html")[0].get_attribute("outerHTML")
        if "HTTP 504 - GATEWAY TIMEOUT" in html:
            driver.refresh()
            print("HTTP 504 - GATEWAY TIMEOUT, refreshing..")
            logging.info("HTTP 504 - GATEWAY TIMEOUT, refreshing..")