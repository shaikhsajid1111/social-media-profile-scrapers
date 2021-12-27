try:
    import argparse
    import json
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



class Reddit:
    @staticmethod
    def init_driver(browser_name):
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
            if browser_name.lower() == "chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Chrome(ChromeDriverManager().install(),options=browser_option) #chromedriver's path in first argument
                driver.maximize_window()
            elif browser_name.lower() == "firefox":
                browser_option = FirefoxOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=browser_option)
                driver.maximize_window()
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)

    @staticmethod
    def close_driver(driver):
        driver.close()
        driver.quit()

    @staticmethod
    def scrap(username,browser_name):
        try:
            URL = "https://reddit.com/user/{}".format(username)

            try:

                driver = Reddit.init_driver(browser_name)
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()



            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located(
                (By.ID, 'profile--id-card--highlight-tooltip--karma')))

            name = driver.title.split(" ")[0]
            bio = driver.find_element_by_class_name("bVfceI5F_twrnRcVO1328").text.strip()
            try:
                banner = driver.find_element_by_class_name("_2ZyL7luKQghNeMnczY3gqW").get_attribute("style")
            except:
                banner = None

            profile = driver.find_element_by_class_name(
                '_2bLCGrtCCJIMNCZgmAMZFM').get_attribute("src")

            karma = driver.find_element_by_id(
                "profile--id-card--highlight-tooltip--karma")
            cake_date = driver.find_element_by_id("profile--id-card--highlight-tooltip--cakeday")

            data =  {
                    "name" : name,
                    "bio" : bio,
                    "banner" : banner.split('(')[-1].split(')')[0] if banner is not None else "",
                    "profile_image" : profile,
                    "karma": karma.get_attribute("innerHTML"),
                    "cake_date": cake_date.get_attribute("innerHTML")
                }
            Reddit.close_driver(driver)
            return json.dumps(data)
        except Exception as ex:
            driver.close()
            driver.quit()
            print(ex)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to scrap")
    parser.add_argument("--browser",help="What browser your PC have?")
    args = parser.parse_args()
    browser_name = args.browser if args.browser is not None else "chrome"
    print(Reddit.scrap(args.username,browser_name))

#last updated - 27th December, 2021
