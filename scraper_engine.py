"""
scraper_engine.py -- shared, extensible scraping layer for every script in this repo.
=====================================================================================

Every scraper script here (facebook.py, instagram.py, ...) used to hand-roll its
own Selenium setup.  This module centralises *how a page is fetched* so all
scripts share one mechanism, while each script's public API (CLI arguments,
function signatures, returned data) stays exactly the same.

Backends
--------
Each backend is a small class that knows how to turn a URL into HTML.
Two ship with the engine:

* ``curl_cffi``       -- plain HTTP requests with real-browser TLS/JA3
                         impersonation (fast, no browser process).  Default
                         first attempt.
* ``seleniumbase_uc`` -- a real, undetectable browser via SeleniumBase UC mode
                         (undetected-chromedriver).  Slower, used as fallback
                         when the HTTP attempt does not return usable data.

Adding another backend later (FlareSolverr, an API service, scrapy, ...) needs
no change in the scripts that use it::

    from scraper_engine import BaseFetchClient, FetchResult, register_client

    @register_client("flaresolverr")
    class FlareSolverrClient(BaseFetchClient):
        requires = ("flaresolverr",)

        @classmethod
        def is_available(cls):
            ...  # import the dependency here, return False on ImportError

        def fetch(self, url, *, timeout=DEFAULT_TIMEOUT, **opts):
            ...
            return FetchResult(url=url, backend=self.name, text=html)

    engine = ScrapingEngine(("curl_cffi", "flaresolverr", "seleniumbase_uc"))

Fallback semantics
------------------
``engine.fetch()`` walks the configured backends in order.  A backend is used
when it is available and its result passes ``validator`` (a callable returning
True when the response actually contains the data we need).  Anything that is
unavailable, errors out, or fails the validator is recorded in
``engine.last_errors`` and the next backend is tried.  If nothing qualifies,
``fetch`` returns ``None`` (or raises ``ScrapeFailedError`` when
``raise_on_error=True``).
"""

from __future__ import annotations

import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (Any, Callable, ClassVar, Dict, List, Optional, Sequence,
                    Tuple, Type, Union)

__all__ = [
    "FetchResult",
    "BaseFetchClient",
    "CurlCffiClient",
    "SeleniumBaseUCClient",
    "ScrapingEngine",
    "ScrapeFailedError",
    "register_client",
    "get_client_class",
    "available_backends",
    "fetch_html",
    "DEFAULT_TIMEOUT",
    "DEFAULT_ORDER",
]

DEFAULT_TIMEOUT = 30
#: Default backend priority used by every script unless it overrides it:
#: fast impersonated HTTP first, real browser (UC mode) as fallback.
DEFAULT_ORDER: Tuple[str, ...] = ("curl_cffi", "seleniumbase_uc")


class ScrapeFailedError(RuntimeError):
    """Raised by ``ScrapingEngine.fetch(..., raise_on_error=True)`` when no
    backend returned data that passed the validator."""


@dataclass
class FetchResult:
    """The outcome of one fetch attempt, backend-agnostic.

    Attributes:
        url:         URL that was requested.
        backend:     Name of the backend that produced this result.
        text:        Raw HTML (empty when the fetch failed).
        status_code: HTTP status when the backend knows one (the browser
                     backend reports 200 for a rendered page).
        final_url:   URL after redirects (login walls / checkpoints show up
                     here), when the backend can tell.
        headers:     Response headers, if available.
        elapsed:     Seconds the fetch took.
        driver:      Live browser handle when the backend kept the browser
                     open (see ``SeleniumBaseUCClient.fetch`` /
                     ``keep_browser_open``).  ``close()`` cleans it up.
        error:       Human readable failure reason; None on success.
    """

    url: str
    backend: str = ""
    text: str = ""
    status_code: Optional[int] = None
    final_url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    elapsed: float = 0.0
    driver: Any = None
    error: Optional[str] = None
    _soup: Any = field(default=None, init=False, repr=False, compare=False)

    @property
    def ok(self) -> bool:
        """True when the backend returned non-empty HTML without an error."""
        return self.error is None and bool(self.text)

    @property
    def soup(self):
        """Parsed HTML (BeautifulSoup).  Needs ``beautifulsoup4``."""
        if self._soup is None:
            try:
                from bs4 import BeautifulSoup
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "Parsing needs beautifulsoup4 - install dependencies from requirement.txt"
                ) from exc
            self._soup = BeautifulSoup(self.text or "", "html.parser")
        return self._soup

    def close(self) -> None:
        """Release any browser kept open by this result (safe to call twice)."""
        driver, self.driver = self.driver, None
        if driver is None:
            return
        for method in ("quit", "close"):
            try:
                getattr(driver, method)()
            except Exception:
                pass

    def __enter__(self) -> "FetchResult":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

