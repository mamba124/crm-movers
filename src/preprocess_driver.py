import random
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType

#CROSS_SELECTOR = ".dismiss-link__09f24__Q1RVn"
#NOTIFICATION_SELECTOR = ".close-button__09f24__qgCyrs"

def generate_proxy():
    profile = webdriver.FirefoxProfile()
    options = Options()
    options.headless = True
    options.add_argument("start-maximized")

    driver = webdriver.Firefox(profile, options=options)
    driver.get("https://sslproxies.org/")
    driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//table[@class='table table-striped table-bordered']//th[contains(., 'IP Address')]"))))

    ips = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered']//tbody//tr/td[position() = 1]")))]
    ports = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered']//tbody//tr/td[position() = 2]")))]
    
    driver.quit()
    proxies = []
    for i in range(0, len(ips)):
        proxies.append(ips[i]+':'+ports[i])
    pos = random.randint(0, len(proxies))
    try:
        print("Proxy selected: {}".format(proxies[pos]))
        my_proxy = proxies[pos]
    except Exception as e:
        print(e)
        driver.quit()
        my_proxy = None
    return my_proxy


def initialize_driver():
    for attempt in range(5):
        sleep_time = 1.8 ** attempt
        my_proxy = generate_proxy()
        if my_proxy:
            break
        else:
            time.sleep(sleep_time)
    if attempt == 4:
        raise Exception("all attempts exceeded, couldn't get proxy")
    options = Options()
    #options.headless = True
    proxy = Proxy({
         'proxyType': ProxyType.MANUAL,
         'httpProxy': my_proxy,
         'ftpProxy': my_proxy,
         'sslProxy': my_proxy,
         'noProxy': '' # set this value as desired
    })

    driver = webdriver.Firefox(proxy=proxy, options=options)    
    driver.maximize_window()
    return driver


"""

def initialize_driver():
    profile = webdriver.FirefoxProfile()
    options = Options()
  #  options.headless = True
    options.add_argument("start-maximized")
#    options.add_experimental_option("excludeSwitches", ["enable-automation"])
  #  options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Firefox(profile, options=options)
    driver.get("https://sslproxies.org/")
    driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//table[@class='table table-striped table-bordered']//th[contains(., 'IP Address')]"))))
    ips = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered']//tbody//tr/td[position() = 1]")))]
    ports = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered']//tbody//tr/td[position() = 2]")))]
    driver.quit()
    proxies = []
    for i in range(0, len(ips)):
        proxies.append(ips[i]+':'+ports[i])
   # print(proxies)
    pos = random.randint(0, len(proxies))
 #   for i in range(0, len(proxies)):
    try:
        print("Proxy selected: {}".format(proxies[pos]))
        my_proxy = proxies[pos]
      
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': my_proxy,
            'ftpProxy': my_proxy,
            'sslProxy': my_proxy,
            'noProxy': '' # set this value as desired
            })            
#      options = Options()
#      options.add_argument('--proxy-server={}'.format(proxies[i]))
        driver = webdriver.Firefox(proxy=proxy)
     #   break
 #     driver.get("https://www.whatismyip.com/proxy-check/?iref=home")
 #     if "Proxy Type" in WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.card-text"))):
 #         break
    except Exception as e:
        print(e)
        driver.quit()
    print("Proxy Invoked")
  #  options.headless = True
   # ua = UserAgent()
 #   user_agent = ua.random
   # profile.set_preference("general.useragent.override", ua.random)    
   # profile.set_preference('permissions.default.stylesheet', 2)
   # profile.set_preference('permissions.default.image', 2)
  #  profile.set_preference('network.proxy.type', 1)
   # profile.set_preference('network.proxy.socks', '127.0.0.1')
   # profile.set_preference('network.proxy.socks_port', 9150)
 #   driver = webdriver.Firefox(profile, options=options)
    
    driver.maximize_window()
    return driver
"""