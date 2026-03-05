# re-pricing-kv-ee

Weekly scraper for **KV.ee** listing fees (Estonia).

## Platform

KV.ee is Estonia's leading real estate portal, operated by Baltics Classifieds Group (BCG).
BCG also operates City24.ee — included in the Pro agency package.

## Pricing Model

**Per-listing fee** for individual sellers (publicly listed):

| Tier | Listing Type | Fee (EUR) |
|------|-------------|-----------|
| Individual — Sales | Property for sale | €44.99 |
| Individual — Rental | Property for rent | €24.99 |

Agency packages are available but pricing is not publicly listed — contact sales.

- `fee_period = per_listing`
- `currency = EUR`
- `hybrid_note`: "BCG platform; City24.ee included in Pro agency package. Agency pricing: contact sales."

Source: [KV.ee liitumine](https://www.kv.ee/liitumine)

## Output

`data/pricing.csv` — 2 rows per scrape date (individual seller tiers only).

## Running Locally

```bash
pip install -r requirements.txt
python scraper.py
```
