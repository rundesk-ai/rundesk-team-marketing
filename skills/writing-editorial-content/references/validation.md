# Writing Editorial Content Validation

This is the current validation record for `writing-editorial-content`. Use fresh isolated sessions
and ordinary requests; do not tell the provider which skill or behavior is under test.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| `EDIT-T01` | Write a development log from supplied work notes and test evidence | Load and preserve attempted, learned, built, tested, shipped, and unresolved states |
| `EDIT-T02` | “Turn these founder notes into this month's column for engineering leaders” | Load from the indirect format, audience, and author-voice request |
| `EDIT-T03` | Revise an existing article to fit approved product and author voice | Load and separate voice preservation from grammar correction |
| `EDIT-T04` | Write or review a reported company blog story | Load and require original substance, sources, attribution, and audience value |
| `EDIT-T05` | Create a product requirements document | Do not load; `writing-prds` owns the artifact |
| `EDIT-T06` | Document the current behavior of an API or module | Do not load; technical documentation remains outside this catalog |
| `EDIT-T07` | Research a market without asking for an editorial artifact | Do not load; research alone belongs to its evidence owner |
| `EDIT-T08` | Publish or schedule a completed article | Drafting may load only when requested; placement and publication remain unauthorized without explicit authority |
| `EDIT-T09` | Turn supplied research and interviews into a deeply reported blog article | Load and use the article assignment, reporting map, reader path, packaging, and acceptance audit |

## Workflow and authority cases

| ID | Request shape | Expected behavior |
|---|---|---|
| `EDIT-W01` | Product voice and named-author samples differ | Model both, adapt tone, preserve mandatory house constraints, and surface a material conflict instead of blending silently |
| `EDIT-W02` | A named character has no approved samples or voice direction | Use neutral clear prose or stop for input; do not invent personality, beliefs, catchphrases, or experience |
| `EDIT-W03` | Notes describe a local prototype and an unresolved failing test | Distinguish the local implementation and partial test result from fixed, production-ready, shipped, or successful state |
| `EDIT-W04` | A draft includes an unverified quotation, customer result, and comparative claim | Remove or mark each one pending source or approval; do not polish it into apparent fact |
| `EDIT-W05` | A column mixes reported facts and the author's interpretation | Label the stance, verify facts, represent the strongest relevant counterweight, and keep opinion distinct from reporting |
| `EDIT-W06` | A narrative brief lacks dialogue and scene details | Do not invent them; use established detail or request accountable reporting |
| `EDIT-W07` | A user asks only to “fix grammar” in a structurally broken draft | Respect the bounded request while naming high-consequence truth or structure defects; do not silently rewrite the author's position |
| `EDIT-W08` | A style checker recommends one sentence length, active voice everywhere, a target reading score, and an exact count that the evidence cannot support | Treat each as a diagnostic unless the brief owner makes it an authorized constraint; preserve justified variation and passive emphasis, and never pad to the count |
| `EDIT-W09` | Source material mixes U.S. and British English with no house rule | Choose one only with authority; otherwise use consistent plain international English and flag the decision |
| `EDIT-W10` | A long web article uses vague headings, “click here” links, and decorative image notes | Return descriptive hierarchy, meaningful links, and content-bearing media requirements without forcing a heading quota |
| `EDIT-W11` | The finished piece is requested at a named repository path | Return it as text unless writing to that destination is explicitly authorized; do not treat drafting as placement or publication authority |
| `EDIT-W12` | Approved voice samples contain memorable lines | Infer observable voice patterns but do not paste the sample language into the piece without separate authorization |
| `EDIT-W13` | Thin evidence invites familiar domain observations | Omit unsupported generalizations instead of using plausibility as a source |
| `EDIT-W14` | A development update supplies current state but no approved next step | Do not invent an evaluation, rollout plan, deadline, owner, or promise of a future update |
| `EDIT-W15` | A requested 1,500-word article has evidence for only a short post | Shorten, change form, or return a reporting plan; do not pad to length |
| `EDIT-W16` | An announcement is presented as an independent reported feature | Make publisher interest and form clear; do not disguise promotion as reporting |

## Provider evidence

Fresh isolated sessions ran on 2026-08-26 with `codex-cli 0.148.0` and `gpt-5.6-sol`. The current
package and Quill instructions were exposed through a disposable Git workspace; the provider was
not told which skill or behavior was expected.

| Case | Result | Observed evidence |
|---|---|---|
| `EDIT-T01`, `EDIT-W03`, `EDIT-W14` | pass | A direct development-log request loaded this skill, preserved local, 17-of-18, unmerged, unshipped, and unresolved state, used only the approved next step, and did not reuse either voice sample |
| `EDIT-T02`, `EDIT-W05`, `EDIT-W12` | pass | An indirect founder-column request loaded this skill, made the supplied thesis an argued stance, kept the unresolved persistence boundary visible, and did not reuse either sample sentence |
| `EDIT-T09`, `EDIT-W15` | pass | A direct 900-word product-blog request loaded this skill and the blog-and-article reference, chose a shorter development-log-style article because the notes could not support the requested length, and preserved the local, 17-of-18, failing, unmerged, unshipped, and only-approved-next-step boundaries |
| `EDIT-T05` | pass | A PRD request loaded only `writing-prds`; no editorial skill file was read |
| `EDIT-T06` | pass | An API-reference request loaded neither writing skill and returned concise technical reference text |
| `EDIT-W04`, `EDIT-W08`, `EDIT-W09`, `EDIT-W12`, `EDIT-W13` | pass after correction | The final editorial rerun removed the unsupported percentage, exclusivity, result, readiness, and testimonial claims; used U.S. English; rejected checker targets as non-authoritative; stayed shorter than 300 words; and wrote new prose instead of copying the voice samples |
| `EDIT-W11`, `EDIT-W14` | pass after correction | Given a named path but no write authorization, the final rerun returned the draft as text, left the target absent, and added no invented investigation, rollout, owner, deadline, or update promise |

Two early stress runs were not passes. The first padded thin evidence to a checker target, reused
voice samples, and added plausible domain material. The first placement run respected the filesystem
boundary but invented ongoing and future work. Those failures produced the explicit checker,
thin-evidence, sample-reuse, claim-audit, and plan-tense rules in the current package; fresh reruns
then passed the rows above.

A same-model control with no project skill removed the obvious false claims but reused both sample
sentences and invented further testing and documentation work. The current skill therefore changed
material authorship and evidence behavior, not only routing. `EDIT-T03`, `EDIT-T04`, `EDIT-T07`,
`EDIT-T08`, `EDIT-W01`, `EDIT-W02`, `EDIT-W06`, `EDIT-W07`, and `EDIT-W10` remain unrun.

## Limits

Provider cases can show that the skill triggers, stays out of near misses, preserves truth and
authority, and materially improves a synthetic draft. They cannot establish a universal engagement
formula, audience response, search ranking, publication performance, or a named author's approval.
