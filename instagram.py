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
    from selenium.common.exceptions import NoSuchElementException
    import json
    from selenium.webdriver.common.by import By
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
            ua = Headers().generate()  # fake user agent
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

            # automating and opening URL in headless browser
            if browser_name.lower() == "chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=browser_option)
            elif browser_name.lower() == "firefox":
                browser_option = FirefoxOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Firefox(
                    executable_path=GeckoDriverManager().install(), options=browser_option)
            else:
                driver = "Browser Not Supported!"
            return driver
        except Exception as ex:
            print(ex)

    @staticmethod
    def find_bio(driver):
        try:
            element = driver.find_element_by_css_selector('div._aa_c')
            return element.text
        except NoSuchElementException:
            return ''
        except Exception as ex:
            print("Error at find_bio : {}".format(ex))

    @staticmethod
    def value_to_float(x):
        try:
            x = float(x)
            return x
        except:
            pass
        x = x.lower()
        if 'k' in x:
            if len(x) > 1:
                return float(x.replace('k', '')) * 1000
            return 1000
        if 'm' in x:
            if len(x) > 1:
                return float(x.replace('m', '')) * 1000000
            return 1000000
        if 'm' in x:
            return float(x.replace('m', '')) * 1000000000
        return 0

    @staticmethod
    def find_profile_image_link(driver):
        try:
            profile_image = driver.find_element_by_tag_name(
                "img")
            return profile_image.get_attribute('src')
        except NoSuchElementException:
            print('Element Not Found')
            profile_image = ''
        # except Exception as ex:
        #  print("Error at find_profile_image_link : {}".format(ex))

    @staticmethod
    def extract_posts_count(text):
        try:
            if 'Posts' in text:
                text = text.split(" ")[-2]
                text = text.replace(',', '')
                print(text)
                return int(Instagram.value_to_float(text))
        except Exception as ex:
            print("Error at extract_posts_count: {}".format(ex))
            return None

    @staticmethod
    def extract_followers_count(text):
        try:
            if 'Followers' in text:
                return int(Instagram.value_to_float(text.split(" ")[0]))
        except Exception as ex:
            print("Error at extract_followers_count : {}".format(ex))
            return None

    @staticmethod
    def extract_following_count(text):
        try:
            if 'Followers' in text:
                return int(Instagram.value_to_float(text.split(" ")[2]))
        except Exception as ex:
            print("Error at extract_followers_count : {}".format(ex))
            return None

    @staticmethod
    def find_bio(driver):
        try:
            elements = driver.find_elements_by_css_selector(
                'div._aacl._aacp._aacu._aacx._aad6._aade')
            if len(elements) == 4:
                return elements[-1].get_attribute('textContent')
            return ''
        except NoSuchElementException:
            print('Element Not Found')
            return ''
        except Exception as ex:
            print("Error at find_bio : {}".format(ex))

    @staticmethod
    def is_private(driver):
        try:
            driver.find_element_by_xpath(
                "//h2[text()='This Account is Private']")
            return True
        except NoSuchElementException:
            return False
        except Exception as ex:
            print("Error at is_private : {} ".format(ex))

    @staticmethod
    def scrap(username, browser_name):
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
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
            description_meta = driver.find_element_by_css_selector(
                'meta[name="description"]')
            meta_content = description_meta.get_attribute(
                'content').split('-')[0]
            posts_count = Instagram.extract_posts_count(meta_content.strip())
            followers_count = Instagram.extract_followers_count(meta_content)
            followings_count = Instagram.extract_following_count(meta_content)
            profile_image = Instagram.find_profile_image_link(driver)
            bio = Instagram.find_bio(driver)
            is_private = Instagram.is_private(driver)
            profile_data = {
                'profile_image': profile_image,
                'bio': bio,
                "posts_count": posts_count,
                "followers": followers_count,
                "followings": followings_count,
                "is_private": is_private
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
    parser.add_argument("username", help="username to search")
    parser.add_argument("--browser", help="Chrome or Firefox?")
    args = parser.parse_args()
    browser_name = args.browser if args.browser is not None else "chrome"
    print(Instagram.scrap(args.username, browser_name))


# last updated on 15th October, 2022
