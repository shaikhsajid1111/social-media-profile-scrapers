try:
    import argparse
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from fake_headers import Headers
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)
class Medium:
    @staticmethod   
    def init_driver(browser_name):
        '''initiailize driver'''
        def set_properties(browser_option):
            '''set properties for the driver'''
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
                driver = webdriver.Chrome(ChromeDriverManager().install(),options=browser_option) #chromedriver's path in first argument
            elif browser_name == "Firefox":
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
        """scrap medium's profile"""
        try:
            URL = "https://medium.com/@{}".format(username)
            
           
            try:
                driver = Medium.init_driver(browser_name)  
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()
           
            #wait until page loads so title contains "Medium"
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains('Medium'))
            
            profile_image = driver.find_element_by_css_selector("img")  
            


            full_name = driver.title
            bio = driver.find_element_by_tag_name("p")
            followings = driver.find_element_by_xpath("//a[contains(@href, 'following')]")
            followers =  driver.find_element_by_xpath("//a[contains(@href, 'followers')]")
            
            image_class = driver.find_element_by_tag_name("img").get_attribute("class") 
            is_paid_member = True if image_class == "z cq ci ch" else False 
                        
            profile_data =  {
                        "profile_image" : profile_image.get_attribute("src"), 
                        'full_name' : full_name.split("-")[0],
                        "bio" : bio.text,
                        'is_paid_member' : is_paid_member,
                        "followings" : followings.text.split(" ")[0],
                        "followers" : followers.text.split(" ")[0] 
                    }    
            driver.close()
            driver.quit()
            return profile_data
        except Exception as ex:
            driver.close()
            driver.quit()
            return {"error" : ex}
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    parser.add_argument("--browser",help="What browser your PC have?")
    
    args = parser.parse_args()
    browser_name = args.browser if args.browser is not None else "chrome"
    print(Medium.scrap(args.username,browser_name))

#last modified on : 11th September,2020
