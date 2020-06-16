import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from fake_headers import Headers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class Quora:
    @staticmethod
    def is_none(val):
        if val is None:
            val = 'Not Found!'
            return val
        else:
            return val
    @staticmethod        
    def scrap(username):
        try:
            URL = f'https://quora.com/profile/{username}'
            
            headers = Headers().generate()
            chrome_option = Options()               #chrome options for driver
            chrome_option.add_argument('--headless')        #don't open browser window
            chrome_option.add_argument('--disable-extensions')  #disable all browser extension
            chrome_option.add_argument('--disable-gpu')
            chrome_option.add_argument(f'user-agent={headers}')
            chrome_option.add_argument('--ignore-certificate-errors')
            chrome_option.add_argument('--ignore-ssl-errors')
            chrome_option.add_argument('--log-level=3')
            driver = webdriver.Chrome('C:\\webdrivers\\chromedriver.exe',options=chrome_option) #chromedriver's path in first argument
            driver.get(URL)

            #time.sleep(5)
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains('Quora'))
            response = driver.page_source.encode('utf-8').strip()
             
            soup = BeautifulSoup(response,'html.parser')
       
            name = soup.find('div',{
                'class' : "q-text qu-bold"
            })
            name = Quora.is_none(name)
            
            profession = soup.find('div',{
                'class' : 'q-text qu-fontSize--large'
            })
            profession = Quora.is_none(profession)
            
            profile_image = soup.find('img',{
                'class' : 'q-image qu-display--block'
            })
            profile_image = Quora.is_none(profile_image)

            bio = soup.find('p',{
                'class' : 'q-text qu-display--block'
            })
            bio = Quora.is_none(bio)

            answers_count = soup.find('div',{
                'class' : 'q-text qu-medium qu-fontSize--small qu-color--red'
            })

            detail_count = soup.find_all('div',{
                'class' : 'q-text qu-medium qu-fontSize--small qu-color--gray_light'
            })
            if detail_count is not None:
                questions = detail_count[0]
                shares = detail_count[1]
                posts = detail_count[2]
                followers = detail_count[3]
                followings = detail_count[4]
            else:
                questions,shares,posts,followers,followings = ''    
            more = soup.find_all('div',{
                'class' : 'q-text qu-truncateLines--2'
            })
            
            return {
                'name'  :name.text,
                'profession' : profession.text.strip(),
                'profile_image' : profile_image['src'] if type(profile_image) is not str else profile_image,
                'bio' : bio if type(bio) is str else bio.text,
                'answers_count' : answers_count.text.strip(),
                'questions_count' : questions.text.strip(),
                'shares' : shares.text.strip(),
                'posts' : posts.text.strip(),
                'followers' : followers.text.strip(),
                'following' : followings.text.strip(),
                'more_details' : [more[i].text.replace('\n','').replace('\r','') for i in range(len(more))]
            }
        except Exception as ex:
            print(ex)        


if __name__ == '__main__':
    print(Quora.scrap(sys.argv[len(sys.argv)-1]))

'''
author : Sajid shaikh
updated : 16-06-2020
'''