from abc import ABC, abstractmethod
from typing import Dict

from abc import ABC, abstractmethod
from typing import Dict

class FetchHTMLStrategy(ABC):
    @abstractmethod
    def fetch_html_get(self, url: str) -> str:
        """Returns raw HTML string."""
        pass

    @abstractmethod
    def fetch_html_post(self, url: str) -> str:
        """Returns raw HTML string."""
        pass

class FetchJSONStrategy(ABC):
    @abstractmethod
    def fetch_json_get(self, url: str) -> Dict:
        """Returns parsed JSON dictionary."""
        pass

    @abstractmethod
    def fetch_json_post(self, url: str) -> str:
        """Returns json."""
        pass
