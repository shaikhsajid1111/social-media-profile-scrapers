import requests
from interfaces.fetch_strategy import FetchJSONStrategy
from model.http_settings import HTTPSettings

class HTTPJSONStrategy(FetchJSONStrategy):
    def __init__(self, settings: HTTPSettings):
        self.settings = settings

    def fetch_json_get(self, url):
        for _ in range(self.settings.retry):
            response = requests.get(url, 
                                    timeout=self.settings.timeout, 
                                    headers=self.settings.headers)
            
            if response and response.status_code == 200:
                return response.json()
            
            print(f"Received code status : {response.status_code} for {url}")
        return ""

    def fetch_json_post(self, url):
        raise NotImplementedError()

    