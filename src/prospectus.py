"""Download an IPO's abridged prospectus from SEBI's public-issues listing and save its text.

Usage: python3 src/prospectus.py moneyview swastika ...   (keys are fragments of the SEBI filing URL)
The abridged prospectus (~10-15 pages) is the same document brokers show retail investors and is
published before bids open. ponytail: only the latest listing page is read, add paging for older IPOs.
"""
import re
import sys
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/prospectus"
LISTING = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=15&smid=11"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) ipo-agent personal research"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()


def find_filing(key, listing_html):
    links = re.findall(r'href="(https://www\.sebi\.gov\.in/filings/public-issues/[^"]+)"', listing_html)
    hits = [l for l in links if key in l and not re.search(r"corrigendum|addendum", l)]
    return next((l for l in hits if "-rhp_" in l), next((l for l in hits if "prospectus" in l), hits[0] if hits else None))


def fetch(key, listing_html):
    page = find_filing(key, listing_html)
    if not page:
        return None
    pdf_url = re.search(r'https?://[^"\' ]+\.pdf', get(page).decode()).group()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{key}.pdf").write_bytes(get(pdf_url))
    text = "\n\f".join((p.extract_text() or "") for p in PdfReader(OUT / f"{key}.pdf").pages)
    (OUT / f"{key}.txt").write_text(text)
    return page, len(text)


if __name__ == "__main__":
    listing = get(LISTING).decode()
    for key in sys.argv[1:]:
        try:
            print(key, fetch(key, listing) or "NOT FOUND on latest listing page")
        except Exception as e:
            print(key, "ERROR", e)
