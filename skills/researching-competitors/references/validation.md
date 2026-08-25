# Researching Competitors Validation

This is the current validation plan for `researching-competitors`. No live provider matrix has been
run for this skill yet, so none of the cases below is marked passed. Record a case only from a run
someone watched.

## Boundary under test

The skill should activate when a question asks who the competitors are, how a rival's business,
pricing, or positioning works, what their product can do, or how offerings compare. It should not
activate for auditing a competitor's site as a serving surface, for first-party analytics, or for
writing the comparison page that results.

Two boundaries carry the risk. The first separates a competitor **as a business** — established by
citing a record someone else can look up — from a competitor **as a serving surface**, established by
retrieving it. The second is **claim discipline**: a published price is not a realized price, a
superlative is a claim rather than a fact, a rating is sentiment rather than capability, and a
comparison without criteria, version, date, and evidence tier is unfalsifiable.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| CMP-T01 | "Who are our competitors and how do they make money?" | Load |
| CMP-T02 | "Break down their pricing against ours" | Load |
| CMP-T03 | "How do they position themselves?" | Load |
| CMP-T04 | "Build a feature comparison for the three of us" | Load |
| CMP-T05 | "Did they really raise $40M at a $400M valuation?" | Load |
| CMP-T06 | "Audit their site's indexing and canonicals" | Do not load; site retrieval |
| CMP-T07 | "What's our win rate against them in the CRM?" | Do not load; first-party analytics |
| CMP-T08 | "Write the competitor comparison landing page" | Do not load; content production |
| CMP-T09 | "How big is this whole category?" | Do not load; market sizing |

## Evidence and claim cases

| ID | Request shape | Expected behavior |
|---|---|---|
| CMP-W01 | A competitor's pricing page lists $79 per seat | Report the published offer and its metering; state that list is not presumed to be the realized price |
| CMP-W02 | A press release states a funding round and a valuation | Cite the statutory notice for the amount sold; report the valuation as the announcer's claim, since the form has no valuation item |
| CMP-W03 | A competitor advertises itself as "#1" | Record it as their claim, note whether a basis was published, and do not repeat it as fact |
| CMP-W04 | Asked whether our own "#1" claim is safe | Name the substantiation standard and the broad-category comparison expectation, flag the exposure, and route the legal question rather than opining |
| CMP-W05 | Their rating is 4.6 and ours is 4.1 | Refuse the quality inference; establish whether the populations and solicitation programs are comparable first |
| CMP-W06 | G2, Capterra and GetApp all show the same ranking | Say that these are one company and do not treat the agreement as independent corroboration |
| CMP-W07 | Asked to build a capability matrix | Fix the criteria before knowing who wins, and mark each cell documented, inspected, or reproduced |
| CMP-W08 | A capability is unknown for one product | Write not established; do not leave an empty cell that reads as absence |
| CMP-W09 | Asked to benchmark a rival's product ourselves | Describe the competitor configuration fully, apply the same tuning effort, and treat a result that contradicts published data as a reason to re-check |
| CMP-W10 | Only a pre-2001 filing would answer the question | Say full-text filing search does not reach it and name another route |
| CMP-W11 | No patent applications appear for a rival | Refuse the inference; publication lags 18 months and can be withheld entirely |
| CMP-W12 | A status page shows 99.99% uptime | Report it as a self-report with an editable history, not a measurement |
| CMP-W13 | A technology detector reports their stack | Report it as a signature present at crawl time, and verify directly where the conclusion depends on it |
| CMP-W14 | Job postings suggest a team of 40 engineers | Refuse the headcount inference; postings are a flow and overrepresent technical roles |
| CMP-W15 | A UK registry filing shows no profit and loss account | Explain the small-company exemption and its April 2028 change rather than reading absence as concealment |

## Next validation

Run every case in fresh supported provider sessions, with and without the skill installed, using
ordinary requests that never name the boundary under test. Retrieve the relevant filings, pricing
pages, and platform policies independently first, so a sourced claim can be distinguished from a
plausible one. Record activation, whether business and serving-surface evidence stayed separate,
whether every price and superlative carried its provenance, and whether any comparison shipped without
criteria, version, date, and evidence tier.
