from pydantic import BaseModel


class BrowserSettings(BaseModel):
    browser: str = "chrome"
    headless: bool = False
    browser_path: str
    uc: bool = True
    xvfb = False
