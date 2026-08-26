# Evaluate the experience before planning changes

Read this reference when mobile behavior, accessibility, field performance, third-party code, or
recovery may explain conversion performance. This is a planning review. It defines what evidence to
request and how it changes priority; it does not prescribe code or certify implementation.

## Review representative conditions

Ask for evidence from the device, browser, traffic, geography, and assistive-technology conditions
that materially represent the audience. A desktop screenshot cannot establish that a mobile form is
usable, and one synthetic speed score cannot establish real-user performance.

Review:

- whether the arrival promise, offer, proof, primary action, disclosures, and next step remain clear
  at narrow widths and zoom;
- whether keyboard, touch, autofill, validation, focus, error announcement, and back/restore behavior
  let a person complete or recover from the flow;
- field Core Web Vitals at the relevant URL or origin scope, together with traffic coverage and the
  observation window;
- layout shifts, delayed interaction, third-party cost, consent controls, and failures that occur
  before accepted conversion; and
- differences between served HTML, rendered behavior, analytics events, and the backend outcome.

Record missing evidence rather than treating absence of a complaint or a green lab score as proof.

## Classify the finding

| Class | Meaning | Planning response |
|---|---|---|
| Functional failure | A representative user cannot complete or recover from the intended path | Prioritize correction and direct verification; do not A/B test the defect |
| Accessibility failure | The path excludes or materially obstructs an applicable access mode | Route correction against the governing accessibility requirement and verify it directly |
| Performance risk | Field evidence or a representative diagnostic shows delay or instability at a consequential step | Name the affected population, likely contributor, and measurement required after correction |
| Persuasion hypothesis | The path works, but evidence suggests an alternative may improve comprehension, confidence, or motivation | Put the alternative into the experiment backlog with a decision rule |

Do not call a preference a defect. Do not call a failed task an experiment opportunity.

## Plan the handoff

For every correction or hypothesis, state:

```text
Observed condition:
Affected audience and step:
Evidence and limit:
Expected user consequence:
Required outcome:
Owning discipline:
Verification evidence:
Conversion metric or guardrail affected:
```

Content owns final words, design owns interaction and visual decisions, development owns the built
behavior, analytics owns implementation of the measurement contract, and compliance owners approve
regulated language or data use. The conversion plan connects those owners without taking over their
work.

## Avoid false proof

- A responsive mockup is not a rendered mobile path.
- A Lighthouse score is lab evidence, not a field Core Web Vitals result.
- Passing one automated accessibility scan does not prove task accessibility.
- A click event does not prove backend acceptance.
- A successful happy path does not prove validation, duplicate activation, slow network, or recovery.
- A correction being implemented does not prove conversion improvement; measure the agreed outcome
  after the change under a named observation window.

Use the evidence to rank the plan, then require the implementation owner to return rendered and
executed verification separately.
