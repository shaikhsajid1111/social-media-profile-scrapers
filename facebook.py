try:
    from bs4 import BeautifulSoup
    import json
    import selenium
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from fake_headers import Headers
    import argparse
    from settings import DRIVER_SETTINGS
except ModuleNotFoundError:
    print("Please download dependecies from requirement.txt")
except Exception as ex:
    print(ex)    

class Facebook:
    @staticmethod   
    def init_driver(driver_path,browser_name):
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

            ua = Headers().generate()      #fake user agent
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
    def scrap(username):
        try:
            URL = "https://facebook.com/{}".format(username)
            
            if DRIVER_SETTINGS['PATH'] != "" and DRIVER_SETTINGS['BROWSER_NAME'] != "":
                driver_path = DRIVER_SETTINGS['PATH']      
                browser = DRIVER_SETTINGS['BROWSER_NAME']    
                driver = Facebook.init_driver(driver_path,browser)  
            else:
                print("Driver is not set!. Please edit settings file for driver configurations.")
                exit()
            
            driver.get(URL)
            #wait until element is present with ID fb-timeline-cover-name
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.ID, "fb-timeline-cover-name")))
            #get source code of the page
            response = driver.page_source.encode('utf-8').strip()
            
            
            soup = BeautifulSoup(response,"html.parser")
            
            facebook_name = soup.find("span",{
                "id":"fb-timeline-cover-name"
            })
            profile_image = soup.find("img",{
                "class" : "_11kf img"
            })
            current_city = soup.find("li",{
                "id" : "current_city"
            })
            clg = soup.find("div",{
                "class" : "_2lzr _50f5 _50f7"
            })
            driver.close()
            driver.quit()
            return {
                    "profile_image" : profile_image['src'] if profile_image is not None else "Not Found!",
                    "current_city" : current_city.text.strip() if current_city is not None else "Not Found!",
                    "Education" : clg.text.strip() if clg is not None else "Not Found!"
                }
        except Exception as ex:
             driver.close()
             driver.quit()
             print(ex)       


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    args = parser.parse_args()
    print(Facebook.scrap(args.username))

#last updated on 31st July, 2020