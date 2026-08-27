# Brief — rundesk-team-marketing

*What this team is and why it exists. One screen, and it changes when the team does.*

## Story

`rundesk-team-marketing` is Rundesk's research, growth, and messaging team, kept as one versioned
artifact. Three named agents: **beacon** reports traceable growth evidence, first-party measurement,
and supplied-data verification without choosing what to do; **scout** researches markets, customers,
and competitors from published sources; and **quill** writes requirements, messaging, editorial
work, organic social and paid advertising copy, and other marketing content for a defined audience
from approved direction and evidence.

The catalog also declares the shared integration catalogs its members borrow, so a member can reach
a service without this repository shipping one.

## Why it exists

Marketing claims are the easiest kind to get wrong confidently. A ranking opportunity, a competitor
fact, a conversion number, and a customer quote all read the same on a slide, and only some of them
can be traced back to anything.

Separating evidence classes is the point: Beacon keeps retrieved growth evidence distinct from
first-party or supplied measurements and exposes the inputs and arithmetic behind derived numbers,
while Scout returns claims published by somebody else with citations. The requesting agent, not
Beacon, ranks options and decides what the evidence means for action.

## Users

- The domain agent that calls this team for research, search, analytics, or content work.
- The owner, who installs the team and can see which member holds which service grant.

*Sourced from the readme, the team declaration, and the member instruction files.*

## Scope

- **Covers:** the three members and their canonical instructions; guidance for search, growth
  analytics, market and customer research, competitor research, data verification, requirements,
  messaging, editorial content, organic social and paid advertising copy for named platform
  surfaces, and marketing content; and the declared dependencies on shared integration catalogs.
- **Refuses:**
  - Presenting an uncertified number as fact. First-party analysis carries a denominator or is
    returned as unestablished.
  - Returning a percentage without its physical inputs, formula, source, and comparable windows.
  - Turning Beacon's report into a ranking, recommendation, verdict, or decision.
  - An external claim with no published source behind it.
  - Shipping its own service commands. Integrations are borrowed from declared catalogs.
  - Taking technical-documentation work owned by the development team.
  - Treating social-copy authorship as account access, scheduling, publishing, or engagement.
  - Treating ad-copy authorship as keyword-volume research, targeting, budget, campaign operation,
    upload, launch, or certified performance.
  - Promising an evidence class a member cannot actually deliver — the gaps are written down rather
    than worked around.

## External systems

- Shared integration catalogs, declared as dependencies rather than vendored, for analytics, search,
  and product data.
- Rundesk — installs the catalog and its dependencies, creates and reconciles the members.
- GitHub — hosts the repository and serves the release an install fetches.
