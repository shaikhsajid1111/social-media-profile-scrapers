try:
    import argparse
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from fake_headers import Headers
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    import re
    import json
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
            ua = Headers().generate()  # fake user agent
            # browser_option.add_argument('--headless')
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
            if browser_name == "Chrome":
                browser_option = ChromeOptions()
                browser_option = set_properties(browser_option)
                driver = webdriver.Chrome(ChromeDriverManager().install(
                ), options=browser_option)  # chromedriver's path in first argument
            elif browser_name == "Firefox":
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
    def value_to_float(x):
        try:
            x = float(x)
            return int(x)
        except:
            pass
        x = x.lower()
        if 'k' in x:
            if len(x) > 1:
                return int(float(x.replace('k', '')) * 1000)
            return 1000
        if 'm' in x:
            if len(x) > 1:
                return int(float(x.replace('m', '')) * 1000000)
            return 1000000
        if 'b' in x:
            return int(float(x.replace('b', '')) * 1000000000)
        return 0

    @staticmethod
    def scrap(username, browser_name):
        """scrap medium's profile"""
        try:
            URL = "https://medium.com/@{}".format(username)

            try:
                driver = Medium.init_driver(browser_name)
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()

            # wait until page loads so title contains "Medium"
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains('Medium'))
            try:
                profile_image = driver.find_element_by_css_selector(
                    'meta[property="og:image"]')
            except Exception as ex:
                profile_image = ""
            first_name = driver.find_element_by_css_selector(
                'meta[property="profile:first_name"]').get_attribute("content")
            last_name = driver.find_element_by_css_selector(
                'meta[property="profile:last_name"]').get_attribute("content")

            full_name = first_name + " " + last_name
            try:
                bio = driver.find_element_by_css_selector(
                    'meta[name="description"]').get_attribute("content")
                bio_splits = bio.split(".")
                bio = "".join(bio_splits[1:])
            except Exception as ex:
                print(ex)
                bio = ""
            try:
                followings = driver.find_element_by_xpath(
                    "//a[contains(text(),'See all')]")
            except Exception as ex:
                print(ex)
                followings = ""
            followings = re.findall(
                r'\d+', followings.get_attribute("innerHTML"))
            followings = "".join(followings)
            followings = Medium.value_to_float(followings)
            try:
                followers = driver.find_element_by_xpath(
                    "//a[contains(@href, 'followers')]")
                followers = Medium.value_to_float(followers.text.split(" ")[0])
            except Exception as ex:
                print(ex)
                followers = ""

            profile_data = {
                "profile_image": profile_image.get_attribute("content"),
                'full_name': full_name,
                "bio": bio,
                "followings": followings,
                "followers": followers
            }
            driver.close()
            driver.quit()
            return json.dumps(profile_data)
        except Exception as ex:
            driver.close()
            driver.quit()
            return {"error": ex}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username to search")
    parser.add_argument("--browser", help="What browser your PC have?")

    args = parser.parse_args()
    browser_name = args.browser if args.browser is not None else "chrome"
    print(Medium.scrap(args.username, browser_name))

# last modified on : 28th December,2021
