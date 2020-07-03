import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
from bs4 import BeautifulSoup
import json
from fake_headers import Headers    
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Pinterest:
    '''This class scraps pinterest and returns a dict containing all user data'''
    @staticmethod   
    def init_driver(driver_path:str,browser_name:str):
        """Initialize webdriver"""
        def set_properties(browser_option):
            """Set Properties of webdriver"""
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
            URL = f'https://in.pinterest.com/{username}'
           
            driver = Pinterest.init_driver('C:\\webdrivers\\chromedriver.exe',"Chrome")  #chromedriver's path in first argument
            
            driver.get(URL)

            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains("Pinterest"))
            response = driver.page_source.encode('utf-8').strip()  
            
            
            soup = BeautifulSoup(response,'html.parser')    
            
            script_tag = soup.find('script',{
                'id' : 'initial-state'
            })
            
            json_data = json.loads(str(script_tag.text.strip()))
            
            data = json_data['resourceResponses'][0]['response']['data']
            user_data = data['user']
            
            is_verified_merchant = user_data['is_verified_merchant']
            full_name = user_data['full_name']
            impressum_url = user_data['impressum_url']
            pin_count = user_data['pin_count']
            domain_url = user_data['domain_url']
            profile_image = user_data['image_xlarge_url']
            bio = user_data['about']
            board_count = user_data['board_count']
            is_indexed = user_data['indexed']
            follower = user_data['follower_count']
            following = user_data['following_count']
            country = user_data['country']
            location = user_data['location']
            
            return{
                'full_name' : full_name,
                'profile_image' : profile_image,
                'followers' : follower,
                'followings' : following,
                'bio' : bio,
                'country' : country,
                'impressum_url' : impressum_url,
                'website' : domain_url,
                'board_count' : board_count,
                'location' : location,
                'pin_count' : pin_count,
                'is_verified' : is_verified_merchant,

            }
        except Exception as ex:
            print(ex)    


if __name__ == '__main__':
    print(Pinterest.scrap(sys.argv[len(sys.argv)-1]))

'''
author : sajid shaikh
updated : 3rd July,2020

'''