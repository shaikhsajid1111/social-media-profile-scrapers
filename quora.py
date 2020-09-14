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

class Quora:
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

            
            #automating and opening URL in headless browser
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
            URL = 'https://quora.com/profile/{}'.format(username)
            try:
                    
                driver = Quora.init_driver(browser_name)  
                driver.get(URL)
            except AttributeError:
                print("Driver is not set")
                exit()
            
            

            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.title_contains('Quora'))

            name = driver.find_element_by_css_selector("div.q-text.qu-bold")
            try:
                profession = driver.find_element_by_css_selector("div.q-text.qu-fontSize--large")
            except:
                profession = ""
            
            try:
                profile_image = driver.find_element_by_css_selector("img.q-image.qu-display--block")
            except:
                profile_image = ""
            try:
                bio = driver.find_element_by_css_selector("div.q-box.qu-mt--small")
            except:
                bio = ""
            try:
                driver.find_element_by_class_name("q-absolute").click()
            except:
                pass
            try:
                answers_count = driver.find_element_by_css_selector('div.q-text.qu-medium.qu-fontSize--small.qu-color--red')
            except:
                answers_count = ""
            try:
                detail_count = driver.find_elements_by_css_selector('div.q-text.qu-medium.qu-fontSize--small.qu-color--gray_light')
                questions = detail_count[0]
                shares = detail_count[1]
                posts = detail_count[2]
                followers = detail_count[3]
                
                #followings = detail_count[4]
                          
            except:
                questions,shares,posts,followers,followings = ''    
            try:
                more_button = driver.find_element_by_name("ChevronDown").click()
                popup = driver.find_element_by_class_name("qu-zIndex--popover")
                all_divs = popup.find_elements_by_css_selector("div")
                followings = all_divs[0]
            except:
                followings = ""
            try:
                more = driver.find_elements_by_css_selector("div.q-text.qu-truncateLines--2")
            except:
                more = ""
            profile_data = {
                'name'  :name.text,
                'profession' : profession.text.strip(),
                'profile_image' : profile_image.get_attribute("src"),
                'bio' : bio.text,
                'answers_count' : answers_count.text.strip().split(" ")[0],
                'questions_count' : questions.text.strip().split(" ")[0],
                'shares' : shares.text.strip().split(" ")[0],
                'posts' : posts.text.strip().split(" ")[0],
                'followers' : followers.text.strip().split(" ")[0],
                'following' : followings.text.split(" ")[0],
                'more_details' : [more[i].text.replace('\n','').replace('\r','') for i in range(len(more))] if type(more) is not str else ""
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
    print(Quora.scrap(args.username,browser_name))

#last updated - 11th September, 2020