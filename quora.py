import requests
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
class Quora:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username

    def scrap(self):
        try:
            URL = f'https://quora.com/profile/{self.username}'
            print(URL)
            #headers = {'user-agent' : 'Your User Agent'}
            chrome_option = Options()
            chrome_option.add_argument('--headless')
            chrome_option.add_argument('--disable-extensions')
            chrome_option.add_argument('--disable-gpu')
            driver = webdriver.Chrome('C:\\webdrivers\\chromedriver.exe',options=chrome_option) #chromedriver's path in first argument
            driver.get(URL)
            time.sleep(5)
            response = driver.page_source.encode('utf-8').strip()
            soup = BeautifulSoup(response,'html.parser')
            name = soup.find('div',{
                'class' : "q-text qu-bold"
            })
            profession = soup.find('div',{
                'class' : 'q-text qu-fontSize--large'
            })
            profile_image = soup.find('img',{
                'class' : 'q-image qu-display--block'
            })
            bio = soup.find('p',{
                'class' : 'q-text qu-display--block'
            })
            print(profession.text)
            print(name.text)
            print(profile_image['src'])
            print(bio)
            """ if response.status_code == 404:
                print("Failed to connect or user does not exist!")
                exit()
            if response.status_code == 200:   
                soup = BeautifulSoup(response.content,'html.parser')
                print(soup.prettify()) """
                
        except Exception as ex:
            print(ex)        
usr = Quora('Kashish-Arora-60')
print(usr.scrap())                