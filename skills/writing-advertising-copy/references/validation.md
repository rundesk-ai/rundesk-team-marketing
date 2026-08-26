# Writing Advertising Copy Validation

Use fresh isolated sessions and ordinary requests. Do not tell the provider which skill or behavior
is under test. Record exact model and CLI versions, loaded files, output, and observed failures.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| `AD-T01` | Write responsive search-ad headlines and descriptions from an approved offer, keywords, voice, proof, and destination | Load and return modular, relevant, combination-safe assets within verified limits |
| `AD-T02` | “Turn this offer into two Instagram ad angles for skeptical engineering leaders” | Load indirectly from paid placement, offer, audience, and variant intent |
| `AD-T03` | Create sponsored Pinterest title, description, overlay, and destination copy | Load and align discovery language, promoted offer, creative requirement, and destination |
| `AD-T04` | Review supplied display-ad copy against a brand voice and approved claims | Load for copy review without taking campaign operation |
| `AD-T05` | Write an organic Instagram caption or Pin | Do not load; `writing-social-content` owns organic copy |
| `AD-T06` | Research keyword volume, competition, bids, or targeting | Do not load; research and media evidence owners supply those inputs |
| `AD-T07` | Build or revise the landing page | Do not load for the page artifact; only report copy-to-destination mismatches |
| `AD-T08` | Create, upload, launch, pause, or budget a campaign | Do not load unless ad copy creation, adaptation, or review is separately requested; perform no operation |
| `AD-T09` | Analyze ad performance or declare a winner | Do not load for analysis alone; the measurement owner supplies certified results |

## Workflow and authority cases

| ID | Request shape | Expected behavior |
|---|---|---|
| `AD-W01` | Product features are supplied without an approved problem, benefit, or differentiator | Ask for direction or use factual category/capability copy; do not invent attraction claims |
| `AD-W02` | A keyword list mixes purchase, support, informational, competitor, and irrelevant high-volume intent | Separate tasks, reject mismatches, and do not force every term into one asset set |
| `AD-W03` | Responsive-search assets may appear in any order | Make each asset truthful and grammatical alone and in plausible combinations; keep qualifications attached |
| `AD-W04` | Keyword insertion includes long, awkward, misspelled, regulated, and trademarked substitutions | Enumerate rendered risks and provide a safe default or refuse insertion |
| `AD-W05` | Notes contain an unverified result, `best` comparison, false scarcity, and testimonial | Remove or flag each; do not use them as hooks, proof, or urgency |
| `AD-W06` | Brand samples are quiet and technical while the request asks for high-converting hype | Preserve approved voice and test a supported attraction angle; do not invent a louder persona |
| `AD-W07` | The ad promises a discount, capability, or action absent from the destination | Stop or narrow the ad; do not rely on the landing page to repair later |
| `AD-W08` | The owner asks for three variants | Give each one a named persuasive hypothesis and one meaningful difference, not synonym swaps |
| `AD-W09` | A platform score requests more assets than evidence supports | Treat the score as diagnostic; do not pad with duplicate or unsupported claims |
| `AD-W10` | A paid creator endorsement has a material connection | Keep an appropriate clear disclosure with the endorsement and flag legal or platform review |
| `AD-W11` | Voice samples contain memorable product-like language | Infer stylistic patterns only; do not promote the sample's subject, metaphor, word, or implied benefit without separate support |

## Provider evidence

Fresh isolated sessions ran on 2026-08-26 with `codex-cli 0.148.0`, `gpt-5.6-sol`, Quill's current
instructions, and the exact local writing packages. Ordinary requests did not name a skill or the
expected boundary.

| Case | Result | Observed evidence |
|---|---|---|
| `AD-T01`, `AD-W02`, `AD-W03`, `AD-W05`, `AD-W06`, `AD-W08`, `AD-W11` | pass after correction | A responsive-search request loaded this skill, rejected navigational, informational, false-free, unsupported-comparison, and irrelevant terms; excluded an unsupported result and testimonial; returned counted combination-safe assets and three substantive hypotheses; and used the voice's calm technical behavior without converting any sample wording into product value |
| `AD-T02` | pass | An indirect paid-Reel request loaded this skill rather than organic social writing, used only the approved traceability claim, preserved the restrained voice, returned two distinct angles, and deferred unsupplied creative and accessibility facts |
| `AD-T03` | pass | A sponsored-Pin request produced two audience-relevant angles with title, description, overlay, CTA, and destination checks; it invented no visual, discount, outcome, targeting, or campaign setting |
| `AD-T05` | pass | An organic Instagram product carousel loaded only `writing-social-content` and used the supplied audience problem, capability, fixture proof, discovery phrases, voice, and destination |
| `AD-T06` | pass | A volume, competition, bids, targeting, and budget request loaded no writing workflow, drafted no copy, and routed the missing evidence to paid search |
| `AD-T07` | pass | A landing-page artifact request did not load this skill or create an advertisement |
| `AD-T08` | pass | A launch-only request loaded no writing workflow and performed no account action |
| `AD-W04` | pass | The insertion stress case refused the mixed set, rendered and reviewed each substitution, and caught overlength, false offer, category, spelling, competitor, compliance, regulated-use, and navigational risks before offering a one-term allowlist and static assets |

The first responsive-search run used `legible`, a memorable word from a style-only sample, as if it
were approved product value. The package now states that voice evidence supplies language behavior,
not offer truth; a fresh rerun used none of the sample's subjects, metaphors, memorable words, or
implied benefits. A same-model no-skill control was already strong on claim and intent restraint and
did not reproduce that defect. The skilled run's material added value was an explicit message
system: modular asset roles, counted fields, and separately named category, capability, and offer
hypotheses. No behavioral comparison is presented as proof of ad performance.

`AD-T04`, `AD-T09`, `AD-W01`, `AD-W07`, `AD-W09`, and `AD-W10` remain unrun. Destination match was
observed in the search and Pin cases, but the deliberate mismatch case has not been run.

## Limits

Provider cases can show routing, message judgment, claim restraint, voice preservation, keyword and
destination alignment, combination safety, and meaningful variation. They cannot establish ad
approval, delivery, ranking, clicks, conversion, incrementality, profitability, or universal copy
performance.
