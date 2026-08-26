# Page architecture, message requirements, proof, and conversion flows

Read this reference when planning how a campaign and offer become sections, message requirements,
proof, CTA behavior, a product purchase path, lead form, or confirmation state. It specifies what
the page must communicate and prove; content, design, and development owners decide the final
expression and implementation. No section sequence is universally highest-converting.

## Match the arrival promise

Create a message map for each materially different campaign or intent. Carry through the same
product, audience, outcome, offer, price or qualification, terminology, visual identity, and next
step. If a search ad promises a free roof estimate, the page must not lead with a general remodeling
brochure or reveal a fee only after submission.

Good: the page headline makes the advertised outcome recognizable and immediately explains the
specific next step.

Bad: the ad is specific, but every campaign lands on a generic homepage with multiple offers.

Failure prevented: visitors must re-evaluate whether they reached the right place, and the campaign
loses both relevance and trust.

## Treat the hero as a decision region, not a template

`Hero` is shorthand for the first prominent content region. It is not a required large image, a
headline formula, or proof that the page has communicated its offer. Review the region by the
decision it supports:

| Concept | Good | Bad |
|---|---|---|
| recognition | the product, task, audience, and advertised outcome are recognizable | a category slogan makes the visitor reinterpret the ad |
| value | the desired outcome and credible mechanism or differentiator are specific | adjectives such as `smarter`, `better`, or `next-generation` carry the claim |
| expectation | material eligibility, burden, timing, cost, and next step are visible when they change the decision | the action conceals a long form, sales call, fee, or disqualifier |
| proof | relevant, attributable evidence bears the weight of the nearby claim | an unsourced rating, logo wall, stock portrait, or decorative counter performs trust theater |
| action | one truthful next step has clear priority, with necessary alternatives subordinate | equal actions compete or a generic label hides the destination |
| media | imagery demonstrates the product, outcome, process, or fit without delaying the decision | decorative media consumes the viewport, implies unsupported proof, or becomes the slow unstable focal point |

A text-first first view can be right. A product demonstration or relevant image can be right. A form
can begin there when the task and burden are already understood, or later when visitors need proof or
qualification first. Treat each as a hypothesis derived from the arrival intent and decision, not a
component quota.

## Review what is good and bad above the fold

Treat "above the fold" as the first rendered viewport under a named device and state, not a fixed
pixel line. Review what the visitor can recognize before scrolling. Do not require every argument or
the complete form to fit there.

| Review area | Good evidence | Bad evidence |
|---|---|---|
| Arrival match | The product, audience, outcome, offer, and terminology continue the acquisition promise | A specific ad or query lands on a generic slogan, homepage, or different offer |
| Decision clarity | The visitor can tell whether the page is for them, what they can get, and what happens next | Brand theatre or feature language leaves the task and next step unclear |
| Proof | One relevant, attributable proof point supports the main promise at the strength claimed | Logo wallpaper, fake activity, context-free ratings, or an unsupported superlative |
| Primary action | One truthful action has clear visual priority and names its real next step | Several equal CTAs compete, or `Submit` and `Get Started` conceal the result |
| Material terms | Eligibility, price or commitment, availability, and important limitations appear early when they change the decision | A mandatory cost, disqualifier, or commitment is delayed until after activation |
| Experience | The main content is stable, readable, unobstructed, and representative field evidence does not show a material loading or interaction failure | A late hero, consent layer, third party, or layout shift delays or covers the decision block |

Classify each row as established, likely, plausible, or unknown and attach the source, observation,
or metric that supports it. A missing item is not automatically bad: a low-risk, high-intent page may
need little proof, while a complex or high-commitment decision may correctly place the full form after
more explanation.

The source basis is bounded. Google Ads documents message match, useful content, mobile friendliness,
and important information early. W3C and NN/g support informative, frontloaded structure. Material
and GOV.UK support descriptive action labels and clear action hierarchy. Web Vitals sources establish
field experience and first-viewport performance mechanics. None establishes a universal hero layout,
fold height, CTA position, or guaranteed conversion lift.

## Sequence the visitor's decision

Use the shortest complete answer path. Start with a first-view decision block, then add only the
questions the audience needs answered.

| Visitor question | Useful content | Weak substitute |
|---|---|---|
| Is this for me? | audience, use case, eligibility, geography | a category slogan |
| What outcome do I get? | concrete benefit, deliverable, time or scope | unsupported superlative |
| Why believe it? | relevant result, demonstration, credential, methodology | logo wallpaper or fake counters |
| What will it take? | steps, timing, price or commitment, information required | “It's easy” |
| What could go wrong? | limits, guarantee terms, privacy, human contact, cancellation | hidden fine print |
| What happens next? | specific CTA and post-submit expectation | `Submit` |

High-intent visitors may need an action immediately plus concise proof and qualification. Lower-
awareness or higher-risk decisions may need explanation, evidence, process, and objection handling
before the form. A long page is not automatically bad; an unstructured or repetitive page is.

Keep each section answerable from its heading. Frontload the information-bearing words. Use short
paragraphs, bullets, comparison or process structure only when it helps the visitor decide. Do not
write every section as a slogan followed by generic marketing copy.

## Choose a layout around the conversion mode

Layout is the relationship among information, proof, and action—not the name of a template. Review
five concepts before prescribing regions:

- **Hierarchy:** the visually strongest elements match the most important visitor decision.
- **Grouping:** headings, spacing, boundaries, and proximity make each claim, proof item, and action
  relationship clear.
- **Sequence:** visual, reading, and focus order preserve a coherent path when columns stack or media
  disappears.
- **Density:** the page contains enough decision information without repetition, slogan stacks, or
  decorative sections.
- **Continuity:** repeated actions keep the same meaning and destination across viewport, section,
  pending, validation, and success states.

Good layout reduces the work of finding and relating decision information. It does not prove
persuasion by being minimal, centered, two-column, card-based, long, or short.

Use these as starting hypotheses, not universal templates:

| Conversion mode | First decision region | Supporting sequence |
|---|---|---|
| direct product purchase | exact product/variant, visual, price, availability, key differentiator, purchase action | proof, benefits/specifications, delivery and returns, objections, repeated purchase action |
| simple high-intent lead | exact service/outcome, eligibility cue, concise proof, short form or call | process, qualifications, evidence, common concerns, repeated action |
| complex quote/application | outcome, who qualifies, burden/timing, start action | requirements, process, cost drivers, evidence, staged questions, review and confirmation |
| B2B demo/consultation | audience problem, business outcome, credible mechanism, booking/request action | use cases, product evidence, integration or process, customer results, fit and next steps |
| call-first local service | service, location/availability, urgency boundary, call action and hours | credentials, service area, process, pricing expectations, alternative form, repeated call action |

The conversion control may be beside the first decision content, embedded after enough proof, or
both. A two-column desktop hero can stack to message then action on mobile. A long page should repeat
the same primary action at real decision points; a short page should not add empty sections to look
complete.

## Plan a specific value proposition

Use this structure as a diagnostic, not a fill-in-the-blank headline:

```text
For [audience with need], get [specific outcome] through [credible mechanism or differentiator],
with [important limitation or risk reducer].
```

Keep claims at the strength the evidence supports. Quantified claims need scope, date, population,
and a source. `Save an average of 18%` is incomplete when the average, product, time window, and
conditions are unknown.

Good:

```text
Compare same-day quotes from licensed local installers.
Answer five questions; no purchase is required.
```

Bad:

```text
The future of home improvement is here.
[Get Started]
```

The good version identifies the task and expectation. It does not guarantee that this wording will
win; test it with the intended traffic.

## Specify CTA hierarchy and continuity

Treat a CTA as an action contract: its label, visual priority, destination, required commitment,
pending behavior, accepted outcome, and next state must agree. Choose one primary action for the
page. Repeating that action after meaningful decision content is not the same as adding competing
goals. A secondary action should serve visitors who cannot or should not take the primary action yet,
such as viewing eligibility or contacting accessibility support.

Use a label that describes the immediate, truthful next step:

```text
Good: Check my eligibility
Good: Book a 20-minute walkthrough
Bad:  Submit
Bad:  Get approved now     # when the form only sends an inquiry
Bad:  Book a demo          # when the action only submits a request for later contact
```

Preserve the label's meaning through pending and success states. Do not change `Check eligibility`
into an unexplained `Processing` or send it to a sales call booking page without warning.

Use visual prominence, surrounding copy, control shape, position, and contrast together. Do not rely
on a fashionable color, animation, or `above the fold` placement as a conversion law. Keep the
action in the visitor's task flow and verify it with the actual content and viewport.

Plan a CTA section at a real decision point: after the nearby content has answered a meaningful
question and before the visitor must search for the next step. Its job is to restate the relevant
outcome, resolve the remaining commitment or risk, and offer the same truthful primary action. Do not
repeat a generic banner every fixed number of pixels, introduce a new promise late in the page, or
use a different label for the same destination.

Judge navigation and secondary actions by function. Keep necessary trust, contact, legal,
accessibility, and recovery paths. Demote or remove unrelated exits only when the campaign decision
does not need them; `no navigation converts better` is not a universal rule.

## Use proof that bears the promised weight

Choose proof by claim:

- outcome claims: scoped case results, distribution or methodology;
- quality claims: independent certification, process evidence, warranty terms;
- adoption claims: current and verifiable counts or named customers with permission;
- experience claims: genuine attributable reviews or testimonials, including material connections;
- fit claims: representative examples, eligibility criteria, before/after context.

Put the strongest relevant proof near the claim or decision it supports. Logos without context,
stock portraits presented as customers, stale awards, fake activity messages, or cherry-picked
testimonials are not risk reducers.

