# Google Merchant CLI reference

## Commands

```text
google-merchant profiles
google-merchant accounts --profile example --limit 25
google-merchant status --profile example --account 123456 [--reporting-context SHOPPING_ADS] [--country US]
google-merchant issues --profile example --account 123456 [--reporting-context SHOPPING_ADS] [--country US]
google-merchant products --profile example --account 123456 \
  [--status eligible] [--brand Acme] [--reporting-context SHOPPING_ADS] --limit 50
google-merchant performance --profile example --account 123456 \
  --breakdown product [--during LAST_30_DAYS | --start-date 2024-01-01 --end-date 2024-01-31] \
  [--marketing-method ads] [--country US] [--store-type online_store] --limit 25
google-merchant price-competitiveness --profile example --account 123456 [--country US] --limit 50
google-merchant price-insights --profile example --account 123456 --limit 50
google-merchant best-sellers --profile example --account 123456 \
  --country US [--view products|brands] [--granularity weekly|monthly] [--category 166] [--date 2024-01-01]
google-merchant competitive-visibility --profile example --account 123456 \
  --country US --category 166 [--view benchmark|competitor|top-merchant] \
  [--during LAST_30_DAYS] [--traffic-source organic]
```

Every command accepts `--profile`, `--email`, `--auth`, `--json`, and, apart from `profiles`,
`--limit`.
Reports allow at most 5,000 rows, `accounts` allows 2,000, and `status` and `issues` allow 1,000.
Every read is bounded by `--limit`; truncation is reported on stderr.

## Signing in

Rundesk owns Google sign-in. It runs the browser flow, keeps the grant sealed, and refreshes
tokens. This package holds none of that and declares no credentials: it asks Rundesk for one
short-lived access token over one end of a socket pair it creates itself, and uses that token as a
request header only. The token never reaches an argument, an environment variable, a file, or any
output.

What `google` means — Google's endpoints, identity fields, base scopes, and the scope behind each
capability — is declared by this catalog's `google-auth` package, which owns sign-in, the account
listing, and the Google Cloud setup. This package reads nothing from it and never runs it.

```sh
rundesk login google
rundesk login google --profile acme
```

A *profile* is one OAuth app configuration, not a person. A single profile can hold several verified
Google accounts; Rundesk keys each by Google's immutable subject identifier and selects it by email.

```text
--profile <app-profile>   which OAuth app configuration to use; needed only when more than one exists
--email <address>         which signed-in account to use; needed only when that profile holds several
--auth                    run `rundesk login google` first, forwarding --profile, then continue
```

`profiles` lists the accounts Rundesk holds for one app profile and contacts Google for none of it.
Missing sign-in, an unconfigured app profile, an ambiguous account, and a missing scope each name
the exact command to run.

Rundesk attaches this package's fixed scope to the token and widens consent in the browser itself
when a grant is short:

```text
https://www.googleapis.com/auth/content   every command
```

The OAuth app Rundesk signs in with must belong to a Google Cloud project with the Merchant API
enabled and Merchant API developer registration completed once by an account holding `ADMIN`; an
unregistered project is rejected as unauthenticated, commonly with `AUTH_GCP_NOT_REGISTERED`.

A Rundesk older than the provider-neutral sign-in bridge cannot answer at all; the command says so
and says to update Rundesk. There is no other way to authorize this package: there is no client ID, client secret,
refresh token, dotenv, or `--env-file` to configure.

### The scope is broader than this package

Google publishes exactly one Merchant API scope, `https://www.googleapis.com/auth/content`, and it
is read-write. There is no read-only scope, so the consent screen says "Manage your product listings
and accounts for Google Shopping" even though nothing here writes.

Constrain the account in Merchant Center instead. Grant the signed-in identity the `READ_ONLY`
access right, which Google documents as access to the same read methods as `STANDARD` with no access
to any mutating method. Add `PERFORMANCE_REPORTING` for `performance`. `API_DEVELOPER` identifies a
technical contact; it does not grant account data access.

## Endpoints

| Command | Method and path |
|---|---|
| `accounts` | `GET accounts/v1/accounts` |
| `status`, `issues` | `GET issueresolution/v1/accounts/{account}/aggregateProductStatuses` |
| everything else | `POST reports/v1/accounts/{account}/reports:search` |

`v1` is the stable version of each sub-API and is pinned literally. `v1beta` was discontinued on
28 February 2026; its endpoints may still answer, which is reachability rather than support.

`status` and `issues` read the same aggregate resource: `status` reports its counts, `issues`
expands its item-level issues. Google accepts a filter there on `reportingContext` and `country`
only. That method serves standalone accounts and sub-accounts, not advanced accounts.

