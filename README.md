# re-pricing-kv-ee

Weekly scraper for **KV.ee** pricing (Estonia).

## Platform

KV.ee is Estonia's leading real estate portal, operated by Baltics Classifieds Group (BCG).
BCG also operates City24.ee — included in higher agency packages.

## Pricing Model

KV.ee is an **agency subscription** model. Individual seller base listing fees are not publicly listed.

### Agency Subscriptions (per month, broker account)

| Tier | Fee (EUR/month) |
|------|----------------|
| Broker S | €79 |
| Broker M | €139 |
| Broker L | €189 |
| Broker XL | €239 |
| Broker XXL | €289 |
| Broker XXXL | €329 |

### Boost / Add-on Services

| Service | Fee (EUR) | Period |
|---------|-----------|--------|
| Star rating | €1.49 | per_day |
| Front page placement | €9.99 | per_day |
| Date refresh + e-Agent | €3.99 | per_listing |
| Client day (open house) | €5.00 | per_listing |

- `currency = EUR`
- Prices valid from 01.10.2025

Source: [KV.ee liitumine](https://www.kv.ee/liitumine)

## Note on Individual Seller Pricing

Base listing fees for private sellers are not published on the public pricing page.
KV.ee monetises primarily through agency subscriptions.

## Running Locally

```bash
pip install -r requirements.txt
playwright install chromium
python scraper.py
```
