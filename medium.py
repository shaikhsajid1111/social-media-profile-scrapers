import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from fake_headers import Headers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
class Medium:
    @staticmethod   
    def init_driver(driver_path:str,browser_name:str):
        '''initiailize driver'''
        def set_properties(browser_option):
            '''set properties for the driver'''
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
        """scrap medium's profile"""
        try:
            URL = f"https://medium.com/@{username}"
           
            driver = Medium.init_driver('C:\\webdrivers\\chromedriver.exe',"Chrome") #replace with your webdriver's path and browser's name
            driver.get(URL)
            #wait until page loads so title contains "Medium"
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains('Medium'))
            #get source code of the page
            response = driver.page_source.encode('utf-8').strip()
             
            soup = BeautifulSoup(response,'html.parser')  
            
            profile_image = soup.find("meta" , {"property" : "og:image"})["content"]   #profile image from meta tag
            profile_username = soup.find("meta" , {"property" : "profile:username"})['content'] #profile username so, it can be used to create URL in following,follwers vars
            #if this finds full name then the account is premium
            full_name = soup.find('h1',{
                'class' :  'aw q do ci dp cj dq dr ds z'
                 
            })
            
            bio = soup.find('p',{
                'class' : 'ep eq ci b cj er es cm z'
            })
            is_paid_member = True
            #if full name was not fetched then account is free
            if full_name is None:
                full_name = soup.find('h1',{
                'class' : 'aw q dg ci dh cj di dj dk z'
            })      
                bio = soup.find('p',{
                'class' : 'eh ei ci b cj ej ek cm z'
            })
                is_paid_member = False  
                 
            followings = soup.find('a',{'href' : f"/@{profile_username}/following"}) 
            followers = soup.find('a',{'href' : f"/@{profile_username}/followers"})
            return {
                        "profile_image" : profile_image, 
                        'full_name' : full_name.text if full_name is not None else "No name found",
                        'is_paid_member' : is_paid_member,
                        'bio' : bio.text if bio is not None else "Bio Not Found!",
                        "followings" : followings.text if followings is not None else "Not found!",
                        "followers" : followers if followers is not None else "Not Found!"
                    }    
        except Exception as ex:
            print(ex)
        

if __name__ == '__main__':
    print(Medium.scrap(sys.argv[ len(sys.argv)-1] ))           

'''
last modified on : 3rd July,2020
'''