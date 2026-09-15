"""Pinterest profile scraper.

Public usage (unchanged from previous versions)::

    python pinterest.py <username> [--browser chrome|firefox] [--proxy PROXY]
                        [--debug] [--headed]

The profile is read from the ``__PWS_INITIAL_PROPS__`` JSON payload that
Pinterest embeds in every profile page (``initialReduxState.users``) through
the shared ``scraper_engine``: a fast ``curl_cffi`` request first, and - only
if that does not return usable data - a real browser via SeleniumBase UC mode
as fallback.  As a last resort the old page-text regexes are used
(``data_source: "page_text"``), so the returned keys and shape stay the same:
username, full_name, follower_count, follower_count_text, following_count,
following_count_text, pin_count, board_count, about, profile_image,
website_url, is_verified, data_source (None values are dropped, like before).

New optional flags (additions only, nothing removed):
    --engine auto|curl_cffi|seleniumbase_uc   pick the backend (default: auto)
    --timeout N                               request / page load timeout (seconds)
"""

try:
    import argparse
    import html as html_module
    import json
    import re

    from scraper_engine import ScrapingEngine
except ModuleNotFoundError:
    print("Please install: pip install curl-cffi seleniumbase beautifulsoup4")
    exit(1)
except Exception as ex:
    print(ex)


class Pinterest:
    """Pinterest profile scraper backed by the shared scraping engine."""

    PROFILE_URL = "https://www.pinterest.com/{}/"

    #: Backend priority: fast impersonated HTTP first, real browser as fallback.
    ENGINE_ORDER = ("curl_cffi", "seleniumbase_uc")

    #: The profile data lives in Pinterest's embedded initial-state payload:
    #: <script id="__PWS_INITIAL_PROPS__" type="application/json">{ ... }</script>
    #: with the user object at initialReduxState.users[<user id>] (fields
    #: verified against ohjoy_pinterest.html: username, full_name, about,
    #: follower_count, following_count, pin_count, board_count,
    #: image_medium_url, image_xlarge_url, website_url, type: "user").
    #: A generic walk is used so UserResource-style payloads match too.
    _PWS_SCRIPT_RE = re.compile(
        r"<script[^>]*id=\"__PWS_INITIAL_PROPS__\"[^>]*>(.*?)</script>",
        re.IGNORECASE | re.DOTALL)

    #: page-text fallback (old "method 3"): "556.5k followers" / "1.2M followers"
    _FOLLOWER_TEXT_RE = re.compile(r"([\d.,]+\s*[KMB]?)\s*followers?", re.IGNORECASE)
    _FOLLOWING_TEXT_RE = re.compile(r"([\d.,]+\s*[KMB]?)\s*following\b", re.IGNORECASE)

    _USER_FIELDS = ("full_name", "follower_count", "following_count", "pin_count",
                    "board_count", "about", "image_medium_url", "image_xlarge_url",
                    "website_url", "is_verified")

    @staticmethod
    def convert_text_to_number(text):
        """Convert '556.5k' to 556500, '1.2M' to 1200000, etc."""
        if not text:
            return None

        text = text.strip().upper()
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}

        for suffix, multiplier in multipliers.items():
            if suffix in text:
                try:
                    number = float(text.replace(suffix, '').replace(',', ''))
                    return int(number * multiplier)
                except Exception:
                    return None

        # No suffix, just a number
        try:
            return int(text.replace(',', ''))
        except Exception:
            return None

    @staticmethod
    def init_driver(browser_name: str, proxy: str = None, headed: bool = False,
                    enable_network_log: bool = True):
        """Backwards compatible helper (kept so old imports keep working).

        Now backed by SeleniumBase (UC mode for Chromium browsers) instead of
        raw Selenium + webdriver_manager, but behaves the same: returns a ready
        driver, prints the same messages and returns None on failures.
        """
        try:
            from seleniumbase import Driver
        except ImportError:
            return None

        name = (browser_name or "chrome").strip().lower()
        if name not in ("chrome", "chromium", "edge", "firefox", "safari"):
            print("Browser '{}' not supported.".format(browser_name))
            return None

        try:
            kwargs = {"browser": "chrome" if name == "chromium" else name}
            if name in ("chrome", "chromium", "edge"):
                kwargs["uc"] = True
                if not headed:
                    kwargs["headless2"] = True
            elif not headed:
                kwargs["headless"] = True
            if proxy:
                kwargs["proxy"] = proxy
            return Driver(**kwargs)
        except Exception as ex:
            print("Error starting {}: {}".format(browser_name, ex))
            return None

    # ------------------------------------------------------------------ #
    # internal helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _iter_dicts(node):
        """Depth-first walk over every dict inside a parsed payload."""
        if isinstance(node, dict):
            yield node
            for value in node.values():
                yield from Pinterest._iter_dicts(value)
        elif isinstance(node, list):
            for value in node:
                yield from Pinterest._iter_dicts(value)

    @staticmethod
    def _extract_user(html, username, debug=False):
        """Pull the profile out of a fetched profile page.

        1. ``__PWS_INITIAL_PROPS__`` payload -> initialReduxState.users entry
           (or any UserResource-style entry) whose ``username`` matches,
           picking the richest match.
        2. page-text fallback (old method 3): follower/following regexes.

        Returns the user dict or None.
        """
        target = (username or "").strip().lower()
        best, best_score = None, -1

        for match in Pinterest._PWS_SCRIPT_RE.finditer(html or ""):
            body = match.group(1)
            try:
                data = json.loads(body)
            except Exception:
                try:
                    data = json.loads(html_module.unescape(body))
                except Exception:
                    if debug:
                        print("[DEBUG] __PWS_INITIAL_PROPS__ is not valid JSON")
                    continue

            for node in Pinterest._iter_dicts(data):
                node_username = node.get("username")
                if not isinstance(node_username, str) \
                        or node_username.lower() != target:
                    continue
                if node.get("type") not in (None, "user"):
                    continue
                score = sum(1 for field in Pinterest._USER_FIELDS if field in node)
                if score > best_score:
                    best, best_score = node, score

        if best is not None:
            if debug:
                print("[DEBUG] extracted user from __PWS_INITIAL_PROPS__ "
                      "({} matching fields)".format(best_score))
            return best

        # page-text fallback (old method 3)
        stats = {"username": username, "extracted_from": "page_text"}
        follower = Pinterest._FOLLOWER_TEXT_RE.search(html or "")
        following = Pinterest._FOLLOWING_TEXT_RE.search(html or "")
        if follower:
            stats["follower_count_text"] = re.sub(r"\s+", "", follower.group(1))
        if following:
            stats["following_count_text"] = re.sub(r"\s+", "", following.group(1))
        if "follower_count_text" in stats or "following_count_text" in stats:
            if debug:
                print("[DEBUG] extracted partial data from page text")
            return stats

        if debug:
            print("[DEBUG] no __PWS_INITIAL_PROPS__ user data and no text counts found")
        return None

    # ------------------------------------------------------------------ #
    # public API                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def scrap(username: str, browser_name: str = "chrome", proxy: str = None,
              debug: bool = False, headed: bool = False, **options) -> str:
        """Scrape a Pinterest profile from the embedded __PWS_INITIAL_PROPS__.

        Same signature and return value as before: a JSON string with the
        profile keys (None values dropped), or a JSON error object
        ({"error": ...}) when the profile could not be scraped.

        Optional extras (all of them optional):
            engine_order, timeout.
        """
        username = str(username or "").strip().lstrip("@").rstrip("/")
        engine_order = options.pop("engine_order", None) or Pinterest.ENGINE_ORDER
        timeout = options.pop("timeout", 30)

        try:
            url = Pinterest.PROFILE_URL.format(username)
            if debug:
                print("[DEBUG] Loading: {}".format(url))

            engine = ScrapingEngine(engine_order, timeout=timeout, verbose=debug)
            # curl_cffi ignores the browser specific kwargs; the SeleniumBase
            # backend picks them up (browser choice, headed mode, UC mode,
            # proxy).
            client_opts = {
                "browser": browser_name or "chrome",
                "headless": not headed,
            }
            if proxy:
                client_opts["proxies"] = {"http": proxy, "https": proxy}  # curl_cffi
                client_opts["proxy"] = proxy                              # seleniumbase

            result = engine.fetch(
                url,
                validator=lambda res: Pinterest._extract_user(
                    res.text or "", username, debug=debug) is not None,
                **client_opts)
            if result is None:
                return json.dumps({
                    "error": "all_methods_failed",
                    "hint": "All extraction methods failed. Pinterest may have "
                            "changed structure or detected automation. Try the "
                            "--headed flag or a different --proxy.",
                    "username": username,
                })
            with result:
                user_data = Pinterest._extract_user(result.text or "", username,
                                                    debug=debug)
        except Exception as ex:
            if debug:
                import traceback
                traceback.print_exc()
            return json.dumps({"error": "unexpected_exception", "message": str(ex)})

        if not user_data:  # validator passed but extraction failed - very unlikely
            return json.dumps({
                "error": "all_methods_failed",
                "hint": "The page was fetched but no profile data could be extracted.",
                "username": username,
            })

        profile_data = {
            "username": user_data.get("username") or username,
            "full_name": user_data.get("full_name") or user_data.get("name"),
            "follower_count": user_data.get("follower_count") or Pinterest.convert_text_to_number(user_data.get("follower_count_text")),
            "follower_count_text": user_data.get("follower_count_text"),
            "following_count": user_data.get("following_count") or Pinterest.convert_text_to_number(user_data.get("following_count_text")),
            "following_count_text": user_data.get("following_count_text"),
            "pin_count": user_data.get("pin_count"),
            "board_count": user_data.get("board_count"),
            "about": user_data.get("about") or user_data.get("bio"),
            "profile_image": user_data.get("image_xlarge_url") or user_data.get("image_large_url"),
            "website_url": user_data.get("website_url"),
            "is_verified": user_data.get("is_verified", False),
            "data_source": user_data.get("extracted_from", "api"),
        }

        # Remove None values (same as before)
        profile_data = {k: v for k, v in profile_data.items() if v is not None}

        return json.dumps(profile_data, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pinterest scraper')
    parser.add_argument("username", help="Pinterest username")
    parser.add_argument("--browser", default="chrome", help="Browser (chrome/firefox)")
    parser.add_argument("--proxy", help="Proxy server")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--engine", default="auto",
                        choices=("auto", "curl_cffi", "seleniumbase_uc"),
                        help="scraping backend; 'auto' = curl_cffi first, "
                             "then a browser with UC mode (default)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="request / page load timeout in seconds")

    args = parser.parse_args()

    engine_order = None if args.engine == "auto" else (args.engine,)
    result = Pinterest.scrap(
        args.username,
        browser_name=args.browser,
        proxy=args.proxy,
        debug=args.debug,
        headed=args.headed,
        engine_order=engine_order,
        timeout=args.timeout,
    )

    print(result)

#last updated on 15th September, 2026

