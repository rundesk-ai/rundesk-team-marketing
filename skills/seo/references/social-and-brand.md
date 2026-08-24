# Social, link previews, and brand signals

Read this when asked about social metadata, share cards, or whether social activity helps search.

## Social is not a ranking factor, and the reason matters

Google has answered this repeatedly and consistently. Asked whether social signals affect organic
rankings, John Mueller: "Not directly, no." Gary Illyes, asked whether views and shares are ranking
signals, said no and gave the reason: **"we need to be able to control our own signals."** A metric
Google does not own is a metric anyone can buy.

Mueller on social meta tags for on-page SEO: "No, I'd use links to social media as a way to add value
to users, not in the hope that they improve rankings." And on traffic sources generally: "It's good
to have multiple separate sources of traffic to your website, and not everything needs to have an SEO
effect."

Treat any proposal to "build social signals for SEO" as based on a false premise, and say so.

## What social activity does do

Three real, indirect mechanisms — worth pursuing on their own terms, not as a ranking hack:

1. **Discovery and links.** Content that circulates gets found by people who cite it from sites that
   do pass signals. The link is the mechanism; the share is upstream of it.
2. **Branded search.** People who encounter a brand socially later search for it by name. Branded
   search volume correlates with AI visibility (0.352–0.466 across platforms in Ahrefs' 75,000-brand
   study), and it is demand that no competitor can outrank.
3. **Entity clarity.** Consistent profiles, declared via `sameAs` on `Organization` markup, help
   search and AI systems resolve which "Acme" this is.

## Brand mentions and AI visibility

This is where the social/brand question has genuinely changed, and it is worth separating from the
ranking-factor question above.

Ahrefs measured 75,000 brands across ChatGPT, AI Mode and AI Overviews (Spearman correlation):

| Factor | Correlation with AI visibility |
|---|---|
| YouTube mentions | 0.737 |
| YouTube mention impressions | 0.717 |
| Branded web mentions | 0.656–0.709 |
| Branded anchors | 0.511–0.628 |
| Branded search volume | 0.352–0.466 |
| Branded traffic | 0.235–0.357 |
| Domain Rating | 0.266–0.326 |
| Backlink count | very weak (~0.218 in the AI Overviews study) |

Read this carefully before repeating it:

- It is **correlational**. The authors state directly that "correlation isn't causation" and that
  improving these metrics will automatically boost AI visibility "remains unproven." Large,
  well-known brands score highly on all of these simultaneously; the study cannot separate the cause.
- The useful inference is a **relative** one: being *talked about* tracks AI visibility considerably
  better than being *linked to*. That is a genuine shift from a decade of link-centric practice, and
  it is directionally consistent with how retrieval-augmented systems assemble an answer.
- Google explicitly warns against acting on this crudely: "Seeking inauthentic 'mentions' isn't as
  helpful as it might seem."

The defensible programme is: publish things worth referencing, get covered by publications and
communities that AI systems actually retrieve from, maintain accurate reference-site entries, and
put substantive material on video where the correlation is strongest. Not: buy mentions.

## Link previews: Open Graph and cards

Open Graph is what turns a URL into a card on LinkedIn, Slack, Discord, Facebook, WhatsApp, iMessage,
Telegram, X, and most AI chat surfaces that unfurl links. It is cheap, entirely code-controlled, and
routinely broken.

```html
<meta property="og:title"       content="Distinct, human-readable title">
<meta property="og:description" content="One or two sentences that read as a promise, not a summary.">
<meta property="og:url"         content="https://example.com/page">   <!-- canonical, absolute -->
<meta property="og:image"       content="https://example.com/og/page.png">  <!-- absolute -->
<meta property="og:image:alt"   content="What the image shows">
<meta property="og:type"        content="article">
<meta property="og:site_name"   content="Acme">

<meta name="twitter:card"  content="summary_large_image">
<meta name="twitter:title" content="Distinct, human-readable title">
<meta name="twitter:image" content="https://example.com/og/page.png">
```

Rules that cause most breakage:

- **Absolute `https://` URLs only.** Social crawlers cannot resolve relative paths and do not
  authenticate.
- **1200 × 630 px, 1.91:1.** Renders correctly across the major platforms.
- `og:url` should be the canonical URL, so shares of tracking-parameter variants consolidate.
- `twitter:` tags fall back to `og:` when absent, so Open Graph alone produces a card on X. Set both
  only where the platforms should genuinely differ. Note that X's public card documentation has been
  folded into a generic developer overview and its Card Validator now requires sign-in — treat
  [ogp.me](https://ogp.me/) as the specification and test by posting a draft.
- **These tags must be in the initial server response.** A crawler that does not execute JavaScript
  sees no card; this is the single most common failure on client-rendered sites.
- Platforms cache aggressively. After a fix, re-scrape via each platform's debugger — Facebook's
  Sharing Debugger, X's Card Validator, LinkedIn's Post Inspector — or the old card persists.

**One SEO-adjacent detail:** Google names `og:title` among the sources it draws on when generating a
title link. An `og:title` that contradicts the `<title>` gives Google another candidate to prefer.
Keep them consistent unless there is a reason not to.

## What to check

```sh
curl -sS https://example.com/page | grep -iE 'og:|twitter:'
```

If that returns nothing but the browser shows the tags, they are being injected client-side and no
platform will see them.

## Sources

- [Google again says: we don't use social media for ranking](https://www.seroundtable.com/again-google-doesnt-use-social-media-for-ranking-22200.html)
- [Google explains why they need to control ranking signals](https://www.searchenginejournal.com/google-explains-why-they-need-to-control-their-ranking-signals/553657/) — Illyes on why social will not be used
- [Are social signals and shares a Google ranking factor?](https://www.searchenginejournal.com/ranking-factors/social-signals-rankinng-factor/)
- [Ahrefs: top brand visibility factors in ChatGPT, AI Mode and AI Overviews](https://ahrefs.com/blog/ai-brand-visibility-correlations/) — 75,000 brands
- [Ahrefs: an analysis of AI Overview brand visibility factors](https://ahrefs.com/blog/ai-overview-brand-correlation/)
- [The Open Graph protocol](https://ogp.me/) — the specification the `og:` tags come from
- [Influencing your title links in search results](https://developers.google.com/search/docs/appearance/title-link) — `og:title` as a title source
- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) — on inauthentic mentions
