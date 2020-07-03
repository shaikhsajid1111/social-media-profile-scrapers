from bs4 import BeautifulSoup
import sys
import json
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from fake_headers import Headers
class Facebook:

    @staticmethod   
    def init_driver(driver_path:str,browser_name:str):
        def set_properties(browser_option):
            ua = Headers().generate()      #fake user agent
            browser_option.add_argument('--headless')
            browser_option.add_argument('--disable-extensions')
            browser_option.add_argument('--incognito')
            browser_option.add_argument('--disable-gpu')
            browser_option.add_argument('--log-level=3')
            browser_option.add_argument(f'user-agent={ua}')
            return browser_option
        try:
            browser_name = browser_name.strip().title()

            ua = Headers().generate()      #fake user agent
            #automating and opening URL in headless browser
            if browser_name == "Chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)    
                driver = webdriver.Chrome(driver_path,options=browser_option) #chromedriver's path in first argument
            elif browser_name == "Firefox":
                browser_option = FirefoxOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Firefox(driver_path,options=browser_option)
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)

    @staticmethod
    def scrap(username):
        try:
            URL = f"https://facebook.com/{username}"
            driver = Facebook.init_driver('C:\\webdrivers\\chromedriver.exe',"Chrome")
            driver.get(URL)
            
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.ID, "fb-timeline-cover-name")))
            response = driver.page_source.encode('utf-8').strip()
            
            
            soup = BeautifulSoup(response,"html.parser")
            
            facebook_name = soup.find("span",{
                "id":"fb-timeline-cover-name"
            })
            profile_image = soup.find("img",{
                "class" : "_11kf img"
            })
            current_city = soup.find("li",{
                "id" : "current_city"
            })
            clg = soup.find("div",{
                "class" : "_2lzr _50f5 _50f7"
            })
            
            return {
                    "profile_image" : profile_image['src'] if profile_image is not None else "Not Found!",
                    "current_city" : current_city.text.strip() if current_city is not None else "Not Found!",
                    "Education" : clg.text.strip() if clg is not None else "Not Found!"
                }
        except Exception as ex:
             print(ex)       


if __name__ == '__main__':
    print(Facebook.scrap(sys.argv[len(sys.argv)-1]))