The commands follow Google's current REST reference for the `issueresolution/v1` resource:
filters use `reportingContext` and `country`, counts are under `stats`, and issues are under
`itemLevelIssues`. They refuse an unrecognized response shape instead of rendering blank counts
or a false empty issue list.

## Reports and the query language

Report commands build a Merchant Center Query Language statement. Callers choose a breakdown, view,
or filter option, never a field list, so a query can only be assembled from names checked against
the tables below.

| Command | Table |
|---|---|
| `products` | `product_view` |
| `performance` | `product_performance_view` |
| `price-competitiveness` | `price_competitiveness_product_view` |
| `price-insights` | `price_insights_product_view` |
| `best-sellers` | `best_sellers_product_cluster_view`, `best_sellers_brand_view` |
| `competitive-visibility` | `competitive_visibility_benchmark_view`, `competitive_visibility_competitor_view`, `competitive_visibility_top_merchant_view` |

Field names are snake_case in a query and camelCase in the response; the runtime maps between them.

### Why filter values are refused rather than escaped

MCQL's published grammar defines a string as `(' Char* ') | (" Char* ")` and never defines `Char`.
There is no documented escape sequence, so there is no verifiable way to represent a quote inside a
literal. This package therefore refuses any filter value containing `'`, `"`, `\`, or a control
character instead of attempting an escape that Google does not document. A refused search term is a
visible error; a silently mangled or extended `WHERE` clause is not.

The grammar also has no `OR`, no parentheses, and no `GROUP BY`. Conditions are joined with `AND`
only, and segmentation is implicit in which segment columns a breakdown selects.

### Performance breakdowns

`performance` always reports `clicks`, `impressions`, `click_through_rate`, `conversions`,
`conversion_value`, and `conversion_rate`.

| `--breakdown` | Segment fields |
|---|---|
| `product` | `offer_id`, `title` |
| `brand` | `brand` |
| `category` | `category_l1`, `category_l2`, `category_l3` |
| `product-type` | `product_type_l1`, `product_type_l2`, `product_type_l3` |
| `country` | `customer_country_code` |
| `marketing-method` | `marketing_method` |
| `store-type` | `store_type` |
| `custom-label` | `custom_label0` |
| `date` | `date` |
| `week` | `week` |

`date` and `week` sort oldest first; every other breakdown sorts by clicks, largest first.

Google requires a date condition on every performance query and requires at least one metric beside
any segment, so both are structural rather than optional. There is no `month` or `year` segment;
roll those up from `date`. `customer_country_code` returns `ZZ` when Google cannot determine the
customer's country.

### Required conditions Google imposes

- `best-sellers` must select `report_date`, `report_granularity`, `report_country_code`, and
  `report_category_id`, and must filter on granularity and country. Without `--date` Google returns
  its latest weekly or monthly report; without `--category` it returns all top-level categories.
  `inventory_status` ignores the country filter. The category ID is sent unquoted, matching Google's
  own samples.
- `competitive-visibility` must filter on date, country, and category for all three views. The
  `benchmark` view must select `date`; the `top-merchant` view must not select it, though it still
  filters on it.
- `price-competitiveness` and `price-insights` must select `id`; `price-competitiveness` must also
  select `report_country_code`.
- `products` may not filter or sort on per-context status or item issues. `reporting_context` is
  filter-only and is never selected.

## Output

Human output is CSV; `--json` emits the same records as JSON. Every row carries `account_id` and
`profile`.

A money field is rendered in its currency's standard unit, converted from Google's int64 micros
with exact decimal arithmetic, and is followed by its own `_currency` column. When a query mixes
price and non-price metrics Google returns them as separate rows, one per currency, zero-padding
the other metrics and emitting one row with an empty currency code. Those rows are preserved as
Google sent them; summing across them double-counts.

A `google.type.Date` arrives as an object on some views and as a plain string on others, and both
are rendered as `YYYY-MM-DD`. A repeated field is joined with `|`.

## Failures

Errors print to stderr as `ERROR: <message>` and exit 2. Google's own message is repeated when it
sends one; access tokens and authorization headers never appear in output.

Common causes: `PERMISSION_DENIED_TO_USE_MARKET_INSIGHTS` means the program is not enabled on the
account; `PERMISSION_DENIED_NOT_ALLOWLISTED_TO_USE_PERFORMANCE_REPORTING` means the identity lacks
the performance and insights role; `INVALID_QUERY` means the query was rejected, which is a defect
in this package rather than in the request. Retryable statuses are retried with backoff, honoring
numeric `Retry-After` delays.

## Tests

```sh
python3 skills/google-merchant/scripts/google-merchant.d/test-google-merchant.py -q
skills/google-merchant/scripts/google-merchant --help
```

Tests are offline: a stand-in Rundesk answers the sign-in bridge exactly as the real one documents
it, synthetic fixtures replace every Merchant API boundary, and no test contacts Google.
