import argparse
import json
from services.json_fetcher import HTTPJSONStrategy
from interfaces.fetch_strategy import FetchJSONStrategy
from base_scraper import BaseScraper 
from model.http_settings import HTTPSettings
class Github(BaseScraper):
    def __init__(self, fetcher: FetchJSONStrategy):
        self.fetcher = fetcher

    def scrape(self, username: str):
        try:
            URL = f'https://api.github.com/users/{username}'
            response = self.fetcher.fetch_json_get(URL)
            return json.dumps(response)
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--username",help="username to search", default="shaikhsajid1111")
    
    args = parser.parse_args()
    username = args.username
    http_engine_config = HTTPSettings()
    http_engine = HTTPJSONStrategy(http_engine_config)
    ghub_scraper = Github(http_engine)
    data = ghub_scraper.scrape(username)
    print(data)



#last updated on June 2nd, 2026