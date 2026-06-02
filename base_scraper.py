from abc import abstractmethod, ABC
from model.scraper_settings import ScraperSettings
from interfaces.fetch_strategy import FetchHTMLStrategy, FetchJSONStrategy
from typing import Union

class BaseScraper(ABC):

    def __init__(self, fetcher: Union[FetchJSONStrategy, FetchHTMLStrategy]):
        self.fetcher = fetcher

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"Scraper execution crashed: {exc_val}")
        
        # Safe cleanup: close the engine if it has a close method (like Selenium)
        if hasattr(self.fetcher, "close"):
            self.fetcher.close()

    @abstractmethod
    def scrape(username: str):
        pass
    