import time
import urllib.robotparser
from typing import Any
from urllib.parse import urlparse

import requests  # type: ignore

USER_AGENT = (
    "CosmicFoundryBot/0.0.0 (https://github.com/cosmic-foundry/cosmic-observables)"
)


class HTTPClient:
    """
    An HTTP client that respects robots.txt and identifies itself via User-Agent.
    """

    def __init__(self, user_agent: str = USER_AGENT):
        self.user_agent = user_agent
        self.robot_parsers: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.last_request_time: dict[str, float] = {}

    def _get_robot_parser(self, url: str) -> urllib.robotparser.RobotFileParser:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if base_url not in self.robot_parsers:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            try:
                rp.read()
            except Exception:
                # If we can't read robots.txt, assume it's okay but be conservative
                pass
            self.robot_parsers[base_url] = rp

        return self.robot_parsers[base_url]

    def _respect_crawl_delay(self, url: str) -> None:
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
        rp = self._get_robot_parser(url)
        if not rp.can_fetch(self.user_agent, url):
            raise PermissionError(f"Robots.txt disallows fetching {url}")

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
        # Note: robots.txt standard usually covers GET, but we'll check for consistency
        rp = self._get_robot_parser(url)
        if not rp.can_fetch(self.user_agent, url):
            raise PermissionError(f"Robots.txt disallows fetching/posting to {url}")

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
