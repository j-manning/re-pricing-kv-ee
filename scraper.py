"""
KV.ee pricing scraper (Estonia) — uses Playwright.

KV.ee (Baltics Classifieds Group) returns 403 to plain requests.
Playwright with a real browser context loads the page correctly.

Source: https://www.kv.ee/liitumine

Individual seller pricing (publicly listed):
  - Sales listing:  €44.99 per listing
  - Rental listing: €24.99 per listing

Agency packages: contact sales (pricing not publicly listed).

fee_period = per_listing
hybrid_note = "BCG platform; City24.ee included in Pro agency package. Agency pricing: contact sales."
"""

import re
from datetime import date

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from config import PLATFORM, MARKET, CURRENCY, PRICING_URL, CSV_PATH
from storage import append_rows

PLAYWRIGHT_TIMEOUT = 30_000

KNOWN_TIERS = [
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


def fetch_page_text(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="et-EE",
        )
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
        except PlaywrightTimeout:
            page.goto(url, wait_until="domcontentloaded", timeout=PLAYWRIGHT_TIMEOUT)

        try:
            page.wait_for_selector("main, .pricing, .price", timeout=10_000)
        except PlaywrightTimeout:
            pass

        text = page.inner_text("body")
        browser.close()
    return text


def parse_fees(text: str) -> list[dict]:
    today = date.today().isoformat()

    verified_sales  = bool(re.search(r"44[.,]99", text))
    verified_rental = bool(re.search(r"24[.,]99", text))
    verified = verified_sales and verified_rental

    if verified:
        print("Confirmed €44.99 and €24.99 from live page.")
    else:
        print(
            f"WARNING: could not confirm prices "
            f"(sales={verified_sales}, rental={verified_rental}). Using last-known values."
        )

    rows = []
    for tier in KNOWN_TIERS:
        note = tier["hybrid_note"]
        if not verified:
            note += " [UNVERIFIED — page content changed]"
        rows.append({
            "scrape_date":    today,
            "platform":       PLATFORM,
            "market":         MARKET,
            "currency":       CURRENCY,
            "tier_name":      tier["tier_name"],
            "fee_amount":     tier["fee_amount"],
            "fee_period":     "per_listing",
            "prop_value_min": "",
            "prop_value_max": "",
            "location_note":  tier["location_note"],
            "hybrid_note":    note,
        })
    return rows


def main():
    print(f"Fetching KV.ee pricing via Playwright: {PRICING_URL}")
    try:
        text = fetch_page_text(PRICING_URL)
        rows = parse_fees(text)
    except Exception as e:
        print(f"WARNING: Playwright fetch failed ({e}). Using last-known values.")
        today = date.today().isoformat()
        rows = [
            {
                "scrape_date":    today,
                "platform":       PLATFORM,
                "market":         MARKET,
                "currency":       CURRENCY,
                "tier_name":      tier["tier_name"],
                "fee_amount":     tier["fee_amount"],
                "fee_period":     "per_listing",
                "prop_value_min": "",
                "prop_value_max": "",
                "location_note":  tier["location_note"],
                "hybrid_note":    tier["hybrid_note"] + " [UNVERIFIED — fetch failed]",
            }
            for tier in KNOWN_TIERS
        ]
    append_rows(CSV_PATH, rows)


if __name__ == "__main__":
    main()
