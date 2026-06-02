import requests
from interfaces.fetch_strategy import FetchHTMLStrategy
from model.http_settings import HTTPSettings

class HTTPFetchStrategy(FetchHTMLStrategy):

    def __init__(self, settings: HTTPSettings):
        self.settings = settings

    def fetch_html_get(self, url):
        for _ in range(self.settings.retry):
            response = requests.get(url, 
                                    timeout=self.settings.timeout, 
                                    headers=self.settings.user_agent)
            
            if response and response.status_code == 200:
                return response.text
            
            print(f"Received code status : {response.status_code} for {url}")
        return ""
    
    def fetch_html_post(self, url):
        raise NotImplementedError()

