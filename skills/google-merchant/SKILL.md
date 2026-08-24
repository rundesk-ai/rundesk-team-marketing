---
name: google-merchant
description: Use when the user needs to inspect a Google Merchant Center account for a shopping site; see which products are eligible, pending, or disapproved on Shopping ads and free listings; diagnose item-level feed issues and what is suppressing products; measure product impressions, clicks, click-through rate, and conversions segmented by date, product, brand, category, country, marketing method, or store type; or review Google's price benchmarks, suggested prices, best sellers, and competitive visibility. It supplies read-only Merchant Center discovery, product status, issue diagnostics, and bounded performance reporting through an explicitly selected Google account and Merchant Center account. Do not use for editing products, feeds, inventory, promotions, or account settings, nor for Google Analytics, Search Console, or Google Ads.
---

# Google Merchant Center

Run `$RUNDESK_SKILLS/google-merchant/scripts/google-merchant`. Rundesk owns Google sign-in and
hands the command one short-lived token, so never ask for or print a credential. Read
`references/cli.md` for signing in, report arguments, breakdown fields, output fields, or validation.

Start with `profiles`, which shows the accounts Rundesk holds and needs no network, then discover
the Merchant Center accounts the selected account can reach:

```sh
"$RUNDESK_SKILLS/google-merchant/scripts/google-merchant" profiles
"$RUNDESK_SKILLS/google-merchant/scripts/google-merchant" accounts --email <address> --limit 25
```

`--email` names one signed-in Google account, and is needed only when Rundesk holds more than one;
the refusal lists the connected addresses. When nothing is connected, the command says so and names
the command to run. Ask the owner to run `rundesk login google` in their own terminal, or pass
`--auth` to run that sign-in from here when a browser is available. The `google-auth` skill in this
catalog owns sign-in, the list of connected accounts, and the Google Cloud setup.

`--profile <app-profile>` exists and is almost never right: it selects a second OAuth **app**, for
an installation with two Google Cloud projects. Do not add it to a command you construct, and never
use it to choose an account — that is always `--email`. Never ask anyone for a client ID, a client
secret, or a refresh token.

Never guess an account. Every other command requires `--account` with the exact numeric
Merchant Center account ID that `accounts` returned. Reporting works for standalone accounts and
individual sub-accounts; an advanced account has no reports of its own, so select the sub-account
that owns the products.

## Answer "is my catalog serving?" before anything else

```sh
google-merchant status --account <id> --limit 50
google-merchant issues --account <id> --limit 25
google-merchant products --account <id> --status not_eligible_or_disapproved --limit 25
```

- `status` — how many products are active, pending, expiring, and disapproved, split by reporting
  context and country. This is the fastest read of catalog health.
- `issues` — the item-level issues behind those numbers, largest number of affected products first,
  with Google's severity, whether the merchant must act, and a documentation link.
- `products` — individual products with their serving status, price, and click potential. Filter
  with `--status`, `--brand`, or `--reporting-context`.

Google does not allow filtering or sorting products by their per-context status or issue list, so
use `issues` for issue analysis and `products` for per-product state.

## Measure performance

```sh
google-merchant performance --account <id> --breakdown product --during LAST_30_DAYS --limit 25
google-merchant performance --account <id> --breakdown date --start-date 2024-01-01 --end-date 2024-01-31
```

`--breakdown` accepts `product`, `brand`, `category`, `product-type`, `country`, `date`, `week`,
`marketing-method`, `store-type`, or `custom-label`, and every report carries clicks, impressions,
click-through rate, conversions, conversion value, and conversion rate. Restrict with
`--marketing-method`, `--country`, or `--store-type`.

A date range is mandatory, so `--during` defaults to `LAST_30_DAYS`. Prefer it over an explicit
window: it asks Google what the range means in the account's own time zone instead of guessing from
this machine's clock. `--start-date` and `--end-date` must be given together.

## Compare against the market

```sh
google-merchant price-competitiveness --account <id> --country US --limit 25
google-merchant price-insights --account <id> --limit 25
google-merchant best-sellers --account <id> --country US --granularity weekly --limit 25
google-merchant competitive-visibility --account <id> --country US --category 166 --limit 25
```

- `price-competitiveness` — each product's price beside Google's benchmark for that country.
- `price-insights` — Google's suggested price with its predicted change in impressions, clicks, and
  conversions.
- `best-sellers` — the best selling `products` or `brands` on Google. `--country` and
  `--granularity` are required; add `--category` for one Google product category and `--date` for a
  specific report, or omit both for all top-level categories in Google's latest report.
- `competitive-visibility` — `benchmark`, `competitor`, or `top-merchant` views. `--country` and
  `--category` are required, and one country and category are sent per request because Google warns
  that wider queries can time out.

These four need Market Insights enabled on the account. A permission error naming Market Insights
is a Merchant Center program that is not turned on, not a broken command.

## Read the results honestly

These commands report only what the account already has. An account with no disapprovals returns
empty `issues` rows, and a product that never served returns no performance row; that is the
absence of a problem or of traffic, not a failure. Google returns only rows where at least one
requested metric is non-zero.

Google reports conversions, conversion value, and conversion rate only for the free traffic source,
so ads rows leave them empty. Do not read that as zero conversions from ads.

Prices and conversion value are money: each gets its own `_currency` column. When a query mixes
price and non-price metrics, Google returns them in separate rows, one per currency, padding the
other metrics with zero — including a row with an empty currency. Never sum those rows together.

Performance days are days in the Merchant Center account time zone. Google publishes no freshness
lag, so treat the most recent day as possibly incomplete rather than as a decline.

Keep breakdowns, filters, date ranges, and row limits no broader than the question requires. Human
output is compact CSV, and truncation is reported on stderr. Use `--json` only for downstream
processing.

All commands are read-only. This package cannot create, edit, or delete products, product inputs,
feeds, data sources, inventory, promotions, users, or account settings.
