import requests
import threading
from seleniumwire import webdriver
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import unicodecsv as csv
import codecs
import json
# Tor proxy settings
proxy= {
    'http':'socks5h://127.0.0.1:9050',
    'https':'socks5h://127.0.0.1:9050',
}
tor_options = {
    'proxy': {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050',
        'connection_timeout': 10
    }
}


def get_coordinates(location):
    base_url = "https://nominatim.openstreetmap.org/search.php"
    params = {
        'q': location,
        'format': 'jsonv2',
        'polygon_geojson': 1
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            location_data = data[0]
            return location_data['lat'], location_data['lon']
    return None, None


# Testing Tor
def rotateIp():
    print("changing IP address in new Request ... \n\n") 
    headers = {'User-Agent': UserAgent().random}
    time.sleep(5)
    with Controller.from_port(port = 9051) as c:
        c.authenticate()
        c.signal(Signal.NEWNYM)




# Main scraping function
def scrape_location_data(location, keyword):
    rotateIp()
    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(
        options=firefox_options,seleniumwire_options=tor_options
    )
    try:
        lat, lon = get_coordinates(location)
        if lat and lon:
            driver.get(f"https://www.google.com/maps/search/{keyword}/@{lat},{lon},15z/")        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body[contains(@class, 'widget-scene-container')]")))
        except Exception:
            print("Timed out waiting for page to load completely")
        
        # try:
        #     WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"form:nth-child(2)"))).click()
        # except Exception as e:
        #     pass

        scrollable_div = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]') 
        print(scrollable_div)
        driver.execute_script("""
            let scrollableDiv = arguments[0];
            function scrollWithinElement(scrollableDiv){
                var totalHeight = 0;
                var distance = 1000;
                var scrollDelay = 3000;

                var timer = setInterval(()=>{
                    var scrolHeightBefore = scrollableDiv.scrollHeight;
                    scorlled = scrollableDiv.scrollBy(0, distance);
                    totalHeight += distance;
                    
                    if(totalHeight >= scrolHeightBefore){
                        totalHeight = 0;
                        setTimeout(()=>{
                            if(scrollableDiv.scrollHeight <= scrolHeightBefore){
                                clearInterval(timer);
                                resolve;
                            }
                        },scrollDelay);                                
                            }
                })
            }
            return scrollWithinElement(scrollableDiv);
        """, scrollable_div)


        time.sleep(5)
        results=[]
        items = driver.find_elements(By.CSS_SELECTOR,'div[role = feed] >div >div[jsaction]')
        for item in items:
            data ={}

            try:
                data['title'] = item.find_element(By.CLASS_NAME,'fontHeadlineSmall ').text
            except Exception:
                pass

            try:
                data['link'] = item.find_element(By.CSS_SELECTOR,' div[role = feed] >div >div[jsaction] > a ').get_attribute('href')
            except Exception:
                pass
            try:
                
                data['website'] = item.find_element(By.CSS_SELECTOR,' div[role = feed] >div >div[jsaction] div  div > a ').get_attribute('href')
            except Exception:
                pass
            
            try:
                rating = item.find_element(By.CSS_SELECTOR,'.fontBodyMedium > span[role="img"]').get_attribute('aria-label')
                data['Rating'] = rating.split(' ')[0]
                data['Opinions'] = rating.split(' ')[3]

            except Exception:
                data['Rating'] ='No Rating'
                data['Opinions'] ='No Rating'
        
            try:
                elemnt= item.find_element(By.CSS_SELECTOR,'.fontBodyMedium > div:nth-child(4)').text          
                metadata_list = elemnt.split('\n')
                data['State Now']='None'
                data['Time']='None'
                data['phone']= 'None'
                metadata_list_1 = metadata_list[0].split('·')
                metadata_list_2 = metadata_list[1].split('·')
                data['category']= metadata_list_1[0]
                data['address']= metadata_list_1[1]
                if(len(metadata_list_2) == 1):
                    if(any(i.isdigit() for i in metadata_list_2[0].split(' ')[0]) == False):
                        data['State Now'] = metadata_list_2[0]
                    else:
                        data['phone'] = metadata_list_2[0]
                else:
                    data['Time'] = metadata_list_2[0].split('⋅')[1]
                    data['State Now'] = metadata_list_2[0].split('⋅')[0]
                    data['phone']= metadata_list_2[1]       
            except Exception:
                pass
            if(data.get('title')): 
                results.append(data)
    finally:
            
        with open(f'output_{location.split(',')[0]}.json','a', encoding='utf-8') as file:
            json.dump(results,file,ensure_ascii=False,indent=3)
        driver.quit()

def main():
    with open('keywords.txt') as f:
        keywords = [line.strip() for line in f]

    with open('Locations.txt') as fLocal:
        locations = [line.strip() for line in fLocal]

    threads = []
    for location in locations:
        for keyword in keywords:
            t = threading.Thread(target=scrape_location_data, args=(location, keyword))
            threads.append(t)
            t.start()
    for t in threads:
        t.join()     
if __name__ == "__main__":
    main()