Do not imply that a platform badge, consent certificate, security icon, or trade membership approves
the whole offer. Verify mark usage and link to meaningful detail when the visitor may need it.

## Plan the field ledger

Classify every field before specifying the form:

| Field purpose | Keep now when | Better alternative when not needed now |
|---|---|---|
| fulfill | required to produce the promised result | collect after the initial result |
| qualify | changes eligibility, routing, or serviceability | infer only when reliable and permitted |
| contact | supports the disclosed next step | let the visitor choose a contact path |
| compliance | required for a specific lawful choice or evidence | do not add generic legal theater |
| enrichment | materially improves this interaction | enrich later under approved data rules |
| analytics | no PII is needed in ordinary event data | use a non-PII campaign or variant key |

Do not treat “sales wants it” as a field purpose. Name the decision and owner. Show why sensitive or
surprising information is needed before asking. Put the explanation beside the field or decision,
not only in a distant privacy policy. Contextual reassurance answers a concrete concern; a generic
lock icon or `100% secure` claim does not establish how the information will be used.

## Preserve the advertised product and offer

For a product-selling page, make the advertised product or variant the primary focus. Keep title,
image, price, currency, availability, promotion, and selected variant consistent with the ad,
listing, or campaign. Show the actual recurring or total commitment, required quantity, delivery or
fulfillment expectation, material fees, return or cancellation terms, and stock or preorder state
before purchase when they affect the decision.

Good: a shopping ad for a blue 64 GB device opens the same selected variant with the advertised
price, availability, and a truthful `Add to cart` or `Buy now` action.

Bad: the click opens a generic category, selects a more expensive variant, hides mandatory fees, or
uses `Buy now` for a button that only starts an inquiry.

Do not let a content-management, feed, promotion, or personalization update make the ad and landing
page disagree. Version and monitor offer inputs. Route actual checkout/payment, subscription,
refund, and order-state behavior through the owning commerce system. Route implementation to the
commerce and development owners.

When an offer promises quotes, matches, introductions, or responses from multiple providers, record
how many recipients may receive the request, who selects them, which party provides the advertised
outcome, when contact or data transfer occurs, and what the visitor is told before acting. This is a
material part of the offer and next-step contract, not fine print to infer from a generic CTA. Route
the applicable consent and lead-transfer conclusion to `lead-compliance-gates` and the current legal
owner.

## Choose single-step or multi-step honestly

Prefer a single step when the form is short, familiar, and can be understood at once. Consider
multiple steps when questions are numerous, conditional, or form meaningful groups.

A multi-step flow must:

- state the overall task before starting;
- group questions by a visitor-understandable purpose;
- show progress only when it is accurate and helpful;
- allow Back without losing answers or duplicating effects;
- distinguish optional stages and allow a real skip;
- preserve context through refresh, validation, and slow responses when practical;
- provide a review step for consequential or hard-to-correct answers; and
- disclose the real burden rather than using steps to conceal it.

Good: split property, project, and contact details into logical steps after explaining that the quote
requires all three.

Bad: turn three simple fields into three screens to manufacture micro-commitments, then reveal seven
unexpected questions.

The failure is surprise and loss of trust, not merely the number of screens.

## Make every field recoverable

- Use a persistent visible label and programmatic association. A placeholder can show an example but
  cannot carry the only label.
- Put format guidance before entry when it is unusual. Accept harmless punctuation, case, and
  spacing variations.
- Use native elements, truthful `type`, stable `name` and `id`, and precise `autocomplete` values.
  Use `inputmode` only as a keyboard hint, not validation.
- Mark optional input clearly in the language the design system uses. Do not leave users guessing
  from inconsistent asterisks.
- Validate on submit by default. Use earlier feedback only when it helps complete a field and does
  not announce an error while the person is still typing.
- Preserve every safe answer after failure. Put a specific corrective message beside the field and
  link a summary to errors in long forms.
- Keep the action available. A silently disabled button makes the visitor hunt for an unknown rule.

## Separate request, consent, and evidence

The requested service, privacy notice, marketing choices, and permission for later contact are
different decisions. Present each required choice visibly and accurately. Do not use a prechecked
box, acceptance hidden only in a button label, a stale partner list, or a consent record that cannot
reconstruct the rendered page and affirmative action.

Use `lead-compliance-gates` for regulated U.S. lead generation. Higher CVR never justifies a hidden
disclosure or a broader contact permission than the visitor chose.

## Complete the handoff

On submit:

1. keep the initiating action and current state understandable;
2. prevent duplicate records at the owning backend, not only with a disabled button;
3. distinguish accepted, duplicate, validation-rejected, policy-rejected, and failed outcomes;
4. retain safe input and provide recovery for a failure; and
5. confirm the exact stored outcome, expected response time and channel, reference when useful, and
   correction or contact path.

Do not fire the canonical conversion merely because the visitor clicked or loaded a thank-you URL.
The accepted backend outcome owns conversion truth.
