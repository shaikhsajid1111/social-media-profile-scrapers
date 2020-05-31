import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import json
from fake_headers import Headers    #__jsx-2164639479
import urllib3
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class Pinterest:
    def __init__(self,username = sys.argv[len(sys.argv)-1]):
        self.username = username
      
    def scrap(self):
        try:
            url = f'https://in.pinterest.com/{self.username}'
           
            ua = Headers(headers=False)       #fake user agent
            #automating and opening URL in headless browser
            chrome_option = Options()
            chrome_option.add_argument('--headless')
            chrome_option.add_argument('--disable-extensions')
            chrome_option.add_argument('--incognito')
            chrome_option.add_argument('--disable-gpu')
            chrome_option.add_argument('--log-level=3')
            chrome_option.add_argument(f'user-agent={ua}')
            driver = webdriver.Chrome('C:\\webdrivers\\chromedriver.exe',options=chrome_option) #chromedriver's path in first argument
            driver.get(url)
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "searchBoxContainer"))
                )
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

user = Pinterest()
print(user.scrap())            
