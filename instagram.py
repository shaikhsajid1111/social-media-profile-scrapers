import requests
from bs4 import BeautifulSoup
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from fake_headers import Headers
'''can scrap only public instagram accounts'''
class Instagram:
    @staticmethod
    def scrap(username):
        try:
            URL = f'https://instagram.com/{username}'
            headers = Headers(headers=True).generate()
            
            chrome_option = Options()
            chrome_option.add_argument('--headless')
            chrome_option.add_argument('--disable-extensions')
            chrome_option.add_argument('--disable-gpu')
            chrome_option.add_argument('--log-level=3')
            chrome_option.add_argument(f'user-agent={headers}')
            driver = webdriver.Chrome('C:\\webdrivers\\chromedriver.exe',options=chrome_option) #chromedriver's path in first argument
            
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
