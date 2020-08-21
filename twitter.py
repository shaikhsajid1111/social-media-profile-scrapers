try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException
    import configparser
    import argparse
    from fake_headers import Headers
    import re
    
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex) 

config = configparser.ConfigParser()
config.read('settings.ini')   

class Twitter:

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
    def scrap(username):
        try:
            #generating URL according to the username
            URL = "https://twitter.com/{}".format(username)

            
            driver_path = config['DRIVER']['PATH']
            
            browser = config['DRIVER']['BROWSER']    
            driver = Twitter.init_driver(driver_path,browser)  
            try:
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()
            wait = WebDriverWait(driver, 30)
            element = wait.until(EC.title_contains("@"))
            
            full_name = driver.title.split("(")[0]
       
            try:
                banner_image = driver.find_element_by_css_selector("img.css-9pa8cd").get_attribute("src")
            except NoSuchElementException:
                banner_image = ""
            
    
            try:
                driver.find_element_by_css_selector("svg[aria-label='Verified account']")
                is_verified = True
            except NoSuchElementException:
                is_verified = False
            profile_image = "https://twitter.com/{}/photo".format(username.lower())
       
            follow_div = driver.find_element_by_css_selector("div.css-1dbjc4n.r-1mf7evn").text
            followers = driver.find_element_by_css_selector("a[href='/{}/followers']".format(username)).get_attribute("title")
            
            try:
                bio = driver.find_element_by_css_selector("div[data-testid='UserDescription']").text
            except NoSuchElementException:
                bio = ""
        
            
            try:
                details = driver.find_element_by_css_selector("[data-testid='UserProfileHeader_Items']")
                all_spans = details.find_elements_by_tag_name("span")
                joined_date = ""
                
                
                birth_date = ""
                for item in all_spans:
                    if "born" in item.text.lower():
                        birth_date = item.text
                    elif "join" in item.text.lower():
                        joined_date = item.text
                  
            except Exception as ex:
                print(ex)
            try:
                website = details.find_element_by_tag_name("a").text
            except NoSuchElementException:
                website = ""
            location = details.text.replace(joined_date,"").replace(website,"") 
            
            driver.close()
            driver.quit() 
            return{
                'full_name' : full_name,
                'banner' : banner_image,
                'profile_image_link' : profile_image,
                 "account_verified" : is_verified,
                 "birth_date" : birth_date,
                 "location" : location,
                 "website" : website,
                 "bio" : bio,
                 "followers" : followers,
                 "following" : follow_div.split(" ")[0],
                 "joined_date" : joined_date

            }
              
        except Exception as ex:
            return {"error" : ex}
            driver.close()
            driver.quit()
               


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    args = parser.parse_args()
    print(Twitter.scrap(args.username))

#last updated - 21st August,2020
    
    
