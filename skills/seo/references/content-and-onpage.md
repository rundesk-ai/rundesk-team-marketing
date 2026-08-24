# Content and on-page

Read this when writing or auditing titles, descriptions, headings, page copy, keyword targeting, or
internal links.

## Titles: what Google actually does

Google generates the title link on the results page automatically, drawing on the `<title>` element,
the main visual title, `<h1>`, `og:title`, prominent styled text, anchor text, and links pointing to
the page ([Title links](https://developers.google.com/search/docs/appearance/title-link)).

**Google rewrites titles.** The documented triggers are:

- the `<title>` is empty or partly missing;
- it is stale relative to the visible content;
- it is inaccurate;
- it is boilerplate repeated across pages;
- its language differs from the page's;
- the page has several equally prominent headings, so the main one is unclear;
- the site name is redundant.

Every one of those is a repository-level defect with a repository-level fix. A rewritten title is
diagnostic information, not bad luck.

**On length:** Google states there is no limit on the `<title>` element; results truncate to fit the
device width. The familiar "50–60 characters" is a *display* heuristic for the desktop SERP, not a
rule, and pixel width — not character count — is what truncates. Use it as a soft target for the part
that must survive truncation, and put the distinguishing words first. Do not truncate a title that
reads correctly just to hit a number.

Practical form:

```text
{Distinguishing thing} — {qualifier a searcher would type} | {Brand}
```

Google's own advice: every page has a `<title>`; make it descriptive and concise; brand it
concisely; avoid keyword stuffing and boilerplate; match the page's language.

## Meta descriptions

Not a ranking factor, and frequently rewritten from page content to match the query. Still worth
writing, because it is the copy under the link when Google does use it, and because it is what most
social and chat surfaces fall back to.

- Roughly 120–160 characters survives on most result layouts.
- Describe the page honestly. A description promising something the page does not deliver costs the
  click twice: once on the bounce, and again on the next impression.
- Unique per page. A templated description across a section is a description Google will discard.
- Never leave it to a CMS default that emits the first 160 characters of boilerplate navigation.

## Headings

- One `H1` per page, stating what the page is.
- `H2`/`H3` reflect the real content hierarchy. Do not choose a level for its font size; style with
  CSS.
- Headings are how both a screen reader and a retrieval system segment a page. A page whose headings
  read as a coherent outline on their own is a page that survives being summarized.

## Helpful, people-first content and E-E-A-T

Google's guidance ([Creating helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content))
is a self-assessment, not a checklist to game. The questions that discriminate hardest:

- Does it provide **original** information, research, or analysis?
- Does it offer insight beyond the obvious?
- Is the sourcing and are the author credentials clear?
- Is it created by demonstrable experts or experienced enthusiasts?
- Would somebody bookmark, share, or recommend it?
- Does it contain easily-verified factual errors?

**E-E-A-T is Experience, Expertise, Authoritativeness, Trustworthiness.** Google states: "Of these
aspects, trust is most important. The others contribute to trust, but content doesn't necessarily
have to demonstrate all of them."

The parts that are implementable rather than aspirational:

- A byline, on every editorial page, linking to a bio that establishes why this person can say this.
- First-hand evidence: original data, screenshots, measurements, a thing actually done. This is the
  "Experience" that a model cannot synthesize and the one durable advantage over generated content.
- Citations to primary sources, with dates.
- A visible last-reviewed date that is true.
- Contact and ownership information that a reader can check.

**On AI-generated content**, Google's rules are two and they are precise:

1. Disclosure question: "Is the use of automation, including AI-generation, self-evident to visitors
   through disclosures or in other ways?"
2. The hard line: "If you use automation, including AI-generation, to produce content for the primary
   purpose of manipulating search rankings, that's a violation of our spam policies."

Google does not penalize AI assistance as such. It penalizes scaled, value-free output — see
`references/anti-patterns.md`.

## Keyword mapping without cannibalization

1. Define the **intent** the page serves, in one sentence, before looking at a keyword tool.
2. Gather the real variants people use, including the phrasings that do not contain the head term.
3. Prioritize by intent match and business value, not by volume alone.
4. Map **one primary theme to one URL**. Write the map down; it is the artifact that prevents the
   next problem.
5. Detect cannibalization from Search Console: query the URLs ranking for one query over time. Two
   URLs alternating on the same query is the signature, and it costs both.
6. Resolve it by consolidating with a redirect and a canonical, not by making the pages "more
   different" — the second-best page rarely earns its own intent.

Modern retrieval matches meaning, not strings. Google states its systems "can understand synonyms and
general meanings," so the exact-phrase discipline of a decade ago is counterproductive. Write the
sentence a person would write.

## Internal linking

The most under-used lever that is entirely under a repository's control.

- Links must be `<a href>`. Anything else is not a link to a crawler.
- Anchor text should describe the destination. "Learn more" transfers no information about the target
  page; the phrase somebody would search for does.
- Link *to* the pages that need authority *from* the pages that have it — usually the homepage, the
  main hub pages, and whatever ranks best today.
- Backfill: when a new page ships, add links to it from existing relevant pages in the same change.
  A page that only the sitemap points to is an orphan with a URL.
- Keep important pages shallow. Click depth from an entry point is a proxy for how much the site
  itself says the page matters.
- Link to the canonical URL, never to a parameterized or redirecting variant.

## Content maintenance

- Consolidate or remove thin pages rather than rewriting each into slightly-less-thin ones.
- Update a page when the world changed, and let `dateModified` reflect that honestly. A refresh that
  only touches the date is the pattern Google learns to discount.
- Removing a genuinely obsolete page and returning `410` is a legitimate, sometimes beneficial act.

## Sources

- [Influencing your title links in search results](https://developers.google.com/search/docs/appearance/title-link)
- [Control your snippets in search results](https://developers.google.com/search/docs/appearance/snippet)
- [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [SEO link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)
- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) — on synonyms and on not writing for machines
