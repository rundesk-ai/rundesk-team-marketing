# Structured data

Read this before adding, auditing, or removing schema markup. Most schema advice in circulation is
several deprecations out of date.

## The policies come before the syntax

From [Structured data general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies):

- **JSON-LD is the recommended format.** Microdata and RDFa are supported; JSON-LD is the one to
  write.
- **"Don't mark up content that is not visible to readers of the page."** This is the rule most
  violated and the one with a real penalty attached.
- **"Don't mark up irrelevant or misleading content, such as fake reviews or content unrelated to
  the focus of a page."**
- Do not block marked-up pages from Googlebot with `robots.txt`, `noindex`, or any access control.
- Provide every required property. Recommended properties improve the odds, never guarantee them.

**Penalty shape:** a violation triggers a manual action that removes rich-result eligibility. Google
states it does not affect ordinary web ranking. Check the Manual Actions report in Search Console.

**Nothing guarantees a rich result.** Correct markup makes a page eligible. Google decides
algorithmically whether to show one, and that decision can change without notice — as the 2026
withdrawals below demonstrate.

## What was withdrawn, and when

Google has been actively reducing the number of rich result types. Do not spend effort on these:

| Type | Status |
|---|---|
| `FAQPage` | Rich results stopped appearing **7 May 2026**. Search appearance, rich result report and Rich Results Test support dropped June 2026; Search Console API support ends August 2026. Documentation now limits the feature to well-known, authoritative government and health sites. |
| `HowTo` | Removed from Search on desktop and mobile; no longer in the gallery. |
| Practice problems | Removed from Search Console reporting and the Rich Results Test from January 2026. |
| Course info, Claim review, Estimated salary, Learning video, Special announcement, Vehicle listing | Search Console reporting support removed. |

Google's position on markup already deployed is that it may be left in place: "Other search engines
may be able to continue to process it and use it for their own purposes." Removing it is optional
housekeeping, not a fix. What is **not** optional is ceasing to recommend it, and correcting any plan
that budgets work for FAQ or HowTo markup on the basis of a Google rich result.

## What is still documented as supported

Article · Breadcrumb · Carousel · Course list · Dataset · Discussion forum · Education Q&A · Employer
aggregate rating · Event · Image metadata · Job posting · Local business · Math solver · Movie ·
Organization · Product · Profile page · Q&A · Recipe · Review snippet · Software app · Speakable ·
Subscription and paywalled content · Vacation rental · Video
([Structured data gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery)).

Check the gallery before recommending a type. This list is a snapshot and the direction of travel is
downward.

## What to actually deploy

For most sites, four types carry nearly all the value:

```jsonc
// Site-wide, on the homepage: who this is
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Acme",
  "url": "https://acme.example",
  "logo": "https://acme.example/logo.png",
  "sameAs": ["https://www.linkedin.com/company/acme", "https://github.com/acme"]
}
```

```jsonc
// Editorial pages: who wrote it and when — the machine-readable half of E-E-A-T
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "The visible H1, verbatim",
  "datePublished": "2026-08-06",
  "dateModified": "2026-08-06",
  "author": {
    "@type": "Person",
    "name": "A Named Human",
    "url": "https://acme.example/authors/a-named-human"   // must resolve to a real bio page
  },
  "publisher": { "@type": "Organization", "name": "Acme" }
}
```

```jsonc
// Interior pages: BreadcrumbList, matching the visible breadcrumb trail
// Commerce: Product with Offer — price and availability must match what the page shows
```

`sameAs` on `Organization` is the cheapest entity signal available and is worth setting properly: it
is how a site asserts which social and reference profiles are the same entity.

## Rules that keep markup honest

- **Generate it from the same data the template renders.** Markup hand-written beside a dynamic page
  drifts within one sprint, and drifted markup is the policy violation.
- `headline` matches the visible `H1`. `datePublished` matches the visible date. `price` matches the
  price on the page, in the same currency.
- `dateModified` must reflect a real change. Touching it every build is the same dishonesty as a
  sitemap `lastmod` that always says today, and it is equally likely to be discounted.
- An `author` must be a real, identifiable person with a bio page that resolves. An `author` of
  `"Admin"` or the brand name asserts nothing.
- Do not stack review markup a page did not earn. Self-serving review snippets on a company's own
  page for its own product are outside the review snippet policy.
- Validate every change: the Rich Results Test for eligibility, the Schema Markup Validator for
  syntax, then the Search Console enhancement report a few days later for the population-level view.

## Does structured data help AI answers?

Google says it is not required: "Structured data isn't required for generative AI search." Deploy it
because it earns rich results, describes entities unambiguously, and costs little — not on the theory
that it buys AI citations. See `references/ai-search.md` for what the evidence supports there.

## Sources

- [Structured data general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [Structured data markup that Google Search supports](https://developers.google.com/search/docs/appearance/structured-data/search-gallery)
- [Changes to HowTo and FAQ rich results](https://developers.google.com/search/blog/2023/08/howto-faq-changes)
- [Simplifying the search results page](https://developers.google.com/search/blog/2025/06/simplifying-search-results)
- [Google to no longer support FAQ rich results](https://searchengineland.com/google-to-no-longer-support-faq-rich-results-476957) — Search Engine Land, the May/June/August 2026 timeline
- [Google to remove more search features](https://searchengineland.com/google-to-remove-more-search-features-including-practice-problems-nutrition-facts-nearby-offers-and-more-464255)
- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
