# Ecommerce and product pages

Read this for product pages, category and listing pages, faceted navigation, variants, and shopping
surfaces including AI shopping agents.

Ecommerce is where technical SEO fails hardest, because a catalogue multiplies every mistake by the
number of products and every filter combination by every other filter combination.

## Product data reaches Google three ways, and they are not alternatives

From [Share your product data with Google](https://developers.google.com/search/docs/specialty/ecommerce/share-your-product-data-with-google):

| Method | Best for | Note |
|---|---|---|
| **Structured data on the page** | Rich results, and accuracy of price, discount and shipping in Search | Depends on the page being crawled, which is never guaranteed |
| **Merchant Center feed** | Complete catalogue coverage, scheduled updates, data not on the site (store-level inventory) | Required for the Shopping tab |
| **Merchant API / Content API** | Real-time updates, "particularly useful for stock level updates" | The right answer for volatile inventory |

Use structured data **and** a feed. Google uses the page to verify the feed and can auto-update its
copy of product data from page contents, which is what prevents a feed showing a price the page
contradicts. A price mismatch between feed and page is a common cause of disapproved items.

## Product structured data

Two distinct experiences, and picking the wrong one wastes the markup
([Intro to product structured data](https://developers.google.com/search/docs/appearance/structured-data/product)):

- **Product snippets** — for pages where a customer *cannot* buy directly (editorial reviews,
  comparisons). More options for review information, including pros and cons.
- **Merchant listings** — for pages where a customer *can* buy. More options for apparel sizing,
  shipping detail, and return policy.

Requirements and rules:

- Required core: `name`, `image`, `offers` with `price`, `priceCurrency`, and `availability`.
- Automatic item updates require `price`, `priceCurrency`, `availability` and `condition` in the
  markup.
- **Variants** use `ProductGroup` with `variesBy`, `hasVariant`, and `productGroupID` alongside
  `Product`. This is what makes products eligible to show with variant information, and it is the
  only way to tell Google that six URLs are one product in six colours rather than six products.
- **Shipping** times need a minimum and maximum in days via `QuantitativeValue`.
- **Returns** can be declared at product level or organization level; where both exist Google uses
  the product-level policy. Shipping and return policies can alternatively be set in Search Console.
- Nest `Organization` data for return policies and loyalty programs.
- Everything marked up must match what the page displays. A marked-up price that differs from the
  rendered price is a structured data policy violation, not a rounding issue.

Google's own framing is to supply as much accurate product information as exists rather than
targeting a particular result format, because the formats change.

## URL structure

From [Designing a URL structure for ecommerce sites](https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites):

- Use `?key=value`, never `?value`. `/frames?page=2`, not `/frames?2`.
- Do not repeat a parameter. `?type=candy,sweet`, not `?type=candy&type=sweet`.
- **Never link internally to session IDs, tracking codes, or time-based parameters.** They mint a
  fresh URL per visit and hand a crawler an infinite space.
- Give each variant its own URL — `/t-shirt/green` or `/t-shirt?color=green`.
- Where a variant parameter is optional, **canonicalize to the parameter-omitted URL**.
- Keep filter order and separators consistent, so the same selection is always the same string.

## Faceted navigation — the crawl trap

Google names the failure directly: crawlers "will typically access a very large number of faceted
navigation URLs" because they cannot tell whether a URL is useful without fetching it, and the
resource that consumes is resource not spent discovering real products
([Crawl management for faceted navigation](https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation)).

Solutions, strongest first:

1. **`robots.txt` disallow on filter parameters**, allowing the base category and product pages. The
   preferred option when facets need no search visibility.
2. **URL fragments for filters.** "If your filtering mechanism is based on URL fragments, it will
   have no impact on crawling (positive or negative)" — Google does not process fragments at all.
3. **`rel="canonical"` to the unfiltered URL.** Weaker; it "may, over time, decrease the crawl
   volume" rather than preventing it.
4. **`rel="nofollow"` on facet links.** Least effective, and only works if *every* anchor to that URL
   carries it — which in a component-driven storefront it will not.
5. **Return `404` for empty filter combinations**, not a redirect and not a soft 404.

Decide deliberately which facets deserve indexing. A small number of high-demand combinations
("waterproof hiking boots") can justify a real, indexable, linked landing page with its own copy. The
combinatorial tail should never be crawlable.

## Pagination

From [Pagination and incremental page loading](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading):

- **`rel="next"`/`rel="prev"` is dead.** "Google no longer uses these tags."
- Each page gets a **unique URL and its own self-referencing canonical**. Explicitly: "Don't use the
  first page of a paginated sequence as the canonical page."
- Link pages sequentially with real `<a href>` elements so page 2 onward is discoverable.
- **Never use fragments for page numbers** — Google ignores them.
- Infinite scroll and "load more" buttons rely on user-triggered JavaScript, and Google's crawlers
  "generally don't trigger JavaScript functions that require user actions." Provide paginated URLs
  underneath, plus sitemaps or a Merchant Center feed, or the tail of the catalogue is undiscovered.

## Inventory lifecycle

The question every catalogue eventually gets wrong: what happens to a URL when the product goes away.

| Situation | Do |
|---|---|
| Temporarily out of stock, returning | Keep the page live and indexed, `availability: OutOfStock`, show alternatives and a restock signal. Do not `noindex`, do not `404` — the ranking is an asset |
| Permanently discontinued, direct replacement exists | Permanent redirect to the replacement, only where it genuinely replaces it |
| Permanently discontinued, no replacement | Keep the page with a clear discontinued state and links to the category, or return `410` if there is nothing useful to say |
| Seasonal, returns annually | Keep one permanent URL. Never mint `/product-2026` |

Never bulk-redirect discontinued products to the homepage or a top-level category; Google treats an
irrelevant redirect target as a soft 404 and the equity is lost anyway.

## Category and listing pages

- A category page ranks on its own intent and needs its own reason to exist: a real description, a
  curated selection, internal links. A bare grid of tiles is a thin page.
- Put the copy where it helps a reader, not in a keyword block below the fold that exists only for
  crawlers.
- Faceted variants of a category are not additional category pages.
- Category pages are usually the highest-authority pages in a catalogue. Link from them deliberately.

## Reviews

- Review markup must reflect reviews the page actually shows.
- Do not aggregate site-wide ratings onto individual products.
- Google publishes review quality guidance for ecommerce; the short version is that a review has to
  contain evidence of use.
- Third-party review widgets that render client-side may not be in the rendered HTML at all. Check.

## Shopping and AI commerce surfaces

Beyond organic results, product data feeds free listings on the Shopping tab, Google Images
annotations, and — increasingly — assistant-driven shopping.

**Documented and stable:** a complete, accurate, frequently-updated Merchant Center feed is what
populates the shopping surfaces. Structured data keeps the page consistent with it. Both are ordinary
work with a clear mechanism.

**Emerging, and worth watching rather than betting on:** Google's own AI optimization guide points
ecommerce sites at Merchant Center feeds and Business Profiles for visibility in generative features,
and mentions the Universal Commerce Protocol and "agent-friendly website best practices" for browser
agents. Stripe and OpenAI publish a competing Agentic Commerce Protocol. ChatGPT Shopping and
Google's agentic checkout in AI Mode both exist in the US market.

Advise on this honestly:

- The durable investment is **structured, accurate, machine-readable product data with real-time
  price and stock** — a feed, an API, and matching on-page markup. Every protocol so far consumes
  that same substrate, so it is the work that does not get stranded.
- Editorial content about a product category does not put a product into an assistant's shopping
  answer the way a correct feed does.
- Protocol adoption is genuinely unsettled and vendor-specific. Do not recommend implementing a
  named agentic protocol without checking its current status and the merchant platform's support;
  most storefronts get this through Shopify, Stripe, or their platform rather than by hand.
- Market-size projections for agentic commerce are vendor forecasts, not measurements. Do not cite
  them as evidence for a technical decision.

## Ecommerce audit order

1. Are product pages indexable, `200`, and rendered server-side? Check a variant URL, not just the
   parent.
2. Is the faceted space crawlable? Count URLs in the Crawl Stats report against the real product
   count — the ratio is the finding.
3. Does every product have one canonical URL, and do internal links and the sitemap point at it?
4. Do feed, page, and structured data agree on price, currency, and availability?
5. Is `ProductGroup` variant markup present where variants exist?
6. What happens to a discontinued URL today? Test one.
7. Is pagination discoverable without JavaScript?
8. Do category pages carry unique, useful content?

## Sources

- [Ecommerce SEO](https://developers.google.com/search/docs/specialty/ecommerce)
- [Share your product data with Google](https://developers.google.com/search/docs/specialty/ecommerce/share-your-product-data-with-google)
- [Intro to product structured data](https://developers.google.com/search/docs/appearance/structured-data/product)
- [Merchant listing structured data](https://developers.google.com/search/docs/appearance/structured-data/merchant-listing)
- [Product variant structured data](https://developers.google.com/search/docs/appearance/structured-data/product-variants)
- [Merchant return policy structured data](https://developers.google.com/search/docs/appearance/structured-data/return-policy)
- [Designing a URL structure for ecommerce sites](https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites)
- [Crawl management for faceted navigation](https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation)
- [Pagination and incremental page loading](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)
- [Write high quality reviews](https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews)
- [Product data specification](https://support.google.com/merchants/answer/7052112) — Merchant Center feed attributes
- [Merchant Center product data specification update 2026](https://support.google.com/merchants/answer/16989427) — including the 500×500 minimum image resolution
- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) — Merchant Center, Business Profiles, UCP
