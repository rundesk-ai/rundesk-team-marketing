# Google Analytics CLI reference

## Commands

```text
google-analytics profiles
google-analytics accounts --profile example --limit 25
google-analytics properties --profile example [--account 123456] --limit 50
google-analytics report --profile example --property 987654321 \
  --start-date 28daysAgo --end-date today \
  --metrics sessions,activeUsers --dimensions date --limit 100
google-analytics realtime --profile example --property 987654321 \
  --metrics activeUsers --dimensions country --limit 25
google-analytics traffic --profile example --property 987654321 \
  --breakdown channel [--scope session|first-user] --limit 25
google-analytics audience --profile example --property 987654321 --breakdown country --limit 25
google-analytics key-events --profile example --property 987654321 \
  --breakdown event [--event generate_lead,purchase] --limit 25
google-analytics commerce --profile example --property 987654321 \
  --breakdown item [--purchased-only] --limit 25
```

`accounts` and `properties` use the Analytics Admin API's account summaries. Every other command
uses the GA4 Data API's `runReport`, except `realtime`, which uses `runRealtimeReport`. Every read
is bounded by `--limit`; the command reports truncation to stderr when Google indicates more results
exist.

`report` and `realtime` take comma-separated Google API names in `--metrics` and `--dimensions` and
send them unchanged. They accept any date string Google accepts.

`traffic`, `audience`, `key-events`, and `commerce` choose their own current GA4 field names from
`--breakdown` and share `--property`, `--start-date`, `--end-date`, `--limit`, `--profile`, and
`--json`. They default to `28daysAgo` through `today`, and accept only `YYYY-MM-DD`, `today`,
`yesterday`, or `NdaysAgo`. Each sorts the largest rows first so a small `--limit` returns the top
of the distribution, except a `date` breakdown, which sorts oldest day first.

## Bounded report fields

`traffic` reports `sessions`, `activeUsers`, `newUsers`, `engagedSessions`, `engagementRate`,
`averageEngagementTimePerSession` (derived as `userEngagementDuration/sessions`), `keyEvents`, and
`totalRevenue`.

| `--breakdown` | `--scope session` | `--scope first-user` |
|---|---|---|
| `channel` | `sessionDefaultChannelGroup` | `firstUserDefaultChannelGroup` |
| `source` | `sessionSource` | `firstUserSource` |
| `medium` | `sessionMedium` | `firstUserMedium` |
| `source-medium` | `sessionSource`, `sessionMedium` | `firstUserSource`, `firstUserMedium` |
| `campaign` | `sessionCampaignName` | `firstUserCampaignName` |
| `landing-page` | `landingPage` | refused |
| `date` | `date` | refused |

`audience` reports `activeUsers`, `newUsers`, `engagedSessions`, `engagementRate`, `eventCount`,
`keyEvents`, and `totalRevenue`, broken down by named GA4 `audience` (`audienceName`), `country`, `region`, `city`, `language`,
`device` (`deviceCategory`), `browser`, `operating-system` (`operatingSystem`), `platform`,
`age` (`userAgeBracket`), or `gender` (`userGender`).

`key-events` reports `keyEvents`, `eventCount`, `activeUsers`, and `totalRevenue`, broken down by
`event` (`eventName`), `date`, or `channel` (`sessionDefaultChannelGroup`).

The audience and key-event metric sets are the ones Google pairs with those dimensions in its own
predefined reports, so a user-scoped breakdown such as age stays inside a published combination.

`commerce` breaks down by `item` (`itemName`), `item-id` (`itemId`), `brand` (`itemBrand`),
`category` (`itemCategory`), or `list` (`itemListName`) and reports `itemsViewed`,
`itemsAddedToCart`, `itemsCheckedOut`, `itemsPurchased`, and `itemRevenue`. It breaks down by `date`
or `channel` (`sessionDefaultChannelGroup`) and reports `ecommercePurchases`, `purchaseRevenue`, and
`totalRevenue`, because item-scoped metrics and purchase-scoped metrics are separate GA4 families.

## Filtering

Filtering is limited to what isolates a dataset correctly, because a broad filter language belongs
in a query tool rather than a guarded report.

