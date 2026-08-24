# Sources

Accessed 12 August 2026. Official standards and platform documentation establish contracts and
definitions. Practitioner studies and case reports expose recurring failures and empirical patterns;
their effect sizes remain scoped to their samples. The recommendations in this package synthesize
those sources and are not a promise of a universal conversion lift.

## Landing-page and campaign contracts

- [Google Ads Help: Optimize your ads and landing pages](https://support.google.com/google-ads/answer/6238826/optimising-your-ad-and-landing-page?hl=en-GB)
  establishes message match among keyword, ad, landing-page content, and CTA; clear differentiation;
  useful content; mobile friendliness; important information early; and easy completion. It is
  platform guidance, not an independent estimate of lift.
- [Google Ads Help: Landing page](https://support.google.com/google-ads/answer/14086?hl=en-419)
  defines landing-page experience through usefulness, relevance, navigation, links, and fulfillment
  of expectations from the ad. It supports treating acquisition and page as one contract.
- [Google Ads Help: CTR definition](https://support.google.com/google-ads/answer/2615875?hl=en)
  defines ad CTR as clicks divided by impressions and says a good CTR depends on the offer and
  network. It supports separating ad CTR from landing-page CTA rate and rejecting a universal CTR.
- [Google Ads Help: Use data to optimize Search campaigns](https://support.google.com/google-ads/answer/9451527?hl=en)
  distinguishes CTR, conversion rate, conversion value, cost per conversion, and ROAS. It supports
  optimizing value rather than raw counts.
- [Google Merchant Center: Landing-page requirements](https://support.google.com/merchants/answer/4752265?hl=en)
  requires an advertised product's title, description, image, price, currency, availability, variant,
  and buy action to remain consistent and discoverable on desktop and mobile. It supports preserving
  the exact advertised offer and variant; its crawler and product-feed requirements apply only when
  Merchant Center is in use.
- [Google Merchant Center: Inaccurate price caused by feed/landing-page mismatch](https://support.google.com/merchants/answer/9773429?hl=en)
  documents user expectation and platform failures when price, availability, selected variant,
  promotions, quantities, or mandatory handling costs disagree. It supports versioning and monitoring
  the offer instead of treating page copy as static.
- [Becker et al., “What Happens after an Ad Click? Quantifying the Impact of Landing Pages in Web Advertising”](https://www.cs.columbia.edu/~hila/papers/cikm09-becker.pdf)
  develops a sponsored-search landing-page taxonomy from a stratified 200-query pilot, then studies
  context transfer with conversion data for more than 31,000 query/landing-page pairs. Its 2009
  Yahoo dataset is observational and not a modern lead-form A/B test, but it independently supports
  matching campaign intent to an appropriate destination instead of defaulting specific traffic to
  a generic homepage.
- [Unbounce 2024 Conversion Benchmark Report](https://unbounce.com/conversion-benchmark-report/)
  reports 41,000 landing pages, 464 million unique visitors, and 57 million conversions, with a 6.6%
  cross-industry median and industry medians from 3.8% to 12.3%. Unbounce notes that conversion
  definitions and value differ. The self-selected Unbounce customer population, mixed offers and
  channels, and vendor interest make these context benchmarks, not quality targets or causal design
  evidence.

## Content, hierarchy, and action

- [W3C WAI: Writing for Web Accessibility](https://www.w3.org/WAI/tips/writing/)
  supports concise content, informative titles, meaningful link text, and short headings that expose
  document structure.
- [W3C WAI: Headings tutorial](https://www.w3.org/WAI/tutorials/page-structure/headings/)
  establishes semantic, nested headings as both page organization and assistive-technology
  navigation. It supports making each landing-page section recognizable from its heading.
- [Kara Pernice, NN/g: F-Shaped Pattern of Reading on the Web](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/)
  revisits NN/g eye-tracking observations, including an early aggregate heatmap from more than 45
  people. It explains that the F pattern is one negative response to weak formatting, not a universal
  layout template, and supports frontloaded headings, visible structure, bullets, and removing
  unnecessary content.
- [Katie Sherwin, NN/g: “Get Started” Stops Users](https://www.nngroup.com/articles/get-started/)
  uses observed usability examples to show that generic CTA language weakens information scent and
  expectation setting. It supports truthful, destination-specific action labels, not a universal
  wording formula or measured lead-gen lift.
- [Material Design 2: Buttons](https://m2.material.io/design/components/buttons.html)
  recommends one prominent button in a layout, lower emphasis for other actions, and labels that
  describe what the action does. This is practitioner design-system guidance, not landing-page lift
  evidence.
- [GOV.UK Design System: Button](https://design-system.service.gov.uk/components/button/)
  supports specific labels, one primary action, visible pending feedback, and protection from
  duplicate submission at both client and server boundaries. Its documented Notify incident links
  double-clicking to duplicate invitations; it does not prescribe one button position for marketing.

## Forms, errors, and completion

- [W3C WAI Forms Tutorial: Labeling controls](https://www.w3.org/WAI/tutorials/forms/labels/)
  establishes explicit form labels, purpose-oriented names, and the larger activation area created
  by associated labels. It supports the persistent-label good/bad pair.
- [W3C WAI Forms Tutorial: Multi-page forms](https://www.w3.org/WAI/tutorials/forms/multi-page/)
  recommends dividing long forms into logical stages when possible, indicating progress, exposing
  optional stages, avoiding time limits, and grouping related controls. It does not establish that
  multiple steps raise CVR for every form.
- [GOV.UK Design System: Question pages](https://design-system.service.gov.uk/patterns/question-pages/)
  directs teams to know why each question is asked, request only needed information, start with one
  question per page, preserve Back behavior, and avoid redundant entry. Its public-service context
  supports comprehension patterns, not a mandatory commercial funnel shape.
- [GOV.UK Design System: Recover from validation errors](https://design-system.service.gov.uk/patterns/validation/)
  supports tolerant input parsing, preserved answers, field-specific errors, linked summaries, and
  submit-time validation unless research supports earlier feedback.
- [GOV.UK Design System: Confirmation pages](https://design-system.service.gov.uk/patterns/confirmation-pages/)
  supports naming the completed transaction, showing a reference when useful, explaining next steps,
  and providing contact or recovery routes.
- [web.dev: Sign-up form best practices](https://web.dev/articles/sign-up-form-best-practices)
  supports cutting unnecessary fields, explicit action labels, browser autofill, truthful input
  types, testing across real devices, and minimizing data liability. Sign-up is adjacent to, not
  identical with, every lead form.
- [Baymard: Mobile form usability and inline labels](https://baymard.com/blog/mobile-forms-avoid-inline-labels)
  reports observed context loss and recovery problems from placeholder-like inline labels in
  Baymard's mobile e-commerce usability research. Its checkout population supports the failure mode,
  not a universal conversion percentage for lead forms.
- [Baymard: Required and optional form fields](https://baymard.com/blog/required-optional-form-fields)
  derives guidance from large-scale checkout usability testing and reports hesitation, errors, and
  abandonment when field requirements are ambiguous. Commerce scope and Baymard's commercial
  research model limit generalization; the skill retains the clearer `optional` labeling lesson.
- [Seckler et al., “Designing Usable Web Forms: Empirical Evaluation of Web Form Improvement Guidelines”](https://research.google/pubs/designing-usable-web-forms-empirical-evaluation-of-web-form-improvement-guidelines/)
  reports a controlled eye-tracking study with 65 participants; guideline-conforming forms produced
  faster completion, fewer trials and eye movements, and higher satisfaction. It supports clear
  labels, logical grouping, one primary completion action, and first-try recovery, while its task is
  not a direct lead-gen revenue experiment.
- [Dvir and Gafni, “How Content Volume on Landing Pages Influences Consumer Behavior”](https://arxiv.org/abs/1806.00923)
  reports two real-world landing-page experiments with 535 and 27,900 participants where reduced
  content improved email capture. Its email-offer context does not prove short pages always win; it
  supports removing redundant content while retaining the proof and objections needed for the
  actual decision.

## Mobile, accessibility, and performance

- [W3C Recommendation: WCAG 2.2](https://www.w3.org/TR/WCAG22/)
  establishes reflow, contrast, keyboard, visible and unobscured focus, input purpose, labels,
  errors, status messages, orientation, dragging alternatives, and a 24-by-24 CSS-pixel AA target
  size criterion with exceptions. Conformance requires more than automated inspection.
- [W3C WAI: Understanding Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow)
  explains the 320 CSS-pixel reflow requirement and warns that fixed content can obscure reading or
  focus. It supports the sticky-CTA and zoom checks.
- [web.dev: Sign-in form best practices](https://web.dev/articles/sign-in-form-best-practices)
  documents keyboard coverage, persistent labels, explicit button labels, stable field semantics,
  and autofill behavior on mobile. It supplies implementation evidence for the keyboard good/bad
  pair, not a lead-specific lift.
- [MDN: `autocomplete`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/autocomplete)
  defines browser field-purpose tokens and explains that appropriate values reduce typing and memory
  burden, including for people with cognitive or motor disabilities.
- [WHATWG HTML Living Standard: Forms](https://html.spec.whatwg.org/multipage/forms.html)
  defines native input types, `autocomplete`, and `inputmode`. It supports using platform semantics
  for keyboards and autofill and not using numeric controls for identifiers.
- [web.dev: How Core Web Vitals thresholds were defined](https://web.dev/articles/defining-core-web-vitals-thresholds)
  establishes current `good` thresholds of LCP <=2.5 seconds, INP <=200 milliseconds, and CLS <=0.1
  at the 75th percentile. These are user-experience thresholds, not CVR guarantees.
- [web.dev: The difference between lab and field data](https://web.dev/articles/lab-and-field-data-differences)
  explains that lab tests reproduce controlled conditions while field data represents real users,
  distributions, devices, and networks. It supports using lab tools for diagnosis and field data for
  the live performance contract.
- [web.dev: Top Core Web Vitals recommendations](https://web.dev/articles/top-cwv)
  supports discovering the LCP resource in initial HTML, not lazy-loading the LCP image, prioritizing
  it when appropriate, reserving image space, and reducing long tasks and third-party cost.
- [web.dev: Optimize LCP](https://web.dev/articles/optimize-lcp) and
  [Optimize CLS](https://web.dev/articles/optimize-cls)
  supply the current resource-discovery, prioritization, explicit-dimension, and reserved-space
  mechanics behind the hero and late-content good/bad pair.
- [web.dev: Browser-level image lazy loading](https://web.dev/articles/browser-level-image-lazy-loading)
  directs authors to lazy-load offscreen images and avoid lazy-loading images likely to be visible
  in the first viewport.
- [web.dev: Cookie notice best practices](https://web.dev/articles/cookie-notice-best-practices)
  documents how late consent UI and third-party work triggered by acceptance can regress LCP, CLS,
  and INP. It supports treating required consent UX as part of the page budget, not removing it.
- [Chrome for Developers: Reduce the impact of third-party code](https://developer.chrome.com/docs/lighthouse/performance/third-party-summary)
  documents that advertising, social, testing, and analytics scripts can block the main thread and
  describes measuring their cost. Its older Lighthouse audit moved in version 13; the underlying
  third-party execution risk remains, while the exact audit UI is not encoded in this skill.
- [Rakuten 24 Core Web Vitals case study](https://web.dev/case-studies/rakuten)
  reports a one-month 50/50 A/B test where the performance-optimized landing page loaded 0.4 seconds
  faster and showed a 33.13% conversion-rate increase, alongside other metric changes. The company
  case does not publish a transferable lead-gen sample or prove that this effect size applies
  elsewhere; the skill cites it only as an illustration that performance can be tested against
  business outcomes.
- [Renault Core Web Vitals case study](https://web.dev/case-studies/renault)
  analyzes December 2020 through March 2021 traffic to Renault landing pages and lead-form
  completions, reporting associations between better LCP, lower bounce rate, and more conversions.
  It is one organization's observational SPA dataset and does not establish a transferable effect
  size; it reinforces using field data and local causal testing.

## Trust, proof, and non-deceptive design

- [FTC: Consumer Reviews and Testimonials Rule Q&A](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers)
  explains the U.S. rule effective 21 October 2024 and routes businesses to endorsement guidance.
  It supports verifying testimonial authenticity and material relationships; it is not a general
  landing-page compliance checklist.
- [FTC: Final rule banning fake reviews and testimonials](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)
  identifies prohibited fake or false reviews, sentiment-conditioned incentives, undisclosed insider
  reviews, and company-controlled sites misrepresented as independent.
- [FTC staff report: Bringing Dark Patterns to Light](https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf)
  documents deceptive activity messages, fake scarcity, hidden costs, false hierarchy, disguised
  ads, and hidden subscription or data practices. It supports rejecting conversion tactics that
  manufacture urgency or obscure a material choice.
- [Baymard: Current state of checkout UX](https://baymard.com/blog/current-state-of-checkout-ux)
  summarizes Baymard's 2025 checkout benchmark and reports pronounced reluctance around unexplained
  phone-number requests. The checkout evidence is adjacent rather than identical to lead generation;
  it supports explaining surprising sensitive fields at the point of entry, not a universal lift.
- [Özpolat et al., “The Value of Third-Party Assurance Seals in Online Retailing: An Empirical Investigation”](https://pubsonline.informs.org/doi/10.1287/isre.2013.0489)
  reports a randomized field experiment at one online retailer with 9,098 sessions. It supports that
  relevant assurance can change behavior in a sensitive transaction; its checkout setting and one-
  retailer sample do not justify adding arbitrary badges to every lead page.
- [Özpolat and Jank, “Getting the Most out of Third Party Trust Seals”](https://digitalcommons.uri.edu/cba_facpubs/44/)
  analyzes more than 250,000 transactions across 493 retailers and reports that excessive seals can
  reduce completion. The observational commerce context supports a few meaningful trust signals
  over badge clutter, not a universal seal count.

## Measurement and experiments

- [Google Analytics: Measure ecommerce](https://developers.google.com/analytics/devguides/collection/ga4/ecommerce)
  defines a purchase funnel including item view, add/remove cart, checkout, purchase, promotions, and
  refund. It supports keeping purchase and refund distinct from CTA or checkout-start diagnostics;
  the application's order/payment lifecycle remains authoritative.
- [GA4 recommended events](https://support.google.com/analytics/answer/9267735?hl=en-EN)
  defines `generate_lead`, `qualify_lead`, `disqualify_lead`, `working_lead`,
  `close_convert_lead`, and `close_unconvert_lead` for lead-generation funnels. It supports measuring
  downstream lead status instead of form submission alone; the application remains the state owner.
- [Google Analytics: About key events](https://support.google.com/analytics/answer/9267568?hl=en)
  distinguishes event counts, session key-event rate, and attribution reports. It supports documenting
  the metric and scope rather than comparing unnamed `conversions`.
- [Google Analytics: Traffic-source dimension scopes](https://support.google.com/analytics/answer/11080067?hl=en)
  distinguishes first-user, session, and event attribution scopes. It supports recording the chosen
  scope and warning that differently scoped reports are not directly interchangeable.
- [Google Ads: Enhanced conversions for leads](https://support.google.com/google-ads/answer/15713840?hl=en_us_us)
  documents capturing approved first-party lead data, later importing offline outcomes, matching and
  attribution, and a 15 June 2026 Data Manager API migration. This volatile provider feature supports
  closing the CRM feedback loop, not a requirement to share lead PII or a legal conclusion.
- [PostgreSQL 18: PREPARE](https://www.postgresql.org/docs/18/sql-prepare.html)
  establishes parameterized prepared statements and explains that planning may vary with supplied
  parameter values. It supports binding report inputs rather than interpolating them; the skill
  still defers framework-specific binding syntax to the application's data layer.
- [PostgreSQL 18: Row Security Policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html)
  documents database-enforced per-role row access, default-deny behavior when row security is enabled
  without a policy, owner and `BYPASSRLS` exceptions, and policy race considerations. It supports
  routing multi-tenant measurement data through the project's database security design rather than
  relying on a generic `WHERE tenant_id = ...` example.
- [PostgreSQL 18: Multicolumn indexes](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
  explains that useful multicolumn index shape follows the query's predicates and operator class. It
  supports deriving campaign/variant/time indexes from actual report queries instead of prescribing
  one universal event-table index.
- [PostgreSQL 18: Using `EXPLAIN`](https://www.postgresql.org/docs/18/using-explain.html)
  documents estimated versus actual plans and that `EXPLAIN ANALYZE` executes the statement. It
  supports plan proof with representative parameters and the warning against casually analyzing
  write statements or production workloads.
- [Microsoft Research: Patterns of Trustworthy Experimentation — pre-experiment](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage)
  synthesizes more than 14 years of Microsoft experimentation work and supports an overall criterion,
  guardrails, feature metrics, and data-quality metrics before launch.
- [Microsoft Research: Patterns of Trustworthy Experimentation — during experiment](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-during-experiment-stage/)
  distinguishes data quality, overall evaluation, diagnostic, and guardrail metrics and supports
  prespecified duration with safety monitoring. Microsoft's typical seven-day example is not a
  universal minimum; the skill requires duration from cycles, power, and delayed outcomes.
- [Fabijan et al., “Diagnosing Sample Ratio Mismatch in Online Controlled Experiments”](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/)
  is a KDD 2019 practitioner paper based on work across four companies, more than 25 products, and
  hundreds of millions of users. It establishes SRM as a symptom of assignment or data-quality
  defects that can reverse shipping decisions.
- [Gupchup et al., “Trustworthy Experimentation Under Telemetry Loss”](https://www.microsoft.com/en-us/research/publication/trustworthy-experimentation-under-telemetry-loss/)
  is an ACM CIKM 2018 paper using applications with millions of users and billions of sessions. It
  explains how telemetry loss can bias effects and reduce power, supporting variant-level telemetry
  checks and reconciliation.
- [Dmitriev et al., “A Dirty Dozen: Twelve Common Metric Interpretation Pitfalls”](https://www.microsoft.com/en-us/research/publication/a-dirty-dozen-twelve-common-metric-interpretation-pitfalls-in-online-controlled-experiments/)
  is a KDD 2017 paper derived from thousands of Microsoft experiments. It supports cautious metric
  interpretation, checking segments and denominators, and avoiding a ship decision from one proxy.
- [Kohavi et al., “Controlled experiments on the web: survey and practical guide”](https://link.springer.com/article/10.1007/s10618-008-0114-1)
  is a 2009 Data Mining and Knowledge Discovery survey covering power, sample size, variance
  reduction, and practical trustworthy experiments. The older platform examples do not change the
  statistical need to predefine a powered decision.
- [Larsen et al., “Statistical Challenges in Online Controlled Experiments”](https://arxiv.org/abs/2212.11366)
  reviews methodology used across major online platforms and discusses optional stopping,
  interference, heterogeneity, and other active challenges. The preprint supports the skill's
  distinction between fixed-horizon and valid sequential analysis; it does not make one method
  universally preferable.

## Good/bad source map

- Specific ad-to-page promise versus a generic homepage maps to Google Ads message-match and landing-
  page-experience guidance plus Becker et al.'s post-click context-transfer study.
- One primary action with truthful labels versus competing or misleading CTAs maps to Material and
  GOV.UK button guidance, NN/g information-scent evidence, and FTC false-hierarchy examples.
- Persistent labels, recoverable errors, logical steps, and accepted-backend confirmation map to W3C
  forms, GOV.UK validation/question/confirmation patterns, web.dev form guidance, and Seckler et al.'s
  controlled form study.
- Authentic, scoped proof versus fake reviews, activity, scarcity, or independence maps to the FTC
  review rule and dark-pattern report; the assurance-seal studies support avoiding badge clutter.
- A contextual sticky action versus one covering fields or focus maps to WCAG Reflow and mobile form
  evidence.
- Field Core Web Vitals plus third-party budgets versus a one-run performance score maps to current
  Web Vitals thresholds, Chrome third-party guidance, and the limited Rakuten case study.
- Backend lifecycle and accepted/qualified purchase or lead outcome versus CTA or thank-you counts
  maps to GA4 ecommerce and lead events plus Google Ads offline lead feedback.
- Prespecified, powered, data-quality-checked tests versus peeking at a proxy maps to the Microsoft
  research program, Kohavi survey, and statistical-methodology review.

## Limits

- No source establishes one universal hero, section order, CTA color, copy length, form length,
  mobile breakpoint, or landing-page CVR. Those decisions depend on traffic intent, offer, audience,
  channel, device, risk, and downstream value.
- Observational benchmarks and vendor datasets reveal context and possible problems but do not prove
  that copying a correlated page feature causes lift.
- Legal, privacy, accessibility, advertising-platform, and consent requirements change by
  jurisdiction and effective date. Use the applicable compliance, accessibility, and provider
  sources at implementation time; this skill supplies a product workflow, not legal advice.
