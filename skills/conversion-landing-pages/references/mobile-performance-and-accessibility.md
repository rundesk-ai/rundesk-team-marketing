# Mobile, performance, and accessibility

Read this reference when implementing or reviewing responsive layout, mobile forms, fixed or sticky
actions, media, third-party scripts, Core Web Vitals, or accessibility for a conversion landing page.

## Preserve the same decision on narrow screens

Start with the content and action in a narrow viewport, then add layout when space permits. Preserve
the offer, proof, limitations, disclosure, primary action, error recovery, and confirmation across
breakpoints. Moving a proof block or form is valid; hiding it because the desktop composition does
not fit is not.

Use content pressure to choose breakpoints. Test long headlines, translated labels, validation
messages, browser zoom, landscape, split-screen, and short-height viewports. Do not target a list of
phone models and assume the gaps between them work.

At 320 CSS pixels, ordinary content must reflow without loss of information or two-dimensional
scrolling. Preserve zoom and at least 200% text resize. Keep DOM, reading, and focus order aligned
with the meaningful visual order.

## Keep the action available without covering the task

A sticky mobile CTA is conditional, not a default conversion trick. Use it only when the action
remains meaningful throughout the page and the control does not cover content, form labels, errors,
consent, focus, browser UI, or the on-screen keyboard.

Good: the sticky action respects safe areas, leaves content scroll padding, disappears or changes
context when the form action is already visible, and remains operable with zoom.

Bad: a fixed footer covers the current field and consent text, then reports higher CTA clicks from
accidental activation.

Test fixed edges in portrait, landscape, browser chrome expanded and collapsed, keyboard open, and
after rotation. Prefer normal document flow unless persistence solves a demonstrated problem.

## Make mobile entry low-effort and truthful

- Put persistent labels above fields when horizontal space is tight.
- Use `type="email"`, `type="tel"`, precise `autocomplete`, `inputmode`, and `enterkeyhint` where
  their semantics match. Do not use `type="number"` for phone, postal, account, or other identifiers.
- Make the focused field, its label, hint or error, and next action remain visible when the keyboard
  reduces the visual viewport.
- Do not trigger a surprise keyboard with autofocus, disable paste, or force keyboard switching for
  values the browser can autofill.
- Use generous targets and spacing. WCAG 2.2 AA defines a 24-by-24 CSS-pixel minimum target-size
  criterion with exceptions; prefer larger practical touch areas where the layout permits.
- Support touch, keyboard, pointer, voice, and screen-reader completion on the same responsive flow.

## Set and measure a field performance contract

Use current Core Web Vitals as experience guardrails at the 75th percentile of real page views:

| Metric | `good` threshold | Conversion-page failure to watch |
|---|---:|---|
| Largest Contentful Paint | <= 2.5 s | hero media, fonts, consent or tag bootstrapping delays the offer |
| Interaction to Next Paint | <= 200 ms | main-thread scripts delay CTA, field, step, or submit feedback |
| Cumulative Layout Shift | <= 0.1 | late media, proof, banners, validation, or widgets move the action |

Measure mobile and desktop field data separately when volume permits. Use lab profiles to reproduce
and diagnose, not to replace real-user measurement. Report the actual population and percentile;
do not call one Lighthouse run a conversion-performance result.

The thresholds do not promise a particular CVR lift. A one-month 50/50 Rakuten 24 landing-page test
reported both faster/stabler rendering and higher conversion, but it is one retailer's case study,
not a transferable effect size. Use performance as a quality contract and test business impact in
your own traffic.

## Budget the page around the conversion path

Load the message, proof needed for the first decision, and primary action before nonessential media
and widgets. Size media, reserve layout space, serve responsive formats, subset or self-host fonts
when appropriate, and avoid video autoplay that competes with reading or data budgets.

Inventory every third party: analytics, tag manager, consent platform, A/B testing, chat, call
tracking, CAPTCHA, reviews, personalization, and advertising. For each, record owner, purpose,
consent state, load strategy, main-thread/network cost, failure behavior, PII boundary, and removal
criterion.

Make the actual LCP resource discoverable in initial HTML. If the first-view visual is the LCP
image, do not lazy-load or hide it behind JavaScript discovery; use a real responsive image and
prioritize or preload only when measurement shows discovery needs help. Give images explicit
dimensions, reserve space for banners and embeds, lazy-load only offscreen media, and make critical
font loading an intentional tradeoff. Break up long main-thread work that delays fields and CTA
feedback.

Good: initialize required consent state early, defer noncritical tags, preserve attribution through
approved first-party data, and let the owning system accept a purchase or lead even when analytics
or chat fails.

Bad: synchronously load multiple tags before rendering, inject an experiment after the first paint,
or block submission until a conversion pixel responds.

Cookie and consent interfaces are part of this budget. Render them without shifting the offer or
action, and test the work triggered by acceptance; a late banner or heavy consent callback can harm
CLS or INP even when the page shell is fast.

Third-party scripts can both slow the task and lose telemetry. Monitor them in field data and test
blocked, slow, and failed dependencies. Do not remove a required consent control to gain speed.

## Apply accessibility to the complete flow

Use WCAG 2.2 AA as the baseline unless a stricter project or jurisdictional standard applies:

- semantic regions and a logical heading outline;
- native form controls and explicit labels;
- meaningful accessible names that include the visible label;
- keyboard operation with visible and unobscured focus;
- text and non-text contrast, without color-only meaning;
- 320 CSS-pixel reflow, zoom, text resize, orientation support, and no clipped disclosures;
- accessible instructions, error identification, error suggestions where known, and status
  announcements;
- alternatives for meaningful images and captions/transcripts for meaningful media;
- no required dragging, hover-only content, motion-only action, or unexpected context change; and
- reduced-motion behavior and no flashing hazards.

Do not claim WCAG conformance from an automated scan. Automated tools catch only some defect types;
complete the page with keyboard and representative assistive technology and record what was tested.

## Verify a representative matrix

Test at least:

1. first view and full flow at 320 CSS pixels, a common mobile viewport, desktop, and 400% zoom;
2. portrait, landscape, short height, safe areas, browser UI states, and keyboard open/closed;
3. touch, keyboard, fine pointer, autofill, paste, voice control, and screen reader;
4. empty, valid, invalid, partial, slow, offline/failure, duplicate activation, and accepted states;
5. long copy, long names, translated content, missing optional media, and blocked third parties;
6. real-user LCP, INP, and CLS plus lab throttling and third-party cost; and
7. CTA visibility, focus, disclosure readability, event accuracy, and backend acceptance in every
   form branch.

Record devices, browsers, network profiles, assistive technology, viewports, dates, and known gaps.
“Responsive in DevTools” and “Lighthouse 100” are not complete proof.