- `key-events` always sends `dimensionFilter` on `isKeyEvent` with an `EXACT` match on `true`, which
  is the GA4 field that replaced `isConversionEvent` when Google renamed conversions to key events
  in May 2024. Without it, a key-event count would include ordinary events.
- `--event` adds a case-sensitive `inListFilter` on `eventName` inside an `andGroup` with the key
  event filter. It accepts at most 25 names, each in GA4's event-name form: a leading letter, then
  letters, digits, or underscores, up to 40 characters.
- `--purchased-only` sends a `metricFilter` requiring the breakdown's purchase metric to be greater
  than zero: `itemsPurchased` for an item breakdown, `ecommercePurchases` for `date` and `channel`.

## Data that does not exist yet

These commands report what the property already collects. `commerce` returns no rows for a property
without GA4 ecommerce events such as `view_item`, `add_to_cart`, `begin_checkout`, and `purchase`,
and `key-events` returns no rows until events are marked as key events in the Analytics interface.
Report that as an instrumentation gap, not as zero demand. Age and gender additionally require
Google signals and are thresholded by Google.

Analytics reports the property's own measurement. Merchant Center product feeds and Google Ads cost
are separate products with separate APIs and are not reachable through this package.

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
https://www.googleapis.com/auth/analytics.readonly   every command
```

The OAuth app Rundesk signs in with must belong to a Google Cloud project where the Google Analytics
Data API and Google Analytics Admin API are enabled, and the account that signs in must be able to
reach the requested Analytics resources.

A Rundesk older than the provider-neutral sign-in bridge cannot answer at all; the command says so
and says to update Rundesk. There is no other way to authorize this package: there is no client ID, client secret,
refresh token, dotenv, or `--env-file` to configure.

## Output

Human-readable discovery commands emit CSV:

```text
account_id,display_name,property_count,profile
123456,Example account,2,example
```

Every report command's output starts with the requested dimensions, followed by metrics and
`profile,property_id`. `--json` emits normalized objects rather than Google's raw response. Empty
result sets still print a CSV header.

```text
sessionDefaultChannelGroup,sessions,activeUsers,newUsers,engagedSessions,engagementRate,averageEngagementTimePerSession,keyEvents,totalRevenue,profile,property_id
Organic Search,1204,908,517,842,0.699,54.2,63,4210.75,example,987654321
```

The bounded reports repeat Google's response metadata on stderr so a short result is not mistaken
for the whole picture: withheld rows below Google's aggregation thresholds, an `(other)` rollup of
low-volume rows, sampling, Google's own empty-result reason, and the reporting currency whenever a
revenue metric was requested.

## Validation

```sh
python3 "$RUNDESK_SKILLS/google-analytics/scripts/google-analytics.d/test-google-analytics.py" -q
"$RUNDESK_SKILLS/google-analytics/scripts/google-analytics" --help
"$RUNDESK_SKILLS/google-analytics/scripts/google-analytics" profiles
```

The test suite is offline: a stand-in Rundesk answers the sign-in bridge exactly as the real one
documents it, and synthetic responses stand in for Google. Optional live smoke tests should stop
after bounded `accounts`, `properties`, and one small report. This package has no mutation
command.

## Official references

- [Google Analytics Admin API account summaries](https://developers.google.com/analytics/devguides/config/admin/v1/rest/v1beta/accountSummaries/list)
- [Google Analytics Data API runReport](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
- [Google Analytics Data API runRealtimeReport](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runRealtimeReport)
- [Data API dimensions and metrics](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
- [Data API predefined reports](https://developers.google.com/analytics/devguides/reporting/data/v1/predefined-reports)
- [Data API changelog: key events replace conversions](https://developers.google.com/analytics/devguides/reporting/data/v1/changelog)
- [Data API FilterExpression](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/FilterExpression)
- [Data API OrderBy](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/OrderBy)
- [Data API ResponseMetaData](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/ResponseMetaData)
- [Data API limits and quotas, including thresholded dimensions](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)
- [GA4 ecommerce measurement events](https://developers.google.com/analytics/devguides/collection/ga4/ecommerce)
- [GA4 event naming rules](https://support.google.com/analytics/answer/13316687)
- [Google OAuth 2.0 for web-server applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
