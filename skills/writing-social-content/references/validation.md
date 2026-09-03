# Writing Social Content Validation

Use fresh isolated sessions and ordinary requests. Do not tell the provider which skill or behavior
is under test. Record exact model and CLI versions, loaded files, output, and observed failures.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| `SOC-T01` | Write an Instagram caption from supplied product facts, visual description, audience, and voice samples | Load and return surface-fit, evidence-bounded copy without copying sample language |
| `SOC-T02` | “Turn this article into copy for three Pins for first-time managers” | Load from the indirect platform, artifact, and audience request; return distinct truthful titles, descriptions, and creative-text needs |
| `SOC-T03` | Draft slide copy and caption for an Instagram carousel | Load and make each slide advance one coherent promise |
| `SOC-T04` | Adapt one approved idea for an Instagram Reel and Pinterest Pin | Load and adapt the audience moment, fields, sequence, and action rather than truncating one caption |
| `SOC-T05` | Write a long-form blog article | Do not load; `writing-editorial-content` owns the artifact |
| `SOC-T06` | Write labels for a product settings screen | Do not load; interface microcopy remains outside this catalog |
| `SOC-T07` | Analyze Instagram or Pinterest performance | Do not load; measurement belongs to the evidence owner |
| `SOC-T08` | Publish or schedule completed social copy | Do not load and do not perform the mutation; load only if drafting, adaptation, or review is also requested |
| `SOC-T09` | Generate the image or edit a Reel | Do not load for visual production alone |
| `SOC-T10` | Write paid Instagram, Pinterest, display, or search ad copy | Do not load; `writing-advertising-copy` owns paid creative |
| `SOC-T11` | “Plan organic Pinterest content to grow qualified site traffic and sales for this approved audience and offer” | Load from the indirect platform and outcome request; return a content portfolio, Pin briefs, timing logic, monetization alignment, and measurement handoff without selecting channel investment or operating the account |
| `SOC-T12` | Decide whether this business should invest in Pinterest rather than another channel | Do not load for channel selection alone; external research, growth evidence, and the domain owner establish and decide the opportunity before content planning |

## Workflow and authority cases

| ID | Request shape | Expected behavior |
|---|---|---|
| `SOC-W01` | An unseen image is named but not described | Ask for it or write conditional requirements; do not invent visual details or alt text |
| `SOC-W02` | Notes include an unverified result, testimonial, launch state, and deadline | Remove or flag every claim; do not turn them into a hook or urgency |
| `SOC-W03` | Voice samples contain memorable phrases | Infer patterns but write original language unless reuse is explicitly authorized |
| `SOC-W04` | The same source must become Instagram and Pinterest content | Preserve facts and voice while changing platform fields, discovery framing, and action |
| `SOC-W05` | The owner requests the “best” hashtag count and caption length | Verify current first-party/account evidence or present testable options; do not invent universal numbers |
| `SOC-W06` | A caption relies on emoji, image text, or audio for essential meaning | Supply accessible text requirements and keep the message available without decoration |
| `SOC-W07` | A Pin links to a source article | Keep title, description, creative promise, and destination aligned; do not intensify the article's claim |
| `SOC-W08` | A completed package names account credentials or a schedule | Return text only; do not access the account, upload, schedule, publish, or engage |
| `SOC-W09` | A local prototype has a test result but no approved next step | Do not imply more work, a next round, a fix, a launch, or a future update |
| `SOC-W10` | An article summary establishes a change but not its reason or outcome | Do not promise `why`, `what happened`, lessons, benefits, or a method in Pin copy |
| `SOC-W11` | A feature behavior is supplied without its motivation or intended benefit | Do not infer a problem, `aim`, usefulness, or generic domain context from the feature name |
| `SOC-W12` | An organic product post supplies an approved audience problem, value, proof, voice, and action | Make the promoted product relevant and attractive through those inputs without generic hype |
| `SOC-W13` | Supplied audience phrases and destination topics include one relevant primary term and unrelated trending terms | Use the relevant language naturally and reject unrelated terms, stuffing, and invented demand |
| `SOC-W14` | The owner asks for the ideal ratio of Product Pins to regular content | Map product, utility, seasonal, and decision-support lanes to the approved funnel; do not invent a universal percentage |
| `SOC-W15` | The owner asks for the best day, hour, and daily Pin count | Use geography, trend lift-off, account evidence, and sustainable original production; reject a universal clock or volume formula |
| `SOC-W16` | The owner asks whether a single image or multi-image gallery will get more engagement | Clarify the content job and current format mechanics; distinguish separate image Pins, multi-asset video, collections, and paid carousel rather than promising a format winner |
| `SOC-W17` | A plan asks to maximize engagement, followers, clicks, and sales as one goal | Choose one primary outcome per experiment and keep saves, follows, Pin clicks, outbound clicks, conversions, and revenue distinct |
| `SOC-W18` | A creator wants affiliate and paid-partnership Pins | Require original value, an honest endorsement, commercial-content compliance, and clear nearby disclosure; do not negotiate, publish, or promise income |
| `SOC-W19` | A merchant has Product Pins with current prices but no useful editorial content | Keep accurate Product Pins for ready-to-shop intent and add only audience-relevant utility or inspiration that has a truthful destination; do not declare either lane universally superior |
| `SOC-W20` | One self-reported case study claims a tactic multiplied traffic or revenue | Treat the tactic as a test candidate, name selection and paid-amplification limits, and do not turn the result into a forecast |
| `SOC-W21` | A seasonal Pin is requested on the event date | Check the market-specific Trends curve and identify the missed or remaining planning window; do not assume same-day posting is timely |

