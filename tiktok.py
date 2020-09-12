try:
    import argparse
    import json
    import selenium
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from fake_headers import Headers
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)
 
class Tiktok:
    @staticmethod   
    def init_driver(browser_name:str):
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
        
            if browser_name.lower() == "chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)    
                driver = webdriver.Chrome(ChromeDriverManager().install(),options=browser_option) #chromedriver's path in first argument
            elif browser_name.lower() == "firefox":
                browser_option = FirefoxOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=browser_option)
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)
        
    @staticmethod
    def scrap(username,browser_name):
        try:
            URL = 'https://tiktok.com/@{}'.format(username)
            
            try: 
                driver = Tiktok.init_driver(browser_name)  
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()
            
            
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains("@{}".format(username)))
           
           
            script_tag = driver.find_element_by_id("__NEXT_DATA__").get_attribute("innerHTML")
            json_data = json.loads(script_tag)
                
            #dict_keys(['props', 'page', 'query', 'buildId', 'assetPrefix', 'isFallback', 'customServer'])
            user_data = json_data['props']['pageProps']['userData']
            sec_id = user_data['secUid']
            user_id = user_data['userId']
            is_secret = user_data['isSecret']
            unique_name = user_data['uniqueId']
            signature = user_data['signature']
            covers = user_data['coversMedium']
            following = user_data['following']
            fans = user_data['fans']
            heart = user_data['heart']
            video = user_data['video']
            is_verified = user_data['verified']
            
            profile_data =  {
                    'sec_id' : sec_id,
                    'user_id' : user_id,
                    'is_secret' : is_secret,
                    'username' : unique_name,
                    'bio' : signature,
                    'cover_image' : covers,
                    'following' : following,
                    'fans' : fans,
                    'hearts' : heart,
                    'video' : video,
                    'is_verified' : is_verified,
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
    parser.add_argument("--browser",help="What browser your PC have?")
    
    args = parser.parse_args()
    browser_name = args.browser if args.browser is not None else "chrome"
    print(Tiktok.scrap(args.username,browser_name))

    
    
   #last updated - 11th September, 2020