# Social Media Profile Crawlers

> These are the collections of scripts that scrape's social media profiles

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/shaikhsajid1111/social-media-profile-scrapers/graphs/commit-activity)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


---
## ⚡ Sponsor

### **[CoreClaw](https://www.coreclaw.com/?utm_source=github&utm_medium=referral&utm_campaign=social&utm_term=social&utm_id=social) — Web Scraping Platform & Ready-to-Use Data Extraction Tools**

[![CoreClaw Banner](assets/images/coreclaw_banner.png)](https://www.coreclaw.com/?utm_source=github&utm_medium=referral&utm_campaign=social&utm_term=social&utm_id=social)

[CoreClaw](https://www.coreclaw.com/?utm_source=github&utm_medium=referral&utm_campaign=social&utm_term=social&utm_id=social) provides **100+ ready-to-use data scraping tools** for platforms like Amazon, TikTok, Google Maps, Instagram, Facebook, YouTube, and more.

*   **🚫 No Coding Required** — Extract structured data effortlessly.
*   **🔄 Flexible Formats** — Export seamlessly to JSON or CSV format.
*   **🛡️ Pay-Per-Success** — Only pay for successful results with no wasted budget on failed extractions.

### 🎁 Special Offer
**[Get started with a free $3 trial today!](https://www.coreclaw.com/?utm_source=github&utm_medium=referral&utm_campaign=social&utm_term=social&utm_id=social)**
---




## Available Social Media
* Twitter
* Facebook
* Instagram
* Reddit
* TikTok
* Medium
* Quora
* Pinterest
* Github



## Installation

1. Install dependencies mentioned inside [requirement.txt](requirement.txt) by opening terminal in project's directory and enter command
    ```
    pip install -r requirement.txt
    ```
## Usage

1. Open terminal in project's directory and enter command
    ```
    python SCRIPT_NAME USERNAME --browser BROWSER_NAME
    ```
    example
    ```
    python twitter.py barackObama --browser firefox
    ```
    if ```--browser``` argument is not passed, chrome is used by default. **currently only firefox and chrome is supported**
    - for more help enter command
    ```
    python SCRIPT_NAME -h
    ```
    example
    ```
    python instagram.py -h
    ```
    Note: Pinterest, Medium and Twitter script doesn't need browser. Just use it like ```python pinterest.py username```
    Github reads the GitHub REST API directly (```python github.py username```); a browser is only started as a fallback for the yearly-contribution count (skip it with ```--no-contributions```).
## Tech

- [chromedriver](https://chromedriver.chromium.org) or [gecko Driver](https://github.com/mozilla/geckodriver/releases)
- [selenium](https://selenium-python.readthedocs.io/installation.html)
- [fake-headers](https://pypi.org/project/fake-headers/)
- [wedriver_manager](https://pypi.org/project/webdriver-manager/)

## Shared scraping engine

All scraper scripts share one fetching mechanism: [scraper_engine.py](scraper_engine.py).
Each script first tries a fast **curl_cffi** request (browser-impersonated TLS,
no browser started) and automatically falls back to a real browser through
**SeleniumBase UC mode** (undetected-chromedriver) when the HTTP attempt does
not return usable data. Extra optional flags are available, e.g.:

```
python facebook.py USERNAME --engine auto     # curl_cffi first, then UC browser (default)
python facebook.py USERNAME --headed          # run the fallback browser non-headless
python facebook.py USERNAME --json            # print the result as JSON
```

The engine is extensible: new backends (a paid API service, FlareSolverr, ...)
can be plugged in without touching the scripts - see the module docstring of
[scraper_engine.py](scraper_engine.py).



## Screenshot
![](screenshot/output.png)


## LICENSE

### Apache License 2.0

**If You have suggestions for more social media. Let me know :wink:**


