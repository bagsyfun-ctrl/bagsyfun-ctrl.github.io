"""Notify IndexNow participants when official BAGSY pages change."""

from __future__ import annotations

import json
import urllib.request


HOST = "bagsy.fun"
KEY = "3da2045520cb4060b11fac978586a2d0"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
URLS = [
    f"https://{HOST}/",
    f"https://{HOST}/status.html",
    f"https://{HOST}/share.html",
    f"https://{HOST}/community.html",
    f"https://{HOST}/project-facts.json",
    f"https://{HOST}/sitemap.xml",
]


def payload() -> dict[str, object]:
    return {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URLS,
    }


def submit() -> int:
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload()).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status


if __name__ == "__main__":
    status = submit()
    if status not in {200, 202}:
        raise SystemExit(f"IndexNow returned HTTP {status}")
    print(f"IndexNow accepted {len(URLS)} official URLs (HTTP {status}).")
