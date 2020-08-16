try:
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
            
            driver.get(URL)
            
            wait = WebDriverWait(driver, 10)
            wait.until(EC.title_contains('@'))
            
            
            data = driver.execute_script('return window._sharedData')['entry_data']

            is_private = data['ProfilePage'][0]['graphql']['user']['is_private']         
            profile_page = data['ProfilePage'][0]['graphql']['user']
            bio = profile_page['biography']
            followings = profile_page['edge_follow']['count']
            followers= profile_page['edge_followed_by']['count']
            posts_count = profile_page['edge_owner_to_timeline_media']['count']
            profile_image = profile_page['profile_pic_url_hd']

            driver.close()
            driver.quit()
            return {
                'profile_image' : profile_image,
                'bio' : bio,
                "posts_count" : posts_count,
                "followers" : followers,
                "followings" : followings,
                "is_private" : is_private
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



#last updated on 16th August, 2020