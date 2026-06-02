from interfaces.fetch_strategy import SeleniumFetchStrategy
from seleniumbase import SB
from model.browser_settings import BrowserSettings
from utils.force_close_utils import ForceProcessCloseUtils

class SeleniumFetcher(SeleniumFetchStrategy):
    def __init__(self):
        pass

    def fetch_html_get(self, url, 
                   browser_setting: BrowserSettings):
        try:
            pids_before = ForceProcessCloseUtils.extract_processes_pids(browser_name_lower)
            with SB(
                browser=browser_setting.browser,
                uc=browser_setting.uc,
                headless=browser_setting.headless,
                xvfb=browser_setting.xvfb
            ) as sb:
                sb.open(url)
                browser_name_lower = browser_setting.browser.lower()
                
                if sb.is_text_visible("checking your browser", "body"):
                    sb.sleep(5)
                
                source_html = sb.get_page_source()
                return source_html
        except Exception as ex:
            print(f"Error while extracting HTML page using selenium: {ex}")
            return ""
        
        finally:
            sb.sleep(0.5)
            pids_after = ForceProcessCloseUtils.extract_processes_pids(browser_name_lower)
            spawned_pids = pids_after - pids_before
            ForceProcessCloseUtils.force_close_processes(spawned_pids)