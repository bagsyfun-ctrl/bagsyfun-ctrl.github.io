import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MINT = "GUAFAP1wtFK2R79y5mCpumZA4yR2R9bNrZs7yB2epump"


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


class SiteFunnelTests(unittest.TestCase):
    def test_share_hub_has_verified_market_route(self):
        html = (ROOT / "share.html").read_text(encoding="utf-8")
        parser = LinkCollector()
        parser.feed(html)
        self.assertIn(MINT, html)
        self.assertTrue(any(link.startswith("https://pump.fun/coin/") for link in parser.links))
        self.assertIn("status.json", html)
        self.assertIn("twitter.com/intent/tweet", html)
        self.assertIn("t.me/share/url", html)

    def test_homepage_and_machine_facts_link_share_hub(self):
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        facts = json.loads((ROOT / "project-facts.json").read_text(encoding="utf-8"))
        self.assertIn("share.html", homepage)
        self.assertEqual(facts["officialLinks"]["shareHub"], "https://bagsy.fun/share.html")

    def test_share_art_exists_and_is_nontrivial(self):
        asset = ROOT / "BAGSY-build-public.png"
        self.assertTrue(asset.exists())
        self.assertGreater(asset.stat().st_size, 100_000)


if __name__ == "__main__":
    unittest.main()
