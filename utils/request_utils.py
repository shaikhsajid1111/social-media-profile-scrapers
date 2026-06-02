from fake_headers import Headers
from typing import Dict

class RequestUtils:
    @staticmethod
    def build_http_user_agent(
        browser = None,
        os = None
    ) -> Dict:
        user_agent = Headers(browser=browser, os=os).generate()
        return user_agent