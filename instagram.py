try:
    from bs4 import BeautifulSoup
    import argparse
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from fake_headers import Headers
    from settings import DRIVER_SETTINGS
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)
'''can scrap only public instagram accounts'''
class Instagram:
    @staticmethod   
    def init_driver(driver_path,browser_name):
        '''init the driver'''
        def set_properties(browser_option):
            '''sets the driver's properties'''
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
                driver = webdriver.Chrome(driver_path,options=browser_option) 
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
    def scrap(username):
        try:
            URL = 'https://instagram.com/{}'.format(username)
            
            if DRIVER_SETTINGS['PATH'] != "" and DRIVER_SETTINGS['BROWSER_NAME'] != "":
                driver_path = DRIVER_SETTINGS['PATH']      
                browser = DRIVER_SETTINGS['BROWSER_NAME']    
                driver = Instagram.init_driver(driver_path,browser)  
            else:
                print("Driver is not set!. Please edit settings file for driver configurations.")
                exit()
            
            ### ----------- edit above^ -------------------
            
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
            driver.close()
            driver.quit()
            return {
                'profile_image' : profile_image,
                'bio' : bio.text,
                'popularity' : popularity
                } 
        except Exception as ex:
            driver.close()
            driver.quit()
            print(ex)            

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    args = parser.parse_args()
    print(Instagram.scrap(args.username))



#last updated on 31st July, 2020