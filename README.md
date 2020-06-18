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
 **Chrome browser's version must be compatible with chromedriver's version**

1. There are 2 ways to input username
    1. Edit source code of the script and pass username as a argument for static method
    1. Pass username from command line  . See [demo](screenshots/demo.gif)
        - Open terminal in project's directory and type command ```python SCRIPT_NAME USERNAME```

- If server stop responding because of too much request, so try modifying ```requests.get()``` with below given code:
  - ```requests.get(URL,headers = headers,verify = False)```
                                or
  - ```requests.get(URL,headers = headers,timeout = 5)```
                                or
  -  Import [proxies](proxies.py) and use random proxies everytime you make a request ```requests.get(URL,proxies=proxy)```

## Tech

- [chromdriver](https://chromedriver.chromium.org)
- [selenium](https://selenium-python.readthedocs.io/installation.html)
- [requests](https://requests.readthedocs.io/en/master/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [fake-headers](https://pypi.org/project/fake-headers/)   
## LICENSE 

### Apache License 2.0                                 

**If You have suggestions for more social media. Let me know :wink:**


