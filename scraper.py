"""
KV.ee pricing scraper (Estonia) — uses Playwright.

KV.ee (Baltics Classifieds Group) is primarily an agency-subscription platform.
Base individual listing fees are not publicly listed.

What IS publicly listed at https://www.kv.ee/liitumine:
  - Agency subscriptions: €79–€329/month (broker packages, fee_period=per_month)
  - Add-on/boost services (per_day or per_listing)

Source: https://www.kv.ee/liitumine (Hinnakiri alates 01.10.2025)
"""

import re
from datetime import date

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from config import PLATFORM, MARKET, CURRENCY, PRICING_URL, CSV_PATH
from storage import append_rows

PLAYWRIGHT_TIMEOUT = 30_000

# Agency subscription tiers — monthly fee per broker account
AGENCY_TIERS = [
    {"tier_name": "Broker S",    "fee_amount": 79,  "fee_period": "per_month"},
    {"tier_name": "Broker M",    "fee_amount": 139, "fee_period": "per_month"},
    {"tier_name": "Broker L",    "fee_amount": 189, "fee_period": "per_month"},
    {"tier_name": "Broker XL",   "fee_amount": 239, "fee_period": "per_month"},
    {"tier_name": "Broker XXL",  "fee_amount": 289, "fee_period": "per_month"},
    {"tier_name": "Broker XXXL", "fee_amount": 329, "fee_period": "per_month"},
]

# Boost/add-on services (per listing or per day)
ADDON_TIERS = [
    {"tier_name": "Boost — Star rating",    "fee_amount": 1.49, "fee_period": "per_day"},
    {"tier_name": "Boost — Front page",     "fee_amount": 9.99, "fee_period": "per_day"},
    {"tier_name": "Boost — Date refresh",   "fee_amount": 3.99, "fee_period": "per_listing"},
    {"tier_name": "Boost — Client day",     "fee_amount": 5.00, "fee_period": "per_listing"},
]

HYBRID_NOTE = (
    "Agency subscription model. Individual seller base listing fee not publicly listed. "
    "BCG platform; City24.ee included in higher agency packages."
)


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
            page.wait_for_selector("text=Hinnakiri", timeout=10_000)
        except PlaywrightTimeout:
            pass

        text = page.inner_text("body")
        browser.close()
    return text


def parse_fees(text: str, today: str) -> list[dict]:
    # Sanity-check known amounts
    verified = "79 €" in text and "329 €" in text and "1.49€" in text

    rows = []
    for tier in AGENCY_TIERS + ADDON_TIERS:
        note = HYBRID_NOTE
        if not verified:
            note += " [UNVERIFIED — page content changed]"
        rows.append({
            "scrape_date":    today,
            "platform":       PLATFORM,
            "market":         MARKET,
            "currency":       CURRENCY,
            "tier_name":      tier["tier_name"],
            "fee_amount":     tier["fee_amount"],
            "fee_period":     tier["fee_period"],
            "prop_value_min": "",
            "prop_value_max": "",
            "location_note":  "",
            "hybrid_note":    note,
        })

    status = "Confirmed" if verified else "WARNING: could not confirm"
    print(f"{status} KV.ee pricing from live page. Writing {len(rows)} rows.")
    return rows


def main():
    today = date.today().isoformat()
    print(f"Fetching KV.ee pricing via Playwright: {PRICING_URL}")
    try:
        text = fetch_page_text(PRICING_URL)
        rows = parse_fees(text, today)
    except Exception as e:
        print(f"WARNING: Playwright fetch failed ({e}). Using last-known values.")
        rows = [
            {
                "scrape_date":    today,
                "platform":       PLATFORM,
                "market":         MARKET,
                "currency":       CURRENCY,
                "tier_name":      tier["tier_name"],
                "fee_amount":     tier["fee_amount"],
                "fee_period":     tier["fee_period"],
                "prop_value_min": "",
                "prop_value_max": "",
                "location_note":  "",
                "hybrid_note":    HYBRID_NOTE + " [UNVERIFIED — fetch failed]",
            }
            for tier in AGENCY_TIERS + ADDON_TIERS
        ]
    append_rows(CSV_PATH, rows)


if __name__ == "__main__":
    main()
