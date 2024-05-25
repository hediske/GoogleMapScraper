import requests
from seleniumwire import webdriver
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
# Tor proxy settings
proxy= {
    'http':'socks5h://127.0.0.1:9050',
    'https':'socks5h://127.0.0.1:9050',
}

def tor_request(url, proxy,headers):
    try:
        response = requests.get(url, proxies=proxy, headers=headers)
        print("Response from Tor circuit:", response.text)
    except Exception as e:
        print("An error occurred:", str(e))

# Test URL
url = "https://ipinfo.io/json"


# Testing Tor
# print("changing IP address in every seconds ... \n\n") 
# while True:
#     headers = {'User-Agent': UserAgent().random}
#     time.sleep(5)
#     with Controller.from_port(port = 9051) as c:
#         c.authenticate()
#         c.signal(Signal.NEWNYM)
#         tor_request(url, proxy,headers)


#Main Function
firefow_options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(
    options=firefow_options
)
keyword = "Software"
driver.get(f"https://www.google.com/maps/search/{keyword}/")
try:
    WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"form:nth-child(2)"))).click()
except Exception as e:
    pass

time.sleep(5)
driver.refresh()
scrollable_div = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]') 
driver.execute_script("""
    let scrollableDiv = arguments[0];
    function scrollWithinElement(scrollableDiv){
        var totalHeight = 0;
        var distane = 1000;
                      
    }
                      """, scrollable_div)

        
