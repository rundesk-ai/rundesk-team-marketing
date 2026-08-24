# Technical SEO

Read this when auditing or changing how a site is crawled, indexed, canonicalized, or rendered.

## The three requirements

A page is eligible for Google Search only when all three hold
([Search Essentials: technical requirements](https://developers.google.com/search/docs/essentials/technical)):

1. **Googlebot is not blocked** — the page is publicly reachable and not disallowed.
2. **The page works** — Google receives HTTP `200`. Neither `4xx` nor `5xx` is indexed.
3. **The page has indexable content** — a supported file type, complying with the spam policies.

Verify with the URL Inspection tool rather than by reading the router. It reports the fetched status,
the rendered HTML, and Google's chosen canonical.

## Crawl control versus index control

These are different mechanisms and confusing them is the most common serious error in a technical
audit.

| Goal | Use | Do not use |
|---|---|---|
| Keep a URL out of the index | `noindex` (meta or `X-Robots-Tag`), and allow the crawl | `robots.txt` |
| Save crawl budget on worthless URLs | `robots.txt` `Disallow` | `noindex` alone |
| Remove a URL urgently | Removals tool, then `noindex` or `410` | either alone |
| Consolidate duplicates | `rel="canonical"` or a redirect | `noindex`, `robots.txt` |

Google states plainly that blocking with `robots.txt` "prevents crawling, but URLs may still appear
in results; use the `noindex` directive to prevent actual indexing while allowing crawl access."
A `noindex` on a page Google is forbidden to fetch is a directive Google never reads.

Google also explicitly warns against using `robots.txt` or the removal tool for canonicalization, and
against using `noindex` instead of `rel="canonical"` to manage duplicates within a site
([Consolidate duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)).

## Canonicalization

Google's signals, in its own stated order of strength:

1. **Redirects** — "a strong signal that the target of the redirect should become canonical".
2. **`rel="canonical"`** — "a strong signal that the specified URL should become canonical".
3. **Sitemap inclusion** — "a weak signal".

Google also prefers HTTPS automatically, and prefers URLs that link reciprocally within an hreflang
cluster.

Rules for `rel="canonical"`:

- Use **absolute** URLs. Relative paths and fragment identifiers are invalid as canonicals.
- Place it in `<head>` only, once. A second one on the page is a conflict.
- Make it **self-referential** on the canonical page itself.
- Serve it as an HTTP `Link:` header for non-HTML files such as PDFs.
- Keep every method in agreement. Contradicting canonical, sitemap, and internal links is how a site
  ends up with Google choosing a URL nobody intended.
- Link internally to the canonical, never to the variant.

A canonical is a hint, not a directive. When Google's chosen canonical differs from the declared one,
the URL Inspection tool says so, and the cause is almost always a contradiction in the list above.

## Redirects and status codes

- Use permanent redirects to deprecate a duplicate. Google states all permanent redirection methods
  have the same effect on Search.
- Keep chains short and never loop. Each hop is another fetch and another chance to lose the signal.
- Return `404` or `410` for content that is gone. A page that returns `200` with "not found" text is
  a soft 404, and Google will class it as such.
- Never redirect a removed page to the homepage in bulk. Google treats an irrelevant redirect target
  as a soft 404.

## Sitemaps

From [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap):

- **Limits:** 50MB uncompressed or 50,000 URLs per file. Split beyond that and use a sitemap index.
- **`<priority>` and `<changefreq>` are ignored.** Emitting them is wasted bytes.
- **`<lastmod>` is used only when "consistently and verifiably accurate"**, and must reflect a
  significant update — content, structured data, or links. Bumping it on every build to look fresh
  teaches Google to ignore the field for the whole site.
- Include **only canonical, fully-qualified URLs**. No redirect targets, no paginated duplicates, no
  non-canonical variants.

Generate sitemaps from the same source of truth that decides `noindex` and canonical, or the three
will drift apart.

## hreflang

From [Localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions):

- Three delivery methods: HTML `<link rel="alternate">`, an HTTP `Link:` header, or XML sitemap
  `<xhtml:link>` entries. Pick one and use it everywhere.
- **Return links are mandatory.** "If page X links to page Y, page Y must link back to page X."
  A one-way annotation is ignored.
- Language is ISO 639-1; region is optional and ISO 3166-1 Alpha 2. **Region alone is not valid.**
- `UK`, `EU`, and `UN` are not valid region codes. The United Kingdom is `GB`.
- Use `x-default` for the fallback served to users matching no localized version.

Every page in a cluster must reference every other page in the cluster, including itself. This is
best generated, never hand-maintained.

## JavaScript rendering

From [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics):

Google processes in three phases — **crawling, rendering, indexing** — with rendering queued
separately. Rules that break indexing when violated:

- **Links must be `<a>` elements with an `href`.** "Google can only discover your links if they are
  `<a>` HTML elements with an `href` attribute." A `div` with a click handler is not a link.
- **Only `200` responses enter the rendering queue.**
- **Do not block JS or CSS in `robots.txt`.** "Google Search won't render JavaScript from blocked
  files," and the result is a page indexed as its empty shell.
- **Route with the History API, not fragments.** `#/page` URLs are not discovered.
- **Handle SPA not-found states.** Redirect to a URL that returns `404`, or inject
  `<meta name="robots" content="noindex">`; otherwise every miss is a soft 404.
- **One `rel="canonical"` and one robots meta tag per page.** Conflicting tags injected by both the
  server and the client "may lead to unexpected results."
- Use content fingerprinting on bundles so a deploy invalidates cached JS.

Server-side rendering or pre-rendering remains the safe default; Google's own documentation says it
"is still a great idea." Always confirm against the rendered HTML rather than assuming the hydration
worked.

## Lazy loading, images, and video

- Lazy loading must load content **when it enters the viewport**. An implementation that waits for a
  scroll event that a crawler never fires hides the content entirely
  ([Fix lazy-loaded content](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading)).
- **Never set `loading="lazy"` on an above-the-fold image.** web.dev is explicit that delaying the
  request "will likely have a massive negative impact on your LCP score."
- Alt text is the primary metadata for an image: informative, in context, not a keyword list. It is
  also the accessibility requirement, which is why it is worth getting right twice over.
- Descriptive filenames beat `IMG00023.JPG`. Place images near the text they illustrate.
- For video, embed on a standalone page with relevant surrounding text and use `<video>`, `<embed>`,
  `<iframe>` or `<object>` — Google finds videos through those elements.

## Site structure

- Group related content in directories. Google uses directory structure to learn how often URLs in a
  section change, which matters once a site exceeds a few thousand URLs.
- Keep important pages within a shallow click depth of an entry point.
- Sitemaps prioritize crawling but do not restrict it; they are not a substitute for internal links.
- Indexing is mobile-first: Google crawls with the smartphone agent and indexes what that agent
  receives. Content hidden from the mobile layout is content that may not be indexed at all.

## Sources

- [Google Search Essentials — technical requirements](https://developers.google.com/search/docs/essentials/technical)
- [Consolidate duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Localized versions of your pages](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
- [Fix lazy-loaded content](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading)
- [Image SEO best practices](https://developers.google.com/search/docs/appearance/google-images)
- [Video SEO best practices](https://developers.google.com/search/docs/appearance/video)
- [Mobile-first indexing best practices](https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing)