class BaseFetchClient(ABC):
    """Interface every scraping backend implements.

    Subclass it, decorate with ``@register_client("name")`` and put the name in
    the backend order you pass to :class:`ScrapingEngine`.
    """

    #: unique backend name, set by ``@register_client(...)``
    name: ClassVar[str] = ""
    #: pip package names users must have installed (used in error hints)
    requires: ClassVar[tuple] = ()
    #: one line description (used in logs and diagnostics)
    description: ClassVar[str] = ""

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """True when this backend's dependencies are importable."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self, url: str, **opts: Any) -> FetchResult:
        """Fetch ``url`` and return a :class:`FetchResult`.  Never raises for
        page-level problems - report them via ``FetchResult.error`` instead."""
        raise NotImplementedError


_CLIENT_REGISTRY: Dict[str, Type[BaseFetchClient]] = {}


def register_client(name: str) -> Callable[[Type[BaseFetchClient]], Type[BaseFetchClient]]:
    """Class decorator: ``@register_client("my_backend")`` -> registers the
    class in the global backend registry so ``ScrapingEngine`` can find it."""
    def decorator(cls: Type[BaseFetchClient]) -> Type[BaseFetchClient]:
        cls.name = name
        _CLIENT_REGISTRY[name] = cls
        return cls
    return decorator


def get_client_class(name: str) -> Type[BaseFetchClient]:
    try:
        return _CLIENT_REGISTRY[name]
    except KeyError:
        raise ValueError(
            "Unknown scraping backend {!r}. Registered backends: {}".format(
                name, ", ".join(_CLIENT_REGISTRY) or "none")
        ) from None


def available_backends() -> List[str]:
    """Names of all registered backends whose dependencies are installed."""
    return [name for name, cls in _CLIENT_REGISTRY.items() if cls.is_available()]

@register_client("curl_cffi")
class CurlCffiClient(BaseFetchClient):
    """HTTP backend built on curl_cffi (curl-impersonate).

    Sends requests that look like a real Chrome browser on the TLS/JA3 and
    HTTP/2 fingerprint level - fast, and no browser process is started.
    """

    requires = ("curl_cffi",)
    description = "HTTP requests with real-browser TLS/JA3 impersonation (no browser process)"

    def __init__(self, impersonate: str = "chrome", proxies: Optional[dict] = None,
                 verify: bool = True):
        self.impersonate = impersonate
        self.proxies = proxies
        self.verify = verify

    @classmethod
    def is_available(cls) -> bool:
        try:
            import curl_cffi  # noqa: F401
        except ImportError:
            return False
        return True

    def fetch(self, url: str, *, timeout: float = DEFAULT_TIMEOUT,
              headers: Optional[dict] = None, impersonate: Optional[str] = None,
              retries: int = 0, **opts: Any) -> FetchResult:
        from curl_cffi import requests as curl_requests

        target = impersonate or self.impersonate
        start = time.monotonic()
        last_error: Optional[Exception] = None
        for attempt in range(max(1, retries + 1)):
            try:
                response = curl_requests.get(
                    url,
                    timeout=timeout,
                    headers=headers,
                    impersonate=target,
                    proxies=self.proxies,
                    verify=self.verify,
                    allow_redirects=True,
                )
                return FetchResult(
                    url=url,
                    backend=self.name,
                    text=response.text or "",
                    status_code=response.status_code,
                    final_url=str(response.url),
                    headers=dict(getattr(response, "headers", {}) or {}),
                    elapsed=time.monotonic() - start,
                )
            except Exception as exc:  # network errors, timeouts, TLS errors...
                last_error = exc
                if attempt < retries:
                    time.sleep(0.75 * (attempt + 1))
        return FetchResult(
            url=url,
            backend=self.name,
            elapsed=time.monotonic() - start,
            error="{}: {}".format(type(last_error).__name__, last_error)
            if last_error else "request failed",
        )

@register_client("seleniumbase_uc")
class SeleniumBaseUCClient(BaseFetchClient):
    """Real-browser backend using SeleniumBase in UC mode.

    UC mode = undetected-chromedriver behaviour built into SeleniumBase; it is
    the fallback for sites that block plain HTTP requests (login walls,
    checkpoint pages, JS heavy apps).
    """

    requires = ("seleniumbase",)
    description = "Real browser via SeleniumBase UC mode (undetected-chromedriver)"

    @classmethod
    def is_available(cls) -> bool:
        try:
            import seleniumbase  # noqa: F401
        except ImportError:
            return False
        return True

    # -- driver helpers -----------------------------------------------------

    @staticmethod
    def _display_available() -> bool:
        """True when a headed browser window can actually be shown."""
        if sys.platform in ("win32", "darwin", "cygwin"):
            return True
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))

    @staticmethod
    def _driver_kwargs(browser: str, headless: bool, uc: bool) -> List[dict]:
        """Candidate keyword sets for SeleniumBase's Driver, best first.

        UC mode only exists for Chromium browsers and needs the *new* headless
        mode (``headless2``); Firefox/Safari use the plain ``headless`` flag.
        """
        browser = (browser or "chrome").strip().lower() or "chrome"
        chromium = browser in ("chrome", "chromium", "edge")
        if chromium and uc:
            base = {"browser": "chrome" if browser == "chromium" else browser,
                    "uc": True}
            if headless:
                return [{**base, "headless2": True}, {**base, "headless": True}]
            return [dict(base)]
        return [{"browser": browser, "headless": headless}]

    def create_driver(self, browser: str = "chrome", headless: bool = True,
                      uc: bool = True):
        """Start a SeleniumBase Driver (UC for Chromium).  Raises on failure."""
        from seleniumbase import Driver

        candidates = self._driver_kwargs(browser, headless, uc)
        last_type_error: Optional[TypeError] = None
        for kwargs in candidates:
            try:
                return Driver(**kwargs)
            except TypeError as exc:  # kwarg unsupported by this SB version
                last_type_error = exc
                continue
        raise last_type_error if last_type_error else \
            RuntimeError("could not build the SeleniumBase driver")

    @staticmethod
    def _quit(driver: Any) -> None:
        if driver is None:
            return
        try:
            driver.quit()
        except Exception:
            pass

    # -- BaseFetchClient API --------------------------------------------------

    def fetch(self, url: str, *, timeout: float = DEFAULT_TIMEOUT,
              browser: str = "chrome", headless: bool = True, uc: bool = True,
              headed_fallback: Union[bool, str] = "auto", render_wait: float = 1.5,
              keep_browser_open: bool = False, retries: int = 0,
              **opts: Any) -> FetchResult:
        """Load ``url`` in a real browser and return the rendered HTML.

        Options:
            browser:           chrome | edge | firefox | safari (default chrome)
            headless:          try to run headless first (default True)
            uc:                use UC/undetected mode on Chromium browsers
            headed_fallback:   when the headless attempt fails, retry once in a
                               visible window ("auto" = only when a display
                               exists, False = never, True = always)
            render_wait:       extra seconds to let JS settle after page load
            keep_browser_open: keep the browser attached to the result for
                               further interaction (call ``result.close()``
                               when done).  By default it is closed as soon as
                               the HTML has been captured.
        """
        attempts: List[Tuple[bool, bool]] = []  # (headless?, uc?)
        if headless:
            attempts.append((True, uc))
            want_headed = (self._display_available() if headed_fallback == "auto"
                           else bool(headed_fallback))
            if want_headed:
                attempts.append((False, uc))
        else:
            attempts.append((False, uc))

        start = time.monotonic()
        last_error: Optional[Exception] = None
        for try_headless, try_uc in attempts:
            driver = None
            try:
                driver = self.create_driver(browser=browser, headless=try_headless,
                                            uc=try_uc)
                try:
                    driver.set_page_load_timeout(timeout)
                except Exception:
                    pass
                driver.get(url)
                if render_wait and render_wait > 0:
                    time.sleep(render_wait)
                html = driver.page_source or ""
                try:
                    final_url = driver.current_url or ""
                except Exception:
                    final_url = ""
                result = FetchResult(
                    url=url,
                    backend=self.name,
                    text=html,
                    status_code=200 if html else None,
                    final_url=final_url,
                    elapsed=time.monotonic() - start,
                    driver=driver if keep_browser_open else None,
                )
                if not keep_browser_open:
                    self._quit(driver)
                return result
            except Exception as exc:
                last_error = exc
                self._quit(driver)
        return FetchResult(
            url=url,
            backend=self.name,
            elapsed=time.monotonic() - start,
            error="{}: {}".format(type(last_error).__name__, last_error)
            if last_error else "browser could not load the page",
        )

ClientSpec = Union[str, Type[BaseFetchClient], BaseFetchClient]
Validator = Callable[[FetchResult], bool]


def _log(verbose: bool, message: str) -> None:
    if verbose:
        print("[scraper_engine] {}".format(message))


class ScrapingEngine:
    """Runs a URL through an ordered list of backends until one returns data
    that passes the caller's ``validator``.

    Args:
        clients: backend priority order (names, classes or instances).
                 Defaults to :data:`DEFAULT_ORDER` (curl_cffi first, then
                 SeleniumBase UC mode).
        timeout: default per-backend timeout in seconds.
        retries: default per-backend retry count for transient errors.
        verbose: print one-line progress / failure notes (handy for the CLI
                 scripts; set False for quiet, library style usage).
    """

    def __init__(self, clients: Optional[Sequence[ClientSpec]] = None,
                 timeout: float = DEFAULT_TIMEOUT, retries: int = 0,
                 verbose: bool = True):
        self.requested_clients: List[ClientSpec] = list(clients) if clients is not None else list(DEFAULT_ORDER)
        self.timeout = timeout
        self.retries = retries
        self.verbose = verbose
        self._instances: Dict[str, BaseFetchClient] = {}
        #: failure notes from the most recent fetch() call
        self.last_errors: List[str] = []

    # -- backend resolution ---------------------------------------------------

    def _coerce(self, spec: ClientSpec) -> BaseFetchClient:
        """Turn a name/class/instance into a ready-to-use client instance."""
        if isinstance(spec, BaseFetchClient):
            self._instances.setdefault(spec.name, spec)
            return spec
        if isinstance(spec, type) and issubclass(spec, BaseFetchClient):
            name = spec.name or spec.__name__.lower().replace("client", "")
            if name not in self._instances:
                self._instances[name] = spec()
            return self._instances[name]
        client_class = get_client_class(str(spec))
        if str(spec) not in self._instances:
            self._instances[str(spec)] = client_class()
        return self._instances[str(spec)]

    def backend_names(self) -> List[str]:
        try:
            return [self._coerce(spec).name for spec in self.requested_clients]
        except ValueError as exc:
            raise ValueError(exc) from None

    # -- the main entry point ---------------------------------------------------

    def fetch(self, url: str, *, order: Optional[Sequence[ClientSpec]] = None,
              validator: Optional[Validator] = None, timeout: Optional[float] = None,
              retries: Optional[int] = None, raise_on_error: bool = False,
              **client_opts: Any) -> Optional[FetchResult]:
        """Fetch ``url`` trying every backend in order.

        A backend result is accepted when the backend returned HTML and
        (optionally) ``validator(result)`` is True.  Rejected / failed results
        are closed (their browser, if any, is shut down) and the next backend
        is tried.  Extra keyword arguments are forwarded to every backend,
        which simply ignores the ones it does not know.

        Returns the first accepted :class:`FetchResult` or None.  Failure notes
        are collected in ``self.last_errors``.
        """
        chain = list(order) if order is not None else list(self.requested_clients)
        self.last_errors = []
        timeout = self.timeout if timeout is None else timeout
        retries = self.retries if retries is None else retries

        for spec in chain:
            try:
                client = self._coerce(spec)
            except ValueError as exc:
                self.last_errors.append(str(exc))
                _log(self.verbose, str(exc))
                continue

            if not client.is_available():
                message = "dependency missing (pip install {})".format(
                    " ".join(client.requires) or client.name)
                self.last_errors.append("{}: {}".format(client.name, message))
                _log(self.verbose, "skipping {!r}: {}".format(client.name, message))
                continue

            try:
                result = client.fetch(url, timeout=timeout, retries=retries, **client_opts)
            except Exception as exc:  # backend misbehaved instead of reporting
                result = FetchResult(url=url, backend=client.name,
                                     error="{}: {}".format(type(exc).__name__, exc))

            accepted = result.ok
            if accepted and validator is not None:
                try:
                    accepted = bool(validator(result))
                except Exception as exc:
                    accepted = False
                    result.error = "validator raised {}: {}".format(type(exc).__name__, exc)

            if accepted:
                _log(self.verbose, "fetched via {!r} in {:.2f}s".format(result.backend, result.elapsed))
                return result

            reason = result.error or ("validator rejected the response" if result.ok
                                      else "empty response")
            self.last_errors.append("{}: {}".format(client.name, reason))
            _log(self.verbose, "{}: {} -- trying next backend".format(client.name, reason))
            result.close()

        if not self.last_errors:
            self.last_errors.append("no backends configured")
        if raise_on_error:
            raise ScrapeFailedError("; ".join(self.last_errors))
        _log(self.verbose, "all backends failed: {}".format("; ".join(self.last_errors)))
        return None


#: engine with the default backend order, reused by the ``fetch_html`` helper
default_engine = ScrapingEngine()


def fetch_html(url: str, **options: Any) -> Optional[FetchResult]:
    """One-liner helper using the module level default engine."""
    return default_engine.fetch(url, **options)





