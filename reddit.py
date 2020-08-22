try:
    import argparse
    import selenium
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from fake_headers import Headers
    import configparser
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)
        
config = configparser.ConfigParser()
config.read('settings.ini') 
class Reddit:
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
            URL = "https://reddit.com/user/{}".format(username)

            try:

                driver_path = config['DRIVER']['PATH']
    
                browser = config['DRIVER']['BROWSER']    
                driver = Reddit.init_driver(driver_path,browser)  
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()
            
            
            
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains("{}".format(username)))
            
            name = driver.find_element_by_tag_name("h4").text
            bio = driver.find_element_by_class_name("bVfceI5F_twrnRcVO1328").text.strip()
            try:
                banner = driver.find_element_by_class_name("_2ZyL7luKQghNeMnczY3gqW").get_attribute("style")
            except:
                banner = None
            
            profile = driver.find_element_by_css_selector("img._2TN8dEgAQbSyKntWpSPYM7").get_attribute("src")   
            
            karma = driver.find_element_by_id("profile--id-card--highlight-tooltip--karma")    
           
            cake_date = driver.find_element_by_id("profile--id-card--highlight-tooltip--cakeday")    
            
            return {
                    "name" : name,
                    "bio" : bio,
                    "banner" : banner.split('(')[-1].split(')')[0] if banner is not None else "",
                    "profile_image" : profile,
                    "karma" : karma.text,
                    "cake_date" : cake_date.text
                }
        except Exception as ex:
            driver.close()
            driver.quit()
            print(ex)        
    
       

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to scrap")
    args = parser.parse_args()
    print(Reddit.scrap(args.username))

#last updated - 21st August, 2020    
