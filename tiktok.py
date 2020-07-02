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
import time
from fake_headers import Headers

class Tiktok:

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
            url = f'https://tiktok.com/@{username}'
            driver = Tiktok.init_driver('C:\\webdrivers\\chromedriver.exe',"Chrome")
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains(f"@{username}"))
            response = driver.page_source.encode('utf-8').strip()
            
            soup =  BeautifulSoup(response,'html.parser')
           
            script_tag = soup.find('script',{
                        'id' : '__NEXT_DATA__'
                    })
                
            json_data = json.loads(str(script_tag.text.strip()))
                
            #dict_keys(['props', 'page', 'query', 'buildId', 'assetPrefix', 'isFallback', 'customServer'])
            user_data = json_data['props']['pageProps']['userData']
            sec_id = user_data['secUid']
            user_id = user_data['userId']
            is_secret = user_data['isSecret']
            unique_name = user_data['uniqueId']
            signature = user_data['signature']
            covers = user_data['coversMedium']
            following = user_data['following']
            fans = user_data['fans']
            heart = user_data['heart']
            video = user_data['video']
            is_verified = user_data['verified']
            return {
                    'sec_id' : sec_id,
                    'user_id' : user_id,
                    'is_secret' : is_secret,
                    'username' : unique_name,
                    'bio' : signature,
                    'cover_image' : covers,
                    'following' : following,
                    'fans' : fans,
                    'hearts' : heart,
                    'video' : video,
                    'is_verified' : is_verified,
                }

        except Exception as ex:
            print(ex)        
if __name__ == "__main__":
    print(Tiktok.scrap(sys.argv[len(sys.argv)-1]))             

'''
author : sajid shaikh
updated : 1st July,2020
'''
    
    
   