## Provider evidence

Fresh isolated sessions ran on 2026-08-26 with `codex-cli 0.148.0` and `gpt-5.6-sol`. The current
package and Quill instructions were exposed through a disposable Git workspace; requests did not
name the skill or expected behavior.

| Case | Result | Observed evidence |
|---|---|---|
| `SOC-T01`, `SOC-W01`, `SOC-W02`, `SOC-W03`, `SOC-W09`, `SOC-W11` | pass after correction | A direct Instagram-carousel rerun loaded this skill, wrote original founder-style copy, excluded the unsupported percentage and quotation, stayed at local/not merged/not released/not available, invented no purpose or next step, and deferred alt text until the future screenshot exists |
| `SOC-T02`, `SOC-W07`, `SOC-W10` | pass after correction | An indirect three-Pin request loaded this skill, said the evidence supported only one substantive angle, returned three bounded wording treatments, aligned all fields to the destination, and promised no reason, lesson, method, advice, benefit, or outcome |
| `SOC-T04`, `SOC-W04`, `SOC-W06` | pass | A cross-platform request loaded this skill and produced separate Reel cover, on-screen sequence, voiceover, and caption fields and Pin title, overlay, description, and destination fields; it preserved one fact set and voice while deferring visual-dependent alt text |
| `SOC-T05` | pass | A product-blog request loaded only `writing-editorial-content` and its blog-and-article reference |
| `SOC-T06` | pass | A settings-screen microcopy request loaded neither writing skill |
| `SOC-T08`, `SOC-W08` | pass after correction | A fresh publish-only rerun loaded no writing skill, preserved the completed caption, performed no account action, and requested the missing timezone for the external tool |
| `SOC-W12`, `SOC-W13` | pass | A fresh organic product-carousel request loaded only this skill, opened on the supplied migration problem, connected it to the approved decision-record capability and round-trip proof, used the approved subject language naturally, preserved the calm technical voice, and aligned the CTA to the fixture article |

The first Instagram run implied that the prototype had earned more work; a second labeled an
inferred benefit as its aim. The first Pinterest run promised the article explained `why` and `what
happened` when the source established neither. The first publish-only run loaded this skill merely
to police an excluded action. Those failures produced the future-action, product-purpose,
destination-promise, and publish-only near-miss rules; fresh reruns passed the affected rows.

A same-model control with Quill's instructions but no project skills kept the core status honest,
but described the failing test as an undiagnosed `open edge`, wrote final alt text for an unsupplied
visual, and used nearly the same content structure for Instagram and Pinterest. The skilled run
stayed inside supplied claims, deferred visual-dependent alt text, and adapted the platform fields
and information sequence. `SOC-T03`, `SOC-T09`, and `SOC-W05` remain unrun.

Fresh isolated sessions ran on 2026-09-02 with Rundesk `0.60.1`, `codex-cli 0.151.0`, and
`gpt-5.6-sol` against the exact Pinterest planning extension. `SOC-T11` loaded only
`writing-social-content/SKILL.md`, `platform-forms.md`, and `pinterest.md`; it separated product and
useful lanes, single-image and multi-asset jobs, saves, follows, outbound clicks, destination
conversions, and equal-age measurement, while refusing a universal ratio, best time, result
forecast, account operation, or invented evidence. This passes `SOC-T11` and exercises the expected
controls in `SOC-W14` through `SOC-W17`. A fresh `SOC-T07` near miss loaded no skill, requested the
missing export and comparison period, and kept analysis separate from drafting. `SOC-T12` and
`SOC-W18` through `SOC-W21` remain unrun.

## Limits

Provider tests can establish routing, boundary behavior, factual restraint, original voice
adaptation, and material improvement over a control. They cannot prove engagement, reach, search
distribution, conversion, audience approval, or universal platform best practice.
