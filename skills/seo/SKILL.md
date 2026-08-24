---
name: seo
description: Use this skill when the user asks to audit, plan, or implement search visibility — technical SEO, crawling and indexing, canonical and hreflang handling, Core Web Vitals, structured data, titles and on-page content, internal linking, ecommerce product and category pages, social link previews, or being cited in AI answers such as AI Overviews, AI Mode, ChatGPT and Copilot. It supplies source-backed rules, the checks that can be measured and changed in code, and the evidence behind each recommendation. Do not use it for paid search campaigns, or for performance work with no search or citation goal.
---

# SEO

Make pages retrievable, correct, fast, and worth citing. Every recommendation names a file or URL,
the change to make, and the measurement that proves it.

## Establish the state before advising

Never advise from the source template alone. Search engines and AI crawlers act on what a URL
returns and what renders, which is often not what the repository suggests.

```sh
curl -sSI https://example.com/page                 # status, redirects, x-robots-tag
curl -sS https://example.com/robots.txt
curl -sS https://example.com/page | grep -iE '<title|canonical|meta name="(description|robots)"|og:'
```

Then read the **rendered** HTML, not the response body, for any JavaScript-built page — Google's URL
Inspection tool and Rich Results Test both expose it. Pull real performance and query data from the
field rather than a local Lighthouse run; `references/measurement.md` names the APIs.

State which of the three a finding is: **verified** on this site, **documented** by the search
engine, or **correlational** from a published study. They carry different weight and the third is
never a guarantee.

## Fix in dependency order

Work down this list. An optimization above an unmet requirement is wasted.

1. **Retrievable** — Googlebot not blocked, HTTP `200`, indexable content. These are Google's three
   stated technical requirements; nothing below matters until they hold.
2. **Unambiguous** — one canonical URL per piece of content, consistent internal links, correct
   redirects, sitemaps listing only canonicals.
3. **Rendered** — content present in rendered HTML, links as `<a href>`, no soft 404s.
4. **Fast in the field** — Core Web Vitals at the 75th percentile of real users.
5. **Understood** — accurate titles, headings that match the content, structured data that
   describes what is visibly on the page.
6. **Worth citing** — first-hand expertise, evidence, a named author, and a claim nobody else made.

## What is measurable and modifiable in code

This is the part of SEO that belongs in a repository. Everything here is asserted in a file, and
verified by an API or a header rather than an opinion.

| Signal | Where it lives in code | How it is verified |
|---|---|---|
| Indexability | `robots.txt`, `<meta name="robots">`, `X-Robots-Tag` header | URL Inspection; `curl -I` |
| Canonical | `<link rel="canonical">`, redirects, sitemap entries | URL Inspection reports Google's chosen canonical |
| Status codes | router, middleware, error pages | `curl -sSI`; Search Console page-indexing report |
| Rendered content | SSR/SSG config, hydration, lazy-loading | Rich Results Test rendered HTML |
| Core Web Vitals | templates, image sizing, JS bundles, fonts | CrUX API (field), Lighthouse (lab only) |
| Structured data | JSON-LD blocks | Rich Results Test; Search Console enhancement reports |
| Product data | JSON-LD `Product`/`ProductGroup`, Merchant Center feed | Rich Results Test; Merchant Center diagnostics |
| Titles and metadata | head component per route | crawl diff; Search Console appearance data |
| Internal links | navigation, related-content components | crawl; click depth from the entry point |
| Link previews | Open Graph and `twitter:` tags | platform debuggers; `curl` for the tags |
| AI crawler access | `robots.txt` per user agent | server logs by user agent |

Two rules that catch most mistakes:

- **`robots.txt` is not `noindex`.** A blocked URL can still be indexed from external links; Google
  cannot read the `noindex` on a page it may not fetch. Use `noindex` and allow the crawl.
- **A lab score is not a Core Web Vitals result.** Lighthouse simulates one load on one machine;
  ranking systems and Search Console use field data from the Chrome UX Report.

## Rules that always hold

- One page, one primary intent, one canonical URL. Consolidate competing pages rather than tuning
  them against each other.
- Mark up only what is visible on the page. Structured data describing absent content is a policy
  violation and costs rich-result eligibility.
- Never present different content to crawlers than to people. That is cloaking regardless of intent.
- Do not generate pages at scale without added value, whether written by a model or a template. This
  is Google's scaled-content-abuse policy and it names generative AI explicitly.
- Prefer removing a weak page to rewriting it into a thin one.
- Report what a check returned, including "unchanged" and "cannot tell from here". An SEO
  recommendation nobody can verify is indistinguishable from a guess.

## Read the reference the task needs

| Area | Read for |
|---|---|
| [Technical SEO](references/technical-seo.md) | Crawling, indexing, canonicals, hreflang, sitemaps, redirects, JavaScript rendering, images |
| [Core Web Vitals](references/core-web-vitals.md) | Thresholds, field versus lab, and the code change behind each metric |
| [Structured data](references/structured-data.md) | Which types still earn anything, the policies, and what was withdrawn in 2026 |
| [Content and on-page](references/content-and-onpage.md) | Titles, descriptions, headings, E-E-A-T, keyword mapping, internal linking |
| [Ecommerce](references/ecommerce.md) | Product and category pages, variants, facets, pagination, feeds, shopping surfaces |
| [AI search](references/ai-search.md) | AI Overviews, AI Mode, ChatGPT, Copilot: crawler control, what is documented, what is measured |
| [Social and brand](references/social-and-brand.md) | Open Graph and cards, what social actually does for search, brand mentions |
| [Measurement](references/measurement.md) | The APIs, exports, and thresholds that make a claim checkable |
| [Anti-patterns](references/anti-patterns.md) | Every named spam policy, and the tactics the evidence has retired |
| [Sources](references/sources.md) | The full citation basis, to audit or update any claim above |

## Audit output shape

One finding per problem, each naming a location, the evidence, and a verifiable fix.

```text
[HIGH] Product pages emit an identical <title>
Location: src/routes/products/[slug].tsx:24
Evidence: 412 URLs share "Shop | Acme"; Search Console reports 0 impressions on 380 of them.
Fix: Render "{product.name} — {category} | Acme" from the loader data.
Check: crawl the sitemap and assert unique titles; re-inspect three URLs after deploy.
```

Rank by expected impact, not by how easy the fix is, and say plainly when a finding is cosmetic.
