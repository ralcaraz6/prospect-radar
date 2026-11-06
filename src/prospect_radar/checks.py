"""Marketing checks on a homepage. Each failed check is an improvement I can offer.

Deliberately NOT here: security probing of any kind, and collecting emails, phone
numbers or names. Only the presence of a contact route is checked, never its content.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser

from .fetch import Page


class _Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self._in_title = "", False
        self.meta: dict[str, str] = {}
        self.h1 = 0
        self.imgs = self.imgs_no_alt = 0
        self.forms = 0
        self.hrefs: list[str] = []
        self.scripts: list[str] = []
        self.ld_json = False
        self.lang = ""
        self.icon = False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img":
            self.imgs += 1
            if not a.get("alt", "").strip():
                self.imgs_no_alt += 1
        elif tag == "form":
            self.forms += 1
        elif tag == "a":
            self.hrefs.append(a.get("href", "").lower())
        elif tag == "script":
            self.scripts.append(a.get("src", "").lower())
            if a.get("type", "").lower() == "application/ld+json":
                self.ld_json = True
        elif tag == "link" and "icon" in a.get("rel", "").lower():
            self.icon = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


@dataclass
class Finding:
    id: str
    passed: bool
    weight: int       # how much fixing it is worth to the business, 1-15
    message: str      # written for the business owner, not for a developer


def run_checks(page: Page, today: date | None = None) -> list[Finding]:
    s = _Scan()
    s.feed(page.html)
    html = page.html.lower()
    today = today or date.today()
    src = " ".join(s.scripts) + " " + html
    title = s.title.strip()
    desc = s.meta.get("description", "").strip()
    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(\d{4})", html)]

    has_analytics = any(k in src for k in ("googletagmanager.com/gtag/js", "googletagmanager.com/gtm.js",
                                           "google-analytics.com", "plausible.io", "matomo"))
    has_pixel = "connect.facebook.net" in src or "fbq(" in html
    contact_link = any(re.search(r"contact|contacto|kontakt|contatti", h) for h in s.hrefs)
    quick_route = any(h.startswith(("tel:", "mailto:")) or "wa.me/" in h or "api.whatsapp.com" in h for h in s.hrefs)

    F = Finding
    return [
        F("https", page.url.startswith("https://"), 10, "The site does not load over HTTPS, so browsers mark it 'Not secure'."),
        F("speed", page.seconds <= 2.5, 12, f"The homepage took {page.seconds:.1f} s to load; visitors start leaving after about 3 s."),
        F("weight", page.bytes <= 2_000_000, 5, f"The homepage HTML alone is {page.bytes / 1e6:.1f} MB."),
        F("mobile", "viewport" in s.meta, 15, "No mobile viewport: the site is not built for phones."),
        F("title", 10 <= len(title) <= 65, 6, "The page title is missing or the wrong length for Google results."),
        F("description", 50 <= len(desc) <= 160, 6, "No usable meta description, so Google writes its own snippet."),
        F("h1", s.h1 == 1, 4, f"The page has {s.h1} main headings (H1); it should have exactly one."),
        F("analytics", has_analytics, 12, "No web analytics found: the owner cannot see where visitors come from."),
        F("ad_pixel", has_pixel, 5, "No ad pixel: paid social campaigns cannot be measured or retargeted."),
        F("contact", s.forms > 0 or contact_link, 10, "No contact form or contact page linked from the homepage."),
        F("quick_contact", quick_route, 6, "No one-tap phone, email or WhatsApp link for mobile visitors."),
        F("structured_data", s.ld_json, 4, "No structured data, so Google cannot show rich business details."),
        F("social_preview", "og:image" in s.meta, 3, "No social preview image when the site is shared."),
        F("fresh", not years or max(years) >= today.year - 1, 5,
          f"The footer still says {max(years) if years else ''}: the site looks abandoned."),
        F("alt_text", s.imgs == 0 or s.imgs_no_alt / s.imgs <= 0.2, 3,
          f"{s.imgs_no_alt} of {s.imgs} images have no alt text (accessibility and image search)."),
        F("lang", bool(s.lang), 2, "The page does not declare its language."),
        F("favicon", s.icon, 2, "No favicon: the tab and bookmarks show a blank icon."),
    ]


def upside(findings: list[Finding]) -> int:
    """0-100: share of the total weight that failed. Higher = more to sell."""
    total = sum(f.weight for f in findings)
    return round(100 * sum(f.weight for f in findings if not f.passed) / total)
