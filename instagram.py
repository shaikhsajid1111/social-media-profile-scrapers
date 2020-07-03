import requests
from bs4 import BeautifulSoup
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from fake_headers import Headers
'''can scrap only public instagram accounts'''
class Instagram:
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
            URL = f'https://instagram.com/{username}'
            driver = Instagram.init_driver('C:\\webdrivers\\chromedriver.exe',"Chrome") #replace with your webdriver's path and browser's name
            driver.get(URL)
            
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains('Instagram'))
            response = driver.page_source.encode('utf-8').strip()
             
            soup = BeautifulSoup(response,'html.parser')
            profile_image = soup.find('img',{
                'class' : '_6q-tv'
            })['src']
            bio =soup.find('div',{
                'class' : '-vDIg'
            })        
            more = soup.find('meta',property='og:description')
        
            popularity = more['content'].split('-')[0]
            return {
                'profile_image' : profile_image,
                'bio' : bio.text,
                'popularity' : popularity
                } 
        except Exception as ex:
            print(ex)            

if __name__ == "__main__":
    print(Instagram.scrap(sys.argv[len(sys.argv)-1]))
'''
author : Sajid Shaikh
Updated : 2nd July, 2020
'''