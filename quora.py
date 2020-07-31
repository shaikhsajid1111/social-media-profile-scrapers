try:
    import argparse
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from fake_headers import Headers
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from settings import DRIVER_SETTINGS
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
class Quora:
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
            browser_option.add_argument('--disable-notifications')
            browser_option.add_argument('--disable-popup-blocking')
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
                driver = webdriver.Firefox(executable_path=driver_path,options=browser_option)
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)
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
            URL = 'https://quora.com/profile/{}'.format(username)
            if DRIVER_SETTINGS['PATH'] != "" and DRIVER_SETTINGS['BROWSER_NAME'] != "":
                driver_path = DRIVER_SETTINGS['PATH']      
                browser = DRIVER_SETTINGS['BROWSER_NAME']    
                driver = Quora.init_driver(driver_path,browser)  
            else:
                print("Driver is not set!. Please edit settings file for driver configurations.")
                exit()
            
            driver.get(URL)

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
            driver.close()
            driver.quit()
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
            driver.close()
            driver.quit()
            print(ex)        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    args = parser.parse_args()
    print(Quora.scrap(args.username))

#last updated - 31st July, 2020