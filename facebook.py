"""Facebook profile scraper.

Public usage (unchanged from previous versions)::

    python facebook.py <username> [--browser chrome|firefox]

Under the hood the scraping is delegated to the shared ``scraper_engine``: it
first tries a fast ``curl_cffi`` request (browser-impersonated TLS), and only
falls back to a real browser (SeleniumBase UC mode / undetected-chromedriver)
when that does not return usable profile data.

New optional flags (additions only, nothing removed):
    --engine auto|curl_cffi|seleniumbase_uc   pick the backend (default: auto)
    --headed                                  run the fallback browser non-headless
    --timeout N                               request / page load timeout (seconds)
    --json                                    print the result as JSON
"""

try:
    import argparse
    import html as html_module
    import json
    import re

    from scraper_engine import FetchResult, ScrapingEngine
except ModuleNotFoundError:
    print("Please download dependecies from requirement.txt")
    exit()
except Exception as ex:
    print(ex)


class Facebook:
    """Scrapes public Facebook profile data from m.facebook.com."""

    BASE_URL = "https://m.facebook.com/{}"

    #: Backend priority: fast impersonated HTTP first, real browser as fallback.
    ENGINE_ORDER = ("curl_cffi", "seleniumbase_uc")

    #: Title/name fragments that mean "we got a login/error page, not a profile".
    _INVALID_NAME_FRAGMENTS = (
        "log in", "log into", "login", "sign up", "sign in", "join facebook",
        "checkpoint", "not found", "not available", "content isn't available",
    )

    # Modern www.facebook.com pages hide the profile data inside embedded
    # <script type="application/json"> payloads (the visible DOM is just a
    # React shell), so they are walked as a second extraction tier.  Structure
    # verified against naushad_alam_fb.html:
    #   {"field_type": "work", "title": {"text": "Branch manager at X"},
    #    "list_item_groups": [{"list_items": [{"text": {"text": "<date>"}},
    #                                         {"text": {"text": "<city>"}}]}]}
    #   {"field_section_type": "college"|"secondary_school", "title": {"text": "University"}}
    #   {"field_type": "null_state", "title": {"text": "No schools/universities to show"}}
    _JSON_SCRIPT_RE = re.compile(
        r"<script[^>]*type=[\"']application/json[\"'][^>]*>(.*?)</script>",
        re.IGNORECASE | re.DOTALL)
    _DATE_TEXT_RE = re.compile(
        r"^\s*(?:\d{1,2}\s+\w+\s+\d{4}|\w{3,9}\s+\d{4})\s*[-\u2013\u2014]\s*"
        r"(?:\d{1,2}\s+\w+\s+\d{4}|\w{3,9}\s+\d{4}|present)\s*$",
        re.IGNORECASE)
    _CITY_TEXT_RE = re.compile(
        r"^\s*[A-Z][\w .,'()&-]+\s*,\s*[A-Z][\w .,'()&-]+\s*$")
    _EDUCATION_FIELD_TYPES = frozenset({
        "education", "college", "university", "secondary_school",
        "high_school", "school", "studied_at",
    })


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
    def _extract_name(title):
        """Profile name out of a page title like ``Sajid Shaikh | Facebook``.

        Returns '' when the title belongs to a login/error page.
        """
        title = html_module.unescape(re.sub(r"\s+", " ", (title or "").strip()))
        if not title:
            return ""
        if "|" in title:
            name = title.split("|", 1)[0].strip()
        elif re.search(r"\s[-\u2013\u2014]\s", title):
            name = re.split(r"\s[-\u2013\u2014]\s", title, maxsplit=1)[0].strip()
        else:
            name = title
        # modern www pages: "Name (@handle) • Facebook, Connect with friends"
        name = re.split(r"\s*[\u2022\u00b7]\s*", name, maxsplit=1)[0].strip()
        name = re.sub(r",\s*Connect with friends\b.*$", "", name,
                      flags=re.IGNORECASE).strip()
        lowered = name.lower()
        if not lowered or lowered in ("facebook", "welcome to facebook", "facebook login"):
            return ""
        for fragment in Facebook._INVALID_NAME_FRAGMENTS:
            if fragment in lowered:
                return ""
        return name

    @staticmethod
    def _page_name(html):
        """Name from the page's <title> (or og:title); '' if not a profile page."""
        html = html or ""
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        name = Facebook._extract_name(match.group(1) if match else "")
        og = re.search(
            r"<meta[^>]+property=[\"']og:title[\"'][^>]*content=[\"']([^\"']+)[\"']",
            html, re.IGNORECASE)
        if not og:
            og = re.search(
                r"<meta[^>]+content=[\"']([^\"']+)[\"'][^>]*property=[\"']og:title[\"']",
                html, re.IGNORECASE)
        og_name = Facebook._extract_name(og.group(1)) if og else ""
        # og:title is the clean display name on modern pages ("Sajid Shaikh"
        # while <title> is "Sajid Shaikh (@handle) • Facebook, ..."), so prefer
        # it when it clearly belongs to the same profile as the <title> name.
        if og_name and (not name or name.startswith(og_name)):
            return og_name
        return name

    @staticmethod
    def _looks_like_profile(result: FetchResult) -> bool:
        """Validator handed to scraper_engine: True when the response really
        holds profile data (rejects login walls, checkpoints, error pages)."""
        html = result.text or ""
        if not html or "facebook" not in html.lower():
            return False
        final_url = (result.final_url or result.url or "").lower()
        if re.search(r"/(login|checkpoint|recover)(/|\?|$)", final_url):
            return False
        return bool(Facebook._page_name(html))

    @staticmethod
    def _payload_text(value):
        """Payload values are plain strings or ``{"text": "..."}`` dicts."""
        if isinstance(value, str):
            return value.strip() or None
        if isinstance(value, dict) and isinstance(value.get("text"), str):
            return value["text"].strip() or None
        return None

    @staticmethod
    def _iter_payload_dicts(node):
        """Depth-first walk over every dict inside a parsed payload."""
        if isinstance(node, dict):
            yield node
            for value in node.values():
                yield from Facebook._iter_payload_dicts(value)
        elif isinstance(node, list):
            for value in node:
                yield from Facebook._iter_payload_dicts(value)

    @classmethod
    def _payload_profile_data(cls, html):
        """Extract profile fields from the embedded JSON payloads used by the
        modern www.facebook.com pages (their rendered DOM is an empty React
        shell, so the old DOM selectors find nothing there).

        Returns {work, education, education_placeholder, city}.
        """
        work_entries, education_entries = [], []
        education_placeholder, city = "", ""
        seen_work, seen_education = set(), set()

        for match in Facebook._JSON_SCRIPT_RE.finditer(html or ""):
            body = match.group(1)
            if "\"field_type\"" not in body and "\"field_section_type\"" not in body:
                continue
            try:
                data = json.loads(body)
            except Exception:
                continue

            for node in Facebook._iter_payload_dicts(data):
                field_type = node.get("field_type")
                if field_type == "null_state":
                    text = (Facebook._payload_text(node.get("title"))
                            or Facebook._payload_text(node.get("subtitle"))
                            or Facebook._payload_text(node.get("text")))
                    if text and not education_placeholder \
                            and re.search(r"school|universit", text, re.I):
                        education_placeholder = text
                    continue
                if field_type != "work" and field_type not in Facebook._EDUCATION_FIELD_TYPES:
                    continue
                title = Facebook._payload_text(node.get("title"))
                if not title or len(title) > 120:
                    continue

                items = []
                for group in node.get("list_item_groups") or []:
                    for item in (group or {}).get("list_items") or []:
                        if isinstance(item, dict):
                            text = Facebook._payload_text(item.get("text"))
                            if text and text not in items:
                                items.append(text)
                dates = [i for i in items if Facebook._DATE_TEXT_RE.match(i)]
                places = [i for i in items
                          if Facebook._CITY_TEXT_RE.match(i) and i not in dates]

                if field_type == "work":
                    if title in seen_work:
                        continue
                    seen_work.add(title)
                    bucket = work_entries
                else:
                    if title in seen_education:
                        continue
                    seen_education.add(title)
                    bucket = education_entries

                extras = ", ".join(dates + places)
                bucket.append("{} ({})".format(title, extras) if extras else title)
                if places and not city:
                    city = places[0]

        return {
            "work": "; ".join(work_entries),
            "education": "; ".join(education_entries),
            "education_placeholder": education_placeholder,
            "city": city,
        }

    @staticmethod
    def _extract_profile(result: FetchResult) -> dict:
        """Parse the profile dict out of a FetchResult.

        Two extraction tiers, so both page formats work:
        1. rendered DOM + og: meta tags (old m.facebook.com / mbasic pages),
        2. embedded JSON payloads (modern www.facebook.com React pages).

        Returns the old keys {name, profile_image, current_city, Education}
        plus the new "work" key (empty when the page has no such data).
        """

        soup = result.soup
        html = result.text or ""
        name = Facebook._page_name(html)

        profile_image = ""
        og_image = soup.find("meta", attrs={"property": "og:image"})
        if og_image and og_image.get("content"):
            profile_image = og_image["content"].strip()
        if not profile_image:
            image_tag = soup.select_one("img.profpic.img") \
                or soup.select_one("img[src*='scontent']")
            if image_tag and image_tag.get("src"):
                profile_image = image_tag["src"].strip()

        # same selector the old Selenium version used: every <h4> on the page
        cities = []
        for tag in soup.find_all("h4"):
            text = tag.get_text(" ", strip=True)
            if text and text not in cities:
                cities.append(text)
        current_city = ", ".join(cities)

        # same selector the old Selenium version used
        education = ""
        education_tag = soup.select_one(".fbProfileEditExperiences")
        if education_tag is None:
            education_tag = soup.select_one("[id^='education']")
        if education_tag is not None:
            education = education_tag.get_text(" ", strip=True)

        # tier 2: embedded JSON payloads (modern www.facebook.com pages)
        payload = Facebook._payload_profile_data(html)
        if not current_city and payload["city"]:
            current_city = payload["city"]
        if not education:
            education = payload["education"] or payload["education_placeholder"]

        return {
            "name": name,
            "profile_image": profile_image,
            "current_city": current_city,
            "Education": education,
            "work": payload["work"],
        }

    # ------------------------------------------------------------------ #
    # public API                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def scrap(username, browser_name="chrome", **options):
        """Scrape a public Facebook profile.

        Args:
            username:     profile username (the path after m.facebook.com/).
            browser_name: browser used by the browser fallback backend
                          ("chrome" or "firefox") - same meaning as before.
            options:      optional extras, all of them optional:
                          engine_order, headless, timeout, verbose.

        Returns the profile dict {name, profile_image, current_city, Education,
        work} or None when the profile could not be scraped.
        """
        username = str(username or "").strip().lstrip("/")
        if not username:
            print("Please provide a valid username")
            return None

        engine_order = options.pop("engine_order", None) or Facebook.ENGINE_ORDER
        headless = options.pop("headless", True)
        timeout = options.pop("timeout", 30)
        verbose = options.pop("verbose", True)

        url = Facebook.BASE_URL.format(username)
        engine = ScrapingEngine(engine_order, timeout=timeout, verbose=verbose)
        # curl_cffi ignores the browser specific kwargs; the SeleniumBase
        # backend picks them up (browser choice, headless/headed, UC mode).
        result = engine.fetch(
            url,
            validator=Facebook._looks_like_profile,
            browser=browser_name or "chrome",
            headless=headless,
        )
        if result is None:
            if verbose:
                print("Could not scrape profile for '{}': {}".format(
                    username, "; ".join(engine.last_errors)))
            return None
        with result:
            return Facebook._extract_profile(result)


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
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON instead of a Python dict")
    args = parser.parse_args()

    engine_order = None if args.engine == "auto" else (args.engine,)
    profile_data = Facebook.scrap(
        args.username,
        args.browser,
        engine_order=engine_order,
        headless=not args.headed,
        timeout=args.timeout,
    )
    if args.json and profile_data is not None:
        print(json.dumps(profile_data, ensure_ascii=False, indent=2))
    else:
        print(profile_data)

#last updated on 13th September, 2026

