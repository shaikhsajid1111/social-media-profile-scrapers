try:
    import argparse
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from fake_headers import Headers
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import configparser
    from selenium.common.exceptions import NoSuchElementException
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)
    
config = configparser.ConfigParser()
config.read('settings.ini') 
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
            

            try:
                driver_path = config['DRIVER']['PATH']
            
                browser = config['DRIVER']['BROWSER']    
                driver = Github.init_driver(driver_path,browser)  
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()          
            
            #wait until page loads
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains(f"{username}"))
            
            full_name = driver.find_element_by_css_selector("span.p-name.vcard-fullname.d-block.overflow-hidden")
            try:
                bio = driver.find_element_by_css_selector("div.p-note.user-profile-bio.mb-3.js-user-profile-bio.f4")
            except NoSuchElementException:
                bio = ""
            try:
                location = driver.find_element_by_css_selector("span.p-label")
            except NoSuchElementException:
                location = ""
            try:
                email = driver.find_element_by_css_selector("li[itemprop='email']")
            except NoSuchElementException:
                email = ""
            
            try:
                contributions = driver.find_element_by_css_selector(".js-yearly-contributions")
            except NoSuchElementException:
                contributions = "" 
            profile_data =  {
                    'full_name' : full_name.text,
                    'bio' : bio.text if type(bio) is not str else "",
                    'location' : location.text if type(location) is not str else "",
                    "contributions" : contributions.text.split(" ")[0] if type(contributions) is not str else ""
                                   }
            driver.close()
            driver.quit()
            return profile_data
        except Exception as ex:
            driver.close()
            driver.quit()
            print(ex)   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    args = parser.parse_args()
    print(Github.scrap(args.username))


#last updated on 22nd August, 2020