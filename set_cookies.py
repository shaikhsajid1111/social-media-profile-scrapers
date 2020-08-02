import time
import pickle
import argparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium import webdriver
import configparser
import json
from selenium.common.exceptions import WebDriverException,TimeoutException
from fake_headers import Headers
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from settings import DRIVER_SETTINGS

class Set_cookies:
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
                driver = webdriver.Firefox(driver_path,options=browser_option)
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)
    @staticmethod
    def facebook_login(username,password,driver):
        try:
            driver = Set_cookies.init_driver(DRIVER_SETTINGS['PATH'],DRIVER_SETTINGS['BROWSER_NAME'])
        
            driver.get("https://facebook.com/")

            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'email'))) 

            username_input = driver.find_element_by_id('email')
            password_input = driver.find_element_by_id('pass')
            login_button = driver.find_element_by_xpath('//*[@data-testid="royal_login_button"]')
            username_input.send_keys(username)
            password_input.send_keys(password)
            time.sleep(1)
            login_button.click()
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'facebook')))
            driver.get("https://facebook.com/facebookai")
            time.sleep(5)
            Set_cookies.save_cookies(driver,os.path.join(os.getcwd(),"fbcookie.txt"))
            return json.dumps({
                "cookie_set" : "cookie is set"
            })
        except WebDriverException:
            driver.close()
            driver.quit()
            return json.dumps({"Error" : "Page is not loading, please check internet connection and try again"})
        except TimeoutException:
            driver.close()
            driver.quit()
            return json.dumps({
                "Invalid credentials " : "Username or Password is wrong"
            })
        except Exception as ex:
            driver.close()
            driver.quit()
            return json.dumps({
                "cookie_not_set" : "Cookie was not set due to {}".format(ex)
            })
    @staticmethod 
    def instagram_login(username,password,driver): 
        try:
            driver = Set_cookies.init_driver(DRIVER_SETTINGS['PATH'],DRIVER_SETTINGS['BROWSER_NAME'])
            driver.get("https://instagram.com")
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'username'))) 

            username_input = driver.find_element_by_name('username')
            username_input.send_keys(username)

            time.sleep(1)

            password_input =  driver.find_element_by_name('password')
            password_input.send_keys(password)

            submit_button = driver.find_element_by_xpath("*//*[@type='submit']")

            time.sleep(1)

            submit_button.click()    

            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'react-root'))) 
            driver.get("https://instagram.com/instagram")
            
            Set_cookies.save_cookies(driver,os.path.join(os.getcwd(),"cookie.txt"))
                
            driver.close()
            driver.quit()
            return json.dumps({
                "cookie_set" : "cookie is set"
            })
        
        except WebDriverException:
            driver.close()
            driver.quit()
            return json.dumps({"Error" : "Page is not loading, please check internet connection and try again"})
        except TimeoutException:
            driver.close()
            driver.quit()
            return json.dumps({
                "Invalid credentials " : "Username or Password is wrong"
            })
        
        except Exception as ex:
            return json.dumps({
                "cookie_not_set" : "Cookie was not set due to {}".format(ex)
            })
    @staticmethod           
    def load_cookies(driver, location, url=None):

        cookies = pickle.load(open(location, "rb"))
        driver.delete_all_cookies()
    # have to be on a page before you can add any cookies, any page - does not matter which
        driver.get("https://google.com" if url is None else url)
        
        for cookie in cookies:

            if isinstance(cookie.get('expiry'), float):#Checks if the instance expiry a float 
                cookie['expiry'] = int(cookie['expiry'])# it converts expiry cookie to a int 
            
            driver.add_cookie(cookie)
    @staticmethod
    def save_cookies(driver, location):
        pickle.dump(driver.get_cookies(), open(location, "wb"))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help= "username for account")
    parser.add_argument("password",help="Password for the account")
    parser.add_argument('media',help="Facebook or Instagram? 'fb' for Facebook and 'ig' for Instagram")
    args = parser.parse_args()

