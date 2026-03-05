"""
KV.ee pricing scraper (Estonia).

Source: https://www.kv.ee/liitumine

KV.ee is part of the BCG (Baltics Classifieds Group) platform.
City24.ee is included in the Pro agency package.

Individual seller pricing (publicly listed):
  - Sales listing:  €44.99 per listing
  - Rental listing: €24.99 per listing

Agency packages: contact sales (pricing not publicly listed).

fee_period = per_listing
"""

import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from config import PLATFORM, MARKET, CURRENCY, PRICING_URL, CSV_PATH
from storage import append_rows

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "et,en;q=0.9",
}

KNOWN_INDIVIDUAL_TIERS = [
    {
        "tier_name": "Individual — Sales listing",
        "fee_amount": 44.99,
        "location_note": "individual seller",
        "hybrid_note": "BCG platform; City24.ee included in Pro agency package. Agency pricing: contact sales.",
    },
    {
        "tier_name": "Individual — Rental listing",
        "fee_amount": 24.99,
        "location_note": "individual seller",
        "hybrid_note": "BCG platform; City24.ee included in Pro agency package. Agency pricing: contact sales.",
    },
]


def fetch_page(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def parse_fees(soup: BeautifulSoup) -> list[dict]:
    today = date.today().isoformat()
    text = soup.get_text(" ", strip=True)

    # Sanity check: confirm known individual prices are present
    verified_sales = "44.99" in text or "44,99" in text
    verified_rental = "24.99" in text or "24,99" in text
    verified = verified_sales and verified_rental

    rows = []
    for tier in KNOWN_INDIVIDUAL_TIERS:
        note = tier["hybrid_note"]
        if not verified:
            note += " [UNVERIFIED — page structure changed]"
        rows.append({
            "scrape_date": today,
            "platform": PLATFORM,
            "market": MARKET,
            "currency": CURRENCY,
            "tier_name": tier["tier_name"],
            "fee_amount": tier["fee_amount"],
            "fee_period": "per_listing",
            "prop_value_min": "",
            "prop_value_max": "",
            "location_note": tier["location_note"],
            "hybrid_note": note,
        })

    if verified:
        print("Confirmed individual seller prices from live page.")
    else:
        print("WARNING: Could not confirm prices. Using last-known values.")

    return rows


def main():
    print(f"Fetching KV.ee pricing from {PRICING_URL}")
    soup = fetch_page(PRICING_URL)
    rows = parse_fees(soup)
    append_rows(CSV_PATH, rows)


if __name__ == "__main__":
    main()
