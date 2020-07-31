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
except Exception as ex:
    print(ex)
    
class Github:
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
            URL = 'https://github.com/{}'.format(username)
            

            if DRIVER_SETTINGS['PATH'] != "" and DRIVER_SETTINGS['BROWSER_NAME'] != "":
                driver_path = DRIVER_SETTINGS['PATH']      
                browser = DRIVER_SETTINGS['BROWSER_NAME']    
                driver = Github.init_driver(driver_path,browser)  
            else:
                print("Driver is not set!. Please edit settings file for driver configurations.")
                exit()  
           
            
            driver.get(URL)            
            #wait until page loads
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains(f"{username}"))
            #get source code of the website
            response = driver.page_source.encode('utf-8').strip()
            
            soup =  BeautifulSoup(response,'html.parser')
            #finding all elements in source code
            full_name = soup.find("span",{
                'class' : 'p-name vcard-fullname d-block overflow-hidden'
            })
            bio = soup.find('div',{
                'class' : 'p-note user-profile-bio mb-3 js-user-profile-bio f4'
            })
            
            location = soup.find('span',{
                'class' : 'p-label'
            })
            status = soup.find('div',{
                'class' : 'ws-normal user-status-message-wrapper f6 min-width-0'
            })
            
            email = soup.find('a',{
                'itemprop' : 'u-email link-gray-dark '
            })
            contributions = soup.find_all("h2",{
                "class" : 'f4 text-normal mb-2'
            })[0]
            driver.close()
            driver.quit()
            return {
                    'full_name' : full_name.text if full_name is not None else "Not Found" ,
                    'bio' : bio.text if bio is not None else "Bio Not Found!",
                    'location' : location.text if location is not None else "Location Not found!",
                    'status':  status.text if status is not None else "No status given",
                    "contributions" : contributions.text.strip().replace("\n","")
                                   }
        except Exception as ex:
            driver.close()
            driver.quit()
            print(ex)   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    args = parser.parse_args()
    print(Github.scrap(args.username))


#last updated on 31st July, 2020