import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prospect_radar.checks import run_checks, upside  # noqa: E402
from prospect_radar.cli import audit_all, load_prospects, main  # noqa: E402
from prospect_radar.fetch import FixtureFetcher, Page  # noqa: E402
from prospect_radar.report import to_csv  # noqa: E402

TODAY = date(2026, 11, 6)
SITES = FixtureFetcher(ROOT / "sample" / "sites")


def failed(page):
    return {f.id for f in run_checks(page, TODAY) if not f.passed}


class CheckTests(unittest.TestCase):
    def test_outdated_site_fails_the_big_ones(self):
        ids = failed(SITES.get("https://old-bakery.test"))
        self.assertTrue({"https", "speed", "mobile", "analytics", "contact", "fresh"} <= ids)

    def test_good_site_passes_everything(self):
        self.assertEqual(failed(SITES.get("https://northlight-studio.test")), set())

    def test_two_h1_and_missing_description(self):
        ids = failed(SITES.get("https://riverside-dental.test"))
        self.assertIn("h1", ids)
        self.assertIn("description", ids)
        self.assertNotIn("analytics", ids)

    def test_copyright_range_uses_latest_year(self):
        page = Page("https://x.test/", "<html><footer>&copy; 2015-2026 X</footer></html>", 0.5, 100)
        self.assertNotIn("fresh", failed(page))

    def test_whatsapp_counts_as_quick_contact(self):
        page = Page("https://x.test/", '<a href="https://wa.me/000">Chat</a>', 0.5, 100)
        self.assertNotIn("quick_contact", failed(page))

    def test_upside_is_bounded(self):
        for host in ("old-bakery.test", "riverside-dental.test", "northlight-studio.test"):
            score = upside(run_checks(SITES.get("https://" + host), TODAY))
            self.assertTrue(0 <= score <= 100)


class ReportTests(unittest.TestCase):
    def test_ranking_and_errors(self):
        audits = audit_all(load_prospects(ROOT / "sample" / "prospects.csv"), SITES, TODAY)
        rows = to_csv(audits).splitlines()
        self.assertTrue(rows[1].startswith("Old Town Bakery"))
        self.assertIn("no fixture", rows[-1])

    def test_demo_runs(self):
        self.assertEqual(main(["--demo"]), 0)


if __name__ == "__main__":
    unittest.main()
