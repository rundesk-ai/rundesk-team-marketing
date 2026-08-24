# Google Search Console CLI reference

## Commands

```text
google-search-console profiles
google-search-console sites --profile example --limit 25
google-search-console performance --profile example --site https://www.example.test/ --days 28 --dimension query --limit 25
google-search-console performance --profile example --site sc-domain:example.test --start-date 2026-07-01 --end-date 2026-07-31 --dimension page --dimension device --limit 100
google-search-console inspect-url --profile example --site https://www.example.test/ --url https://www.example.test/page
google-search-console sitemaps --profile example --site https://www.example.test/ --limit 25
google-search-console performance --profile example --site https://www.example.test/ --dimension page --filter country:equals:usa --filter device:equals:MOBILE
google-search-console submit-sitemap --profile example --site https://www.example.test/ --sitemap https://www.example.test/sitemap.xml
google-search-console submit-sitemap --profile example --site https://www.example.test/ --sitemap https://www.example.test/sitemap.xml --confirm
```

Every command except `submit-sitemap` is read-only. Text is the compact default; pass `--json` for
structured output. `sites`, `performance`, and `sitemaps` default to 25 results and accept `--limit` from 1 to
1,000. When a list is cut to the requested limit, the command warns on stderr that output may be
truncated.

`performance` defaults to the last 28 complete days in Google's Pacific reporting zone
(`America/Los_Angeles`), which is how Search Console buckets rows; a late-evening UTC run therefore
still ends on the prior Pacific day. Use either `--days` or both `--start-date` and `--end-date`,
which are passed to Google verbatim. Supported dimensions are `date`, `country`, `device`, `page`,
`query`, and `searchAppearance`; repeat `--dimension` to group by more than one. Optional
`--search-type` values are `web`, `image`, `video`, `news`, `discover`, and `googleNews`.

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
https://www.googleapis.com/auth/webmasters   every command, including submit-sitemap
```

A Rundesk older than the provider-neutral sign-in bridge cannot answer at all; the command says so
and says to update Rundesk. There is no other way to authorize this package, and it declares no credentials of its own:
there is no client ID, client secret, refresh token, dotenv, or `--env-file` to configure.

## Filtering performance

`--filter DIMENSION:OPERATOR:EXPRESSION` is repeatable and adds Google's `dimensionFilterGroups` to
the Search Analytics request body. Without `--filter` that key is absent, so an unfiltered report
sends exactly the request body it sent before.

```json
{"dimensionFilterGroups": [{"groupType": "and", "filters": [
  {"dimension": "country", "operator": "equals", "expression": "usa"},
  {"dimension": "query", "operator": "contains", "expression": "pricing"}
]}]}
```

Every `--filter` joins that one `and` group, so a row is returned only when it matches all of them.
Google ANDs separate groups together and documents only the `and` group type, so a single group
already expresses every combination this command can build. A filter may name a dimension the report
does not group by.

Filter dimensions are `query`, `page`, `country`, `device`, and `searchAppearance`. Operators are
`equals`, `notEquals`, `contains`, `notContains`, `includingRegex`, and `excludingRegex`. The
argument is split on its first two colons only, so a page or query expression may contain colons and
slashes; the expression travels in the JSON body and is never percent-encoded.

Expressions by dimension:

- `country` with `equals` or `notEquals` takes an ISO 3166-1 alpha-3 code and is lowercased for you,
  so `usa`, `USA`, and `Usa` all work; anything that is not three letters is refused.
- `device` with `equals` or `notEquals` is uppercased to `DESKTOP`, `MOBILE`, or `TABLET`; any other
  value is refused.
- `query` and `page` take literal text, or an RE2 pattern for the two regex operators. RE2 matches
  partially and case-insensitively unless the pattern is anchored with `^` or `$`, or prefixed with
  `(?-i)`.
- `searchAppearance` is sent verbatim in the `AMP_BLUE_LINK` form Search Console reports, because
  Google extends that vocabulary without notice.

`contains`, `notContains`, and both regex operators are always sent exactly as typed, including for
`country` and `device`, because they match part of a value rather than all of it. A malformed filter
is refused before any credential or network use.

## Sitemap submission

`submit-sitemap` is the only command that changes Google's state. It sends Google's
`sitemaps.submit` method:

```text
PUT https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}
```

`{siteUrl}` and `{feedpath}` are each a whole URL, so each is percent-encoded into a single path
segment. The request carries no body and Google answers with an empty body, so a silent 2xx is not
treated as proof. The command reads the sitemap back with `sitemaps.get` on the same path and
reports the entry Google recorded; when Google returns no usable entry it fails instead of claiming
success, and a path Google rewrote is reported on stderr.

Without `--confirm` the command resolves only local configuration, prints the method, full request
URL, and required scope, makes no network call at all, and exits 2. `--sitemap` must be an absolute
`http` or `https` URL. A sitemap outside a URL-prefix property is warned about on stderr because
Google rejects it; a `sc-domain:` property covers every host it verifies, so no warning applies
there.

## Output

- `sites`: property URL, permission level, profile.
- `performance`: requested dimension keys, clicks, impressions, CTR, average position, profile.
- `inspect-url`: inspection URL, verdict, coverage state, indexing state, last crawl, robots state,
  canonical URLs, profile.
- `sitemaps`: sitemap path, type, submission and download dates, pending state, warning and error
  counts, profile.
- `submit-sitemap` without `--confirm`: property, sitemap, method, request URL, required scope,
  `preview` state, profile. It exits 2 and changes nothing.
- `submit-sitemap --confirm`: property plus the sitemap fields Google returned when the entry was
  read back, `submitted` state, profile.

Errors and truncation warnings go to stderr. Access tokens and authorization headers are never
printed.

## Validation

```sh
python3 skills/google-search-console/scripts/google-search-console.d/test-google-search-console.py -q
skills/google-search-console/scripts/google-search-console --help
skills/google-search-console/scripts/google-search-console submit-sitemap --help
skills/google-search-console/scripts/google-search-console profiles
```

Tests are offline: a stand-in Rundesk answers the sign-in bridge exactly as the real one
documents it, and synthetic responses stand in for Google.

## Official references

- [Search Console API authorization](https://developers.google.com/webmaster-tools/v1/how-tos/authorizing)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Sites: list](https://developers.google.com/webmaster-tools/v1/sites/list)
- [Search Analytics: query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)
- [URL Inspection: index.inspect](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)
- [Sitemaps: list](https://developers.google.com/webmaster-tools/v1/sitemaps/list)
- [Sitemaps: get](https://developers.google.com/webmaster-tools/v1/sitemaps/get)
- [Sitemaps: submit](https://developers.google.com/webmaster-tools/v1/sitemaps/submit)
- [Query your Search analytics data](https://developers.google.com/webmaster-tools/v1/how-tos/search_analytics)
- [RE2 syntax](https://github.com/google/re2/wiki/Syntax)
