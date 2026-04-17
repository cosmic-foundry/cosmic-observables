import time
import urllib.robotparser
from typing import Any
from urllib.parse import urlparse

import requests  # type: ignore

BOT_UA = "CosmicFoundryBot/0.0.0 (https://github.com/cosmic-foundry/cosmic-observables)"
# A standard browser-like UA for research/one-time ingestion
STANDARD_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class HTTPClient:
    """
    An HTTP client that supports both transparent bot identification and
    standard user identification for research purposes.
    """

    def __init__(self, user_agent: str = BOT_UA, respect_robots: bool = True):
        self.user_agent = user_agent
        self.respect_robots = respect_robots
        self.robot_parsers: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.last_request_time: dict[str, float] = {}

    def _get_robot_parser(self, url: str) -> urllib.robotparser.RobotFileParser:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if base_url not in self.robot_parsers:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{base_url}/robots.txt"
            rp.set_url(robots_url)
            try:
                # Use standard UA to read robots.txt to avoid 403s on the policy
                headers = {"User-Agent": STANDARD_UA}
                r = requests.get(robots_url, headers=headers, timeout=10)
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
            except Exception:
                pass
            self.robot_parsers[base_url] = rp

        return self.robot_parsers[base_url]

    def _respect_crawl_delay(self, url: str) -> None:
        if not self.respect_robots:
            return

        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        rp = self._get_robot_parser(url)
        delay_val = rp.crawl_delay(self.user_agent)
        if delay_val:
            delay = float(delay_val)
            last_time = self.last_request_time.get(base_url, 0.0)
            elapsed = time.time() - last_time
            if elapsed < delay:
                time.sleep(delay - elapsed)

    def get(
        self, url: str, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> requests.Response:
        if self.respect_robots:
            rp = self._get_robot_parser(url)
            if not rp.can_fetch(self.user_agent, url):
                raise PermissionError(f"Robots.txt disallows bot fetching of {url}")
            self._respect_crawl_delay(url)

        actual_headers = {"User-Agent": self.user_agent}
        if headers:
            actual_headers.update(headers)

        response = requests.get(url, headers=actual_headers, **kwargs)
        self.last_request_time[f"{urlparse(url).scheme}://{urlparse(url).netloc}"] = (
            time.time()
        )
        return response

    def post(
        self,
        url: str,
        data: Any = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        if self.respect_robots:
            rp = self._get_robot_parser(url)
            if not rp.can_fetch(self.user_agent, url):
                raise PermissionError(f"Robots.txt disallows bot posting to {url}")
            self._respect_crawl_delay(url)

        actual_headers = {"User-Agent": self.user_agent}
        if headers:
            actual_headers.update(headers)

        response = requests.post(
            url, data=data, json=json, headers=actual_headers, **kwargs
        )
        self.last_request_time[f"{urlparse(url).scheme}://{urlparse(url).netloc}"] = (
            time.time()
        )
        return response
