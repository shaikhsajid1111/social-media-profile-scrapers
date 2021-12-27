try:
    import argparse
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from fake_headers import Headers
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    import json
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)


'''can scrap only public instagram accounts'''
class Instagram:
    @staticmethod
    def init_driver(browser_name):
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
            if browser_name.lower() == "chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Chrome(ChromeDriverManager().install(),options=browser_option)
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
            URL = 'https://instagram.com/{}'.format(username)

            try:
                driver = Instagram.init_driver(browser_name)
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()

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


            profile_data = {
                'profile_image' : profile_image,
                'bio' : bio,
                "posts_count" : posts_count,
                "followers" : followers,
                "followings" : followings,
                "is_private" : is_private
                }
            driver.close()
            driver.quit()
            return json.dumps(profile_data)
        except Exception as ex:
            driver.close()
            driver.quit()
            print(ex)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")
    parser.add_argument("--browser",help="Chrome or Firefox?")
    args = parser.parse_args()
    browser_name = args.browser if args.browser is not None else "chrome"
    print(Instagram.scrap(args.username,browser_name))



#last updated on 27th December, 2020