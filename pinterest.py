import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import json
from fake_headers import Headers    #__jsx-2164639479
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Pinterest:
    '''This class scraps pinterest and returns a dict containing all user data'''
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
    @staticmethod
    def scrap(username):
        try:
            url = f'https://in.pinterest.com/{username}'
           
            ua = Headers(headers=False).generate()       #fake user agent
            #automating and opening URL in headless browser
            chrome_option = Options()
            chrome_option.add_argument('--headless')
            chrome_option.add_argument('--disable-extensions')
            chrome_option.add_argument('--incognito')
            chrome_option.add_argument('--disable-gpu')
            chrome_option.add_argument('--log-level=3')
            chrome_option.add_argument(f'user-agent={ua}')
            chrome_option.add_argument('--ignore-certificate-errors')
            chrome_option.add_argument('--ignore-ssl-errors')
            driver = webdriver.Chrome('C:\\webdrivers\\chromedriver.exe',options=chrome_option) #chromedriver's path in first argument
            driver.get(url)

            time.sleep(10)
            #wait = WebDriverWait(driver, 10)
            #element = wait.until(EC.title_contains('P'))
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
updated : 16-06-2020

'''