# Retrieving a URL you do not own

Read this before inspecting any page — your own or a competitor's. The rest of this package tells you
what to conclude; this file fixes what you fetch, what you must not do while fetching, and what every
inspection returns, so two audits of the same site agree.

## What you may do, and what you may not

Retrieval is reading. It stops being reading the moment it changes something or reaches somewhere it
was not offered.

- **`GET` and `HEAD` only.** Never `POST`, `PUT`, `PATCH`, or `DELETE` against a site you are
  auditing. A form submission is contact, not inspection.
- **Public hosts only.** Never a loopback, link-local, or private address, and never an internal
  hostname. If a redirect leads there, stop and report it — a public URL redirecting into a private
  range is itself the finding.
- **No credentials.** Do not send cookies, tokens, `Authorization` headers, or a logged-in session.
  What a signed-in user sees is not what a crawler indexes, so an authenticated fetch answers a
  different question than the one you were asked.
- **Identify honestly.** Do not forge Googlebot to see what Google sees. It is a request to be served
  different content, which is the definition of the thing you would be auditing for, and a site that
  cloaks will hand you the cloaked version and hide the defect. Where a per-agent answer is genuinely
  the question — a `robots.txt` rule — read the file and apply the rule yourself.
- **Stay small.** A competitor audit is tens of requests. Fetch a representative set and say it was a
  sample; do not crawl a catalog you were not asked to crawl.
- **Honor `robots.txt` on a host you do not own.** Read it first, and do not fetch a path it
  disallows. You are asking that site's owner for the same courtesy you would advise your own.

## Fetch the file that governs the rest first

```sh
curl -sS --max-time 20 https://example.com/robots.txt
```

A `4xx` here means there is no `robots.txt` at all, which is a finding and not an error — treat it as
"no directives", check the status explicitly, and never mistake an HTML error page for a robots file.
A `robots.txt` served as `4xx` is treated by crawlers as absent, so **file-exists is not the check;
`200` with `content-type: text/plain` is.**

## The fixed check set

Every page inspection returns these, in this order, or says which could not be established and why.
An audit missing a row is incomplete, not concise.

| Field | How it is retrieved |
|---|---|
| Final status and redirect chain | `curl -sSI -L`, reading every hop, not only the last |
| `Location` form on each hop | absolute or relative — a relative target resolves against the current directory |
| `X-Robots-Tag` | response headers |
| `<title>` and meta description | served HTML |
| `<meta name="robots">`, `max-snippet`, `data-nosnippet` | served HTML |
| Canonical, and whether it is self-referential | served HTML |
| Open Graph and `twitter:` tags | served HTML |
| Structured data present or absent | `application/ld+json` blocks |
| `<h1>` count and text | served HTML |
| Sitemap and `robots.txt` status | direct fetch, status checked |

```sh
U=https://example.com/page
curl -sSI -L --max-time 20 "$U" | grep -iE '^HTTP|^location|^x-robots-tag|^content-type'
curl -sS  -L --max-time 25 "$U" -o page.html
grep -oiE '<title[^>]*>[^<]*|<link[^>]*rel=.{0,3}canonical[^>]*>|<meta[^>]*name="(description|robots)"[^>]*>' page.html
grep -oiE 'og:[a-z_]+|twitter:[a-z_]+' page.html | sort -u
grep -c 'application/ld+json' page.html
grep -oiE '<h1[^>]*>[^<]{0,80}' page.html
```

**Match tags tolerantly or you will report defects that do not exist.** Use `<tag[^>]*>`, never
`<tag>`. A bare pattern misses every tag carrying an attribute — a framework that emits
`<title data-x="">` will read as a page with no title, and "no title element" is a serious-sounding
finding that is simply wrong. When a check returns nothing, prove the absence a second way before
reporting it.

## Follow the whole redirect chain, not the destination

```sh
curl -sSI --max-time 20 "$U" | grep -i '^location'          # the target as sent
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' -L --max-time 20 "$U"   # where it ends
```

Compare the two. A `Location` without a leading slash is **relative** and resolves against the
current directory, so `/category/x` redirecting to `art/x` lands on `/category/art/x`. The redirect
returns `301` and the destination exists, and the URL still ends at `404`. Checking only the first
hop's status, or only whether the destination path is valid, misses this entirely.

Also record whether each hop is `301` or `302`. A temporary redirect on a permanent move tells
crawlers not to transfer the signal.

## Comparing yourself with a competitor

The comparison is only worth anything if both sides were fetched the same way on the same day. Run
the same check set against the same page type — homepage against homepage, product against product —
and report the fields side by side.

State plainly what a comparison cannot show you: their traffic, their conversion rate, their
rankings, or why they made a choice. You retrieved what they serve. Anything about their business,
strategy, or results is a different kind of claim and is not established by fetching their HTML.

## Comparing a sitemap with what is served

```sh
curl -sS -L --max-time 30 https://example.com/sitemap.xml | grep -oE '<loc>[^<]*</loc>' | sed 's/<[^>]*>//g' > urls.txt
wc -l urls.txt
head -20 urls.txt | while read -r u; do printf '%s %s\n' "$(curl -sS -o /dev/null -w '%{http_code}' -L --max-time 15 "$u")" "$u"; done
```

Sample rather than sweep, and say the sample size. What this establishes: URLs the site declares and
what those return today. What it does not establish: what is indexed — that needs Search Console, and
the difference between declared and indexed is usually the actual finding.

## What retrieval cannot establish

Every finding here is what a URL returned on a date. It is not traffic, not rankings, not revenue,
and not cause. A page can be perfectly retrievable and rank nowhere. Report the retrieval, its date,
and the check that produced it, then say what would settle the question you were actually asked.
