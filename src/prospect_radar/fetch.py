"""Fetching a homepage politely (robots.txt, one request per site), or from local fixtures."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass
from pathlib import Path

USER_AGENT = "prospect-radar/0.1 (+https://github.com/ralcaraz6/prospect-radar)"


@dataclass
class Page:
    url: str          # final URL after redirects
    html: str
    seconds: float    # time to first full response
    bytes: int


class FetchError(RuntimeError):
    pass


class WebFetcher:
    def __init__(self, timeout: float = 15, delay: float = 1.0):
        self.timeout, self.delay = timeout, delay

    def _allowed(self, url: str) -> bool:
        parts = urllib.parse.urlsplit(url)
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
        try:
            rp.read()
        except Exception:
            return True  # no readable robots.txt: allowed
        return rp.can_fetch(USER_AGENT, url)

    def get(self, url: str) -> Page:
        if "://" not in url:
            url = "https://" + url
        if not self._allowed(url):
            raise FetchError("robots.txt disallows it")
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read()
                final = resp.geturl()
                charset = resp.headers.get_content_charset() or "utf-8"
        except Exception as e:
            raise FetchError(str(e)) from e
        elapsed = time.monotonic() - start
        time.sleep(self.delay)
        return Page(final, body.decode(charset, errors="replace"), elapsed, len(body))


class FixtureFetcher:
    """Serves made-up sites from sample/sites for --demo and tests."""

    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.meta = json.loads((self.folder / "meta.json").read_text())

    def get(self, url: str) -> Page:
        host = urllib.parse.urlsplit(url if "://" in url else "https://" + url).netloc
        m = self.meta.get(host)
        if m is None:
            raise FetchError("no fixture for this host")
        html = (self.folder / m["file"]).read_text()
        return Page(m.get("final_url", url), html, m.get("seconds", 0.8), len(html.encode()))
