# Social Media Profile Crawlers


[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](hhttps://github.com/shaikhsajid1111/social-media-profile-scrapers/graphs/commit-activity)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)







## Available Social Media
- Twitter :+1:
- Facebook :+1:
- Instagram :+1:
- Reddit :+1:   
- tiktok :+1:
- Medium :+1:
- Quora :+1:
- Linkedin :+1:
- Pinterest :+1:
- Github :+1:


![Screenshot](screenshots/screenshot1.PNG)



## Installation

1. You need person's social media username to fetch detail

1. Install dependencies mentioned inside [requirement.txt](requirement.txt) by entering command ```pip install -r requirement.txt``` from project's directory and chromedriver, from [here](https://chromedriver.chromium.org/downloads). 
 **Browser's version must be compatible with driver's version**. See how to setup for [firefox](https://stackoverflow.com/questions/42204897/how-to-setup-selenium-python-environment-for-firefox), [Chrome](https://chromedriver.chromium.org/getting-started)

1. There are 2 ways to input username
    1. Edit source code of the script and pass username as a argument for static method and run from terminal with ```python SCRIPT_NAME```
    1. Pass username from command line  . See [demo](screenshots/demo.gif)
        - Open terminal in project's directory and type command ```python SCRIPT_NAME USERNAME```
    1. In case server stop responding then use [proxies](proxies.py) everytime you make a request. See reference [here](https://stackoverflow.com/questions/11450158/how-do-i-set-proxy-for-chrome-in-python-webdriver)
    


## Tech

- [chromedriver](https://chromedriver.chromium.org) or [gecko Driver](https://github.com/mozilla/geckodriver/releases)
- [selenium](https://selenium-python.readthedocs.io/installation.html)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [fake-headers](https://pypi.org/project/fake-headers/)   

## LICENSE 

### Apache License 2.0                                 

**If You have suggestions for more social media. Let me know :wink:**


