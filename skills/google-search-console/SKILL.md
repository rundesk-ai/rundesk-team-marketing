---
name: google-search-console
description: Use when the user needs Google Search Console property discovery, organic search performance overall or filtered by query, page, country, device, or search appearance, URL index inspection, sitemap status, or submitting a sitemap. It supplies bounded evidence through Google's Search Console APIs plus one confirmation-guarded sitemap submission. Do not use for general web search, Google Analytics, SEO recommendations without Search Console evidence, or Search Console changes other than sitemap submission.
---

# Google Search Console

Run `$RUNDESK_SKILLS/google-search-console/scripts/google-search-console`. Rundesk owns Google
sign-in and hands the command one short-lived token, so never ask for or print a credential. Read
`references/cli.md` for signing in, complete output fields, API behavior, or validation.

Start with `profiles`, which shows the accounts Rundesk holds and needs no network. Never guess an
account or a property when more than one is available:

```sh
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" profiles
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" sites --email <address> --limit 25
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

Keep performance reads narrow. Default to the last 28 complete days in Google's Pacific reporting
zone and a small row limit; add only the dimensions needed for the question:

```sh
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" performance \
  --site <property> --dimension query --limit 25
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" inspect-url \
  --site <property> --url https://www.example.test/page
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" sitemaps \
  --site <property> --limit 25
```

A URL-prefix property includes its trailing slash; a domain property starts with `sc-domain:`.
Always reuse the exact property identifier returned by `sites`.

Narrow a report with the repeatable `--filter DIMENSION:OPERATOR:EXPRESSION`. A row must match every
filter given, and a filter works on a dimension the report does not group by:

```sh
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" performance \
  --site <property> --dimension page \
  --filter country:equals:usa --filter device:equals:MOBILE --filter query:contains:pricing
```

Filterable dimensions are `query`, `page`, `country`, `device`, and `searchAppearance`. Read
`references/cli.md` for the operators and the expression each dimension expects.

Performance rows are aggregated and may omit anonymized queries. Treat clicks, impressions,
click-through rate, and average position as Search Console measurements, not complete traffic or
ranking truth. State the date range and dimensions with findings, and report dates as Pacific
reporting days rather than local ones.

Every command except `submit-sitemap` is read-only. `submit-sitemap` changes Google's state, so
it prints the exact request it would send and refuses until `--confirm` is passed:

```sh
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" submit-sitemap \
  --site <property> --sitemap https://www.example.test/sitemap.xml
"$RUNDESK_SKILLS/google-search-console/scripts/google-search-console" submit-sitemap \
  --site <property> --sitemap https://www.example.test/sitemap.xml --confirm
```

Submission requires the `https://www.googleapis.com/auth/webmasters` scope, which Rundesk attaches
to this package's tokens and widens in the browser when a grant is short. Get the owner's decision
before passing `--confirm`, and report the sitemap state the command read back rather than the exit
status alone.

The package still cannot add properties, delete sitemaps, request indexing, or change any other
Search Console configuration.
