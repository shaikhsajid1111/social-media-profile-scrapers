
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

GECKO_PATH = "/opt/homebrew/bin/geckodriver"

options = FirefoxOptions()

service = FirefoxService(executable_path=GECKO_PATH)
driver = webdriver.Firefox(service=service, options=options)
username = "ohjoy"
profile_url = f"https://www.pinterest.com/{username}/"
driver.get(profile_url)

time.sleep(20)

#  Name
try:
    name_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    name = name_element.text.strip()
except:
    name = "Not found"

# Bio 
try:
    bio_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'pinterest.com/')]/following::div[1]"))
    )
    bio = bio_element.text.strip()
except:
    bio = "No bio found"


driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(6)

# Followers
follower_count = "Not available"
try:
    elems = driver.find_elements(By.XPATH, "//*[contains(text(), 'followers')]")
    for elem in elems:
        text = elem.text.strip()
        if "followers" in text.lower():
            parts = text.lower().replace(",", "").split()
            for i, part in enumerate(parts):
                if "followers" in part and i > 0:
                    follower_count = parts[i - 1]
                    break
            if follower_count != "Not available":
                break
except:
    pass


# Output
print("Name:", name)
print("Bio:", bio)
print("Followers:", follower_count)

driver.quit()