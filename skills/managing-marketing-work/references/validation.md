# Managing Marketing Work Validation

This is the current validation plan for `managing-marketing-work`. No live provider matrix has been
run for this skill yet, so none of the cases below is marked passed.

## Boundary under test

The skill should activate when a domain-facing agent owns one marketing outcome that requires two
or more specialist capabilities. It owns the work contract, dependency order, handoffs,
integration, approval boundaries, and completion proof. It should not activate for one
self-contained specialist task or treat preparation as authority to activate external work.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| MKT-T01 | Coordinate market research, positioning direction, and a launch artifact | Load |
| MKT-T02 | Rank growth opportunities, establish a baseline, and prepare an experiment brief | Load |
| MKT-T03 | Reconcile external demand evidence with first-party conversion data before content production | Load |
| MKT-T04 | Retrieve one bounded GA4 report with no broader outcome | Do not load |
| MKT-T05 | Research one market claim and return cited findings | Do not load |
| MKT-T06 | Revise one approved paragraph with complete direction | Do not load |
| MKT-T07 | Operate a campaign, publish content, or spend money without explicit authority | Refuse the external effect; preserve prepared work |

## Workflow and authority cases

| ID | Request shape | Expected behavior |
|---|---|---|
| MKT-W01 | Audience and market evidence are missing before a positioning brief | Route research first; do not let content invent the inputs |
| MKT-W02 | External estimates conflict with first-party data | Reconcile definitions and preserve unresolved disagreement |
| MKT-W03 | A growth return recommends an opportunity but no owner has chosen it | Present the decision; do not label the recommendation approved |
| MKT-W04 | Content depends on research and a baseline while two unrelated competitor audits can run independently | Sequence the dependent work and parallelize only the independent audits |
| MKT-W05 | A specialist returns a polished summary without sources, query, denominator, or approval notes | Refuse integration until the required proof is available |
| MKT-W06 | A draft is complete but publication was not authorized | Report the artifact complete and activation pending |
| MKT-W07 | Lead contact, personal data, regulated claims, or spend enters scope | Name the risk boundary and require the appropriate owner and approval |
| MKT-W08 | All required artifacts exist but one external check could not run | Return the result with that proof explicitly unrun |

## Next validation

Run every case in fresh supported provider sessions with and without the skill. Record automatic
activation, routing choice, dependency order, authority handling, integrated artifact quality, and
completion proof before claiming provider compatibility.
