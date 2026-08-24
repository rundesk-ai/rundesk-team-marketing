# Anti-patterns

Read this before recommending a tactic, and when auditing a site that has lost traffic suddenly.

Two categories: things Google will penalize, and things that simply do not work. Both waste a budget;
only the first also causes damage.

## Google's spam policies, in full

Violating these can remove a site from results entirely or demote it. From
[Spam policies for Google web search](https://developers.google.com/search/docs/essentials/spam-policies):

| Policy | What it is |
|---|---|
| **Cloaking** | Showing different content to users and search engines to manipulate rankings |
| **Doorway abuse** | Multiple near-identical pages or sites targeting query variations, funnelling to one destination |
| **Expired domain abuse** | Buying an expired domain for its history and putting unrelated low-value content on it |
| **Hacked content** | Content injected through a security vulnerability |
| **Hidden text and link abuse** | White-on-white text, off-screen positioning, zero opacity |
| **Keyword stuffing** | Unnatural repetition or keyword lists |
| **Link spam** | Buying or selling links, exchanges, automated links, low-quality directories, paid advertorials passing credit |
| **Machine-generated traffic** | Automated querying of Google, including rank scraping without permission |
| **Malicious practices** | Malware, unwanted software, back-button hijacking |
| **Misleading functionality** | Promising content or a service the site cannot provide |
| **Scaled content abuse** | Generating many pages without adding value — explicitly including generative AI |
| **Scraping** | Republishing others' content with little or no original value |
| **Site reputation abuse** | Third-party content published on a host site mainly for the host's ranking signals |
| **Sneaky redirects** | Sending users somewhere other than what was crawled or expected |
| **Thin affiliation** | Affiliate pages with merchant-supplied descriptions and no original value |
| **User-generated spam** | Spam in comments, forums, profiles, uploads |

### The three worth understanding in detail

**Scaled content abuse** is the one most likely to be committed accidentally today. Google's wording:
"Using generative AI tools or other similar tools to generate many pages without adding value for
users." The trigger is **scale without value**, not the use of a model. Programmatic pages built from
a real dataset that users want are fine; a thousand near-identical location or question pages are
not. If a project plan involves generating pages per keyword, this is the policy it will meet.

**Site reputation abuse** — "parasite SEO" — is publishing third-party content on an established
domain "mainly because of that host site's already-established ranking signals." Google is clear that
third-party content is not itself a violation, and has since clarified that first-party oversight
does not exempt content whose primary purpose is exploiting the host's signals. It is enforced by
**manual action**, not algorithmically; major publishers including Forbes, The Wall Street Journal,
Time and CNN received penalties from November 2024, and enforcement has continued in Europe. If a
client is hosting a coupons or reviews section run by a third party, this is the exposure.

**Link spam** covers "advertorials or native advertising where payment is received for articles that
include links that pass ranking credit." Sponsored placements need `rel="sponsored"` or
`rel="nofollow"`. This is the single most common thing an agency will propose that is against policy.

### Structured data has its own penalty

Marking up invisible, irrelevant, or misleading content triggers a **manual action removing
rich-result eligibility**. Google states it does not affect ordinary web ranking. Check the Manual
Actions report before assuming a rich-result loss was algorithmic — and note that FAQ and HowTo
results disappearing in 2026 was a product withdrawal, not a penalty. See
`references/structured-data.md`.

## Tactics the evidence has retired

Not penalties — just work that does not produce the claimed result.

| Tactic | Why it fails |
|---|---|
| `llms.txt` for AI visibility | Ahrefs found **97% of `llms.txt` files across 137,210 domains received zero requests** in May 2026. Google's Illyes and Mueller have both said Google does not support it and does not plan to; Google's AI guide says such files "will neither harm nor help your site's visibility". Harmless, but not a deliverable |
| Chunking content for AI | "There's no requirement to break your content into tiny pieces" |
| Writing in a special style for AI | "You don't need to write in a specific way just for generative AI search" |
| Structured data as an AI ranking lever | "Structured data isn't required for generative AI search" |
| A page per keyword variation | Retrieval understands synonyms; the variants compete with each other instead |
| `<meta name="keywords">` | Unused for two decades |
| Exact-match keyword density targets | Not how any modern retrieval system scores text |
| `rel="next"`/`rel="prev"` | "Google no longer uses these tags" |
| FAQ / HowTo markup for rich results | Both withdrawn from Google Search — see `references/structured-data.md` |
| `<priority>` and `<changefreq>` in sitemaps | "Google ignores" both |
| Buying "social signals" | Never a ranking factor; Illyes: "we need to be able to control our own signals" |
| Chasing 100/100 Lighthouse | Lab score, not the field measurement rankings use |
| Domain Authority as a goal | A vendor metric. Google does not have or use one |
| Blocking `GPTBot` to protect AI visibility | Wrong bot. `OAI-SearchBot` governs ChatGPT search inclusion; blocking *it* is what removes the site |

## Process anti-patterns

The ways an SEO engagement itself goes wrong:

- **Advising from the template instead of the URL.** Audit what the server returns and what renders.
- **Reporting a lab score as a Core Web Vitals result.**
- **Citing a vendor correlation as a cause.** Say "correlates with", give the sample, name the study.
- **Recommending a change with no way to verify it.** Every finding needs a check.
- **Bulk-redirecting removed pages to the homepage.** Treated as soft 404s; the equity is lost anyway.
- **Fixing content before indexation.** A page Google will not index cannot be improved into ranking.
- **Making many changes at once, then attributing the outcome to the favoured one.**
- **Claiming a recovery timeline.** Nobody can promise one, and the honest answer — "indexing in
  days, ranking effects over weeks, contaminated by any core update in between" — is more useful.
- **Treating "GEO"/"AEO" as a separate discipline with a separate budget.** Google's position:
  "optimizing for generative AI search is optimizing for the search experience, and thus still SEO."

## Sources

- [Spam policies for Google web search](https://developers.google.com/search/docs/essentials/spam-policies)
- [Updating our site reputation abuse policy](https://developers.google.com/search/blog/2024/11/site-reputation-abuse)
- [Google site reputation abuse policy now includes first-party involvement](https://searchengineland.com/google-site-reputation-abuse-policy-now-includes-first-party-involvement-or-oversight-of-content-448432)
- [Google sending manual actions for site reputation abuse in Europe](https://searchengineland.com/google-manual-actions-site-reputation-abuse-europe-451046)
- [Structured data general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Ahrefs: 97% of llms.txt files never get read](https://ahrefs.com/blog/llmstxt-study/)
- [Google says llms.txt is purely speculative for now](https://www.searchenginejournal.com/google-says-llms-txt-is-purely-speculative-for-now/577576/)
- [John Mueller rebuts the idea that Google uses a domain authority signal](https://www.searchenginejournal.com/domain-authority/246515/)
- [Qualify your outbound links to Google](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)
