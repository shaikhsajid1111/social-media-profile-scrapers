# Social Media Profile Crawlers

## Available Social Media
- Twitter :+1:
- Facebook :+1:
- Instagram :+1:
- Reddit :+1:   
- tiktok :+1:
- Medium :+1:
- Quora :+1:


## To do

- Pinterest :clock1:

## How to run these scripts?
1. You need person's social media username to fetch detail
1. Install dependencies mentioned inside [requirement.txt](requirement.txt) by entering command ```pip install -r requirement.txt``` from project's directory directory
1. There are 2 ways to input username
    - Edit source code of the script and pass username as a constructor's parameter
    - Pass username from command line
        - Open terminal in project's directory and type command ```python SCRIPT_NAME USERNAME```
1. Some scripts use chromdriver, install chromedriver from [here](https://chromedriver.chromium.org/downloads). Chrome browser's version must be same as chromedriver's version

- If server stop responding because of too much request, so try modifying requests.get() with below given code:
    - ```requests.get(URL,headers = headers,proxies={"http": "http://111.233.225.166:1234"})```
                                or
    - ```requests.get(URL,headers = headers,verify = False)```
                                or
    - ```requests.get(URL,headers = headers,timeout = 5)```
                            




**More social media will be added :sleepy:**