"""GitHub profile scraper.

Public usage (unchanged from previous versions)::

    python github.py <username> [--browser chrome|firefox]

The profile is now read from the official REST API
(https://api.github.com/users/{username}) through the shared
``scraper_engine``: a fast ``curl_cffi`` request first, and - only if that does
not return usable data - a real browser via SeleniumBase UC mode as fallback.

The yearly contribution count is not part of the REST API, so it is still read
best-effort from the public profile page (github.com/{username}) through the
same engine, exactly like the old scraper did; pass ``--no-contributions`` to
skip that extra request (the key then stays an empty string).

The returned value is the same JSON string as before, with the original keys
(full_name, bio, location, contributions) plus a few extra API fields
(email, company, blog, twitter, public_repos, followers, following, user_since).

New optional flags (additions only, nothing removed):
    --engine auto|curl_cffi|seleniumbase_uc   pick the backend (default: auto)
    --headed                                  run the fallback browser non-headless
    --timeout N                               request / page load timeout (seconds)
    --no-contributions                        skip the yearly-contribution lookup
"""

try:
    import argparse
    import html as html_module
    import json
    import re

    from scraper_engine import FetchResult, ScrapingEngine
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
    exit()
except Exception as ex:
    print(ex)


class Github:
    """Scrapes public GitHub profile data through the shared scraping engine."""

    API_URL = "https://api.github.com/users/{}"
    PROFILE_URL = "https://github.com/{}"

    #: Backend priority: fast impersonated HTTP first, real browser as fallback.
    ENGINE_ORDER = ("curl_cffi", "seleniumbase_uc")

    #: "1,847 contributions in the last year" on the public profile page.
    _CONTRIB_RE = re.compile(
        r"([\d][\d,]*)\s*(?:<[^>]+>\s*)*contributions?\s*"
        r"(?:<[^>]+>\s*)*in\s+the\s+last\s+year",
        re.IGNORECASE)

    @staticmethod
    def quit_driver(driver):
        """Backwards compatible helper: cleanly shut a Selenium-like driver down."""
        if driver is None or isinstance(driver, str):
            return
        try:
            driver.close()
        except Exception:
            pass
        try:
            driver.quit()
        except Exception:
            pass

    @staticmethod
    def init_driver(browser_name="chrome", headless=True, uc=True):
        """Backwards compatible helper (kept so old imports keep working).

        Now backed by SeleniumBase (UC mode for Chromium browsers) instead of
        raw Selenium + webdriver_manager, but behaves the same: returns a ready
        driver, or the string "Browser Not Supported!" for unknown browsers.
        """
        try:
            from scraper_engine import SeleniumBaseUCClient
        except ImportError:
            return "Browser Not Supported!"
        name = str(browser_name or "chrome").strip().lower()
        if name not in ("chrome", "chromium", "edge", "firefox", "safari"):
            return "Browser Not Supported!"
        try:
            return SeleniumBaseUCClient().create_driver(browser=name, headless=headless, uc=uc)
        except Exception as ex:
            print(ex)
            return None

    # ------------------------------------------------------------------ #
    # internal helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_json(text):
        """Parse the JSON payload out of a raw response.

        Responses fetched through a real browser arrive wrapped in HTML
        (``<pre>{ ... }</pre>``), plain HTTP responses are pure JSON.
        """
        text = (text or "").strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            pass
        pre = re.search(r"<pre[^>]*>(.*?)</pre>", text, re.DOTALL | re.IGNORECASE)
        if pre:
            try:
                return json.loads(html_module.unescape(pre.group(1)).strip())
            except Exception:
                pass
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(html_module.unescape(text[start:end + 1]))
            except Exception:
                pass
        return None

    @staticmethod
    def _looks_like_user(result: FetchResult) -> bool:
        """Validator: the response is a GitHub user object, not an error
        payload (errors look like {"message": "Not Found", ...})."""
        data = Github._extract_json(result.text)
        return isinstance(data, dict) and "login" in data

    @staticmethod
    def _has_yearly_contributions(result: FetchResult) -> bool:
        return bool(Github._CONTRIB_RE.search(result.text or ""))

    @classmethod
    def _yearly_contributions(cls, engine, username, browser_name="chrome",
                              headless=True):
        """The REST API has no yearly-contribution count, so read the number
        the old scraper showed from the public profile page (best effort -
        returns "" when it cannot be read)."""
        result = engine.fetch(
            cls.PROFILE_URL.format(username),
            validator=cls._has_yearly_contributions,
            browser=browser_name or "chrome",
            headless=headless,
        )
        if result is None:
            return ""
        with result:
            match = cls._CONTRIB_RE.search(result.text or "")
            return match.group(1) if match else ""

    # ------------------------------------------------------------------ #
    # public API                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def scrap(username, browser_name="chrome", **options):
        """Scrape a public GitHub profile through the REST API.

        Args:
            username:     GitHub username.
            browser_name: browser used by the browser fallback backend
                          ("chrome" or "firefox") - same meaning as before.
            options:      optional extras, all of them optional:
                          engine_order, headless, timeout, verbose,
                          include_contributions.

        Returns the same JSON string as before, with the original keys
        (full_name, bio, location, contributions) plus extra API fields, or
        None when the profile could not be scraped.
        """
        username = str(username or "").strip().lstrip("@").rstrip("/")
        if not username:
            print("Please provide a valid username")
            return None

        engine_order = options.pop("engine_order", None) or Github.ENGINE_ORDER
        headless = options.pop("headless", True)
        timeout = options.pop("timeout", 30)
        verbose = options.pop("verbose", True)
        include_contributions = options.pop("include_contributions", True)

        engine = ScrapingEngine(engine_order, timeout=timeout, verbose=verbose)
        # curl_cffi ignores the browser specific kwargs; the SeleniumBase
        # backend picks them up (browser choice, headless/headed, UC mode).
        result = engine.fetch(
            Github.API_URL.format(username),
            validator=Github._looks_like_user,
            headers={"Accept": "application/vnd.github+json"},
            browser=browser_name or "chrome",
            headless=headless,
        )
        if result is None:
            if verbose:
                print("Could not scrape GitHub profile for '{}': {}".format(
                    username, "; ".join(engine.last_errors)))
            return None
        with result:
            data = Github._extract_json(result.text) or {}

        profile_data = {
            "full_name": data.get("name") or "",
            "bio": data.get("bio") or "",
            "location": data.get("location") or "",
            "contributions": "",
            "email": data.get("email") or "",
            "company": data.get("company") or "",
            "blog": data.get("blog") or "",
            "twitter": data.get("twitter_username") or "",
            "public_repos": data.get("public_repos") or 0,
            "followers": data.get("followers") or 0,
            "following": data.get("following") or 0,
            "user_since": str(data.get("created_at") or "")[:10],
        }
        if include_contributions:
            profile_data["contributions"] = Github._yearly_contributions(
                engine, username, browser_name or "chrome", headless)
        return json.dumps(profile_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username to search")
    parser.add_argument("--browser",
                        help="What browser your PC have? (used by the browser fallback backend)",
                        default="chrome")
    parser.add_argument("--engine", default="auto",
                        choices=("auto", "curl_cffi", "seleniumbase_uc"),
                        help="scraping backend; 'auto' = curl_cffi first, "
                             "then a browser with UC mode (default)")
    parser.add_argument("--headed", action="store_true",
                        help="run the fallback browser non-headless (helps when UC mode is blocked)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="request / page load timeout in seconds")
    parser.add_argument("--no-contributions", action="store_true",
                        help="skip the extra profile-page request for the yearly contribution count")
    args = parser.parse_args()

    engine_order = None if args.engine == "auto" else (args.engine,)
    print(Github.scrap(
        args.username,
        args.browser,
        engine_order=engine_order,
        headless=not args.headed,
        timeout=args.timeout,
        include_contributions=not args.no_contributions,
    ))

#last updated on 13th September, 2026
