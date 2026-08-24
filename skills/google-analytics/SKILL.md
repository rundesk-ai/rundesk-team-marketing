---
name: google-analytics
description: Use when the user needs to inspect Google Analytics 4 accounts or properties; understand where site traffic and sessions come from; break traffic down by channel, source, campaign, landing page, geography, device, or aggregated age and gender; measure leads and other key events; review ecommerce product, purchase, and revenue behavior; or run a bounded historical or realtime GA4 metric query. It supplies read-only GA4 discovery and reporting through an explicitly selected Google account and property. Do not use for Universal Analytics, tag or ecommerce implementation, Google Ads, Merchant Center product feeds, Search Console, Analytics Admin change history, or Analytics configuration changes.
---

# Google Analytics

Run `$RUNDESK_SKILLS/google-analytics/scripts/google-analytics`. Rundesk owns Google sign-in and
hands the command one short-lived token, so never ask for or print a credential. Read
`references/cli.md` for signing in, report arguments, breakdown fields, output fields, or validation.

Start with `profiles`, which shows the accounts Rundesk holds and needs no network, then discover
what the selected account can reach:

```sh
"$RUNDESK_SKILLS/google-analytics/scripts/google-analytics" profiles
"$RUNDESK_SKILLS/google-analytics/scripts/google-analytics" accounts --email <address> --limit 25
"$RUNDESK_SKILLS/google-analytics/scripts/google-analytics" properties --limit 50
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

Never guess an account or a property. Use the exact numeric property ID returned by
`properties`.

## Answer the common questions with the bounded reports

Prefer these over hand-built field lists; each one already carries the current GA4 field names for
its question and returns the largest rows first.

```sh
google-analytics traffic --property <id> --breakdown channel --limit 25
google-analytics audience --property <id> --breakdown country --limit 25
google-analytics key-events --property <id> --breakdown event --limit 25
google-analytics commerce --property <id> --breakdown item --purchased-only --limit 25
```

- `traffic` — where sessions came from: `channel`, `source`, `medium`, `source-medium`, `campaign`,
  `landing-page`, or `date`. Add `--scope first-user` to attribute to the visitor's first visit
  instead of the session; `landing-page` and `date` have no first-user form.
- `audience` — named GA4 audiences or aggregated audience traits: `audience`, `country`, `region`, `city`, `language`, `device`, `browser`,
  `operating-system`, `platform`, `age`, `gender`.
- `key-events` — leads and other key events, GA4's current name for conversions. Broken down by
  `event`, `date`, or `channel`, and always restricted to events the property marks as key events.
  Add `--event generate_lead,purchase` to isolate named events.
- `commerce` — shopping behavior: `item`, `item-id`, `brand`, `category`, `list` report item views,
  cart adds, checkouts, purchases, and item revenue; `date` and `channel` report purchases and
  purchase revenue. `--purchased-only` drops rows with no purchase in the window.

Every one of these accepts `--start-date`, `--end-date`, `--limit`, `--email`, and `--json`, and
defaults to the last 28 days.

Use `report` and `realtime` only when the question needs a field combination the four bounded
reports do not cover:

```sh
google-analytics report --property <id> --metrics sessions,activeUsers --dimensions date --limit 100
google-analytics realtime --property <id> --metrics activeUsers --dimensions country --limit 25
```

## Read the results honestly

These commands report only what the property already collects. A property with no ecommerce tagging
returns empty `commerce` rows, and a property that marks no key events returns empty `key-events`
rows; that is a measurement gap, not a command failure. Say so rather than reporting zero demand.

Google's own caveats arrive on stderr: withheld low-volume rows, an `(other)` rollup, sampling, and
the reporting currency. Repeat them when they change what the numbers mean. Age and gender are
thresholded and need Google signals enabled, so small groups are missing by design.

Analytics measures the property only. Product feeds and item availability live in Merchant Center,
and ad spend lives in Google Ads; neither is reachable from here.

Keep dimensions, metrics, date ranges, and row limits no broader than the question requires. Human
output is compact CSV. Use `--json` only for downstream processing or when normalized JSON fields
are explicitly needed.

All commands are read-only. This package cannot create or edit Analytics accounts, properties,
streams, events, audiences, access, or configuration.
