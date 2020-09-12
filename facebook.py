try:

    import selenium
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support import expected_conditions as EC
    from fake_headers import Headers
    import argparse
    import configparser
    import time
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
except ModuleNotFoundError:
    print("Please download dependecies from requirement.txt")
    exit()
except Exception as ex:
    print(ex)    



class Facebook:
    @staticmethod
    def quit_driver(driver):
        driver.close(
        )
        driver.quit()
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
            elif browser_name.lower() == "firefox":
                browser_option = FirefoxOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Firefox(executable_path= GeckoDriverManager().install(),options=browser_option)
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)

    @staticmethod
    def scrap(username,browser_name):
        try:
            URL = "https://facebook.com/{}".format(username)
            
            
            driver = Facebook.init_driver(browser_name)  
        
            try:
                driver.get(URL)
            except AttributeError:
                print("Driver is not set!")
                exit()
            #wait until element is present with ID fb-timeline-cover-name
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.ID, "fb-timeline-cover-name")))
            #get source code of the page
            
            facebook_name = driver.find_element_by_id("fb-timeline-cover-name")
            
            try:
                profile_image = driver.find_element_by_css_selector("img._11kf.img")
            except NoSuchElementException:
                profile_image = ""
            try:
                current_city = driver.find_element_by_id("current_city")
            except NoSuchElementException:
                current_city = ""
            try:
                educations = driver.find_element_by_class_name("fbProfileEditExperiences")
            except NoSuchElementException:
                educations = ""
            
        
            profile_data =  {
                    "profile_image" : profile_image.get_attribute("src") if type(profile_image) is not str else "",
                    "current_city" : current_city.text.strip() if type(current_city) is not str else "",
                    "Education" : educations.text if type(educations) is not str else ""
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
    print(Facebook.scrap(args.username,browser_name))

#last updated on 11th September, 2020