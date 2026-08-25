# Brief — rundesk-team-marketing

*What this team is and why it exists. One screen, and it changes when the team does.*

## Story

`rundesk-team-marketing` is Rundesk's research, growth, analytics, and messaging team, kept as one
versioned artifact. Four named agents: **beacon** owns organic and AI search end to end, **scout**
researches markets, customers, and competitors from published sources, **signal** certifies
first-party data, and **quill** writes requirements, documentation, and messaging from an approved
brief.

The catalog also declares the shared integration catalogs its members borrow, so a member can reach
a service without this repository shipping one.

## Why it exists

Marketing claims are the easiest kind to get wrong confidently. A ranking opportunity, a competitor
fact, a conversion number, and a customer quote all read the same on a slide, and only some of them
can be traced back to anything.

Splitting the work by evidence class is the point: what was retrieved and can be retrieved again,
what was published by somebody else and is cited, and what is first-party and needs a denominator
before it means anything. A member that mixes them produces work nobody can check.

## Users

- The domain agent that calls this team for research, search, analytics, or content work.
- The owner, who installs the team and can see which member holds which service grant.

*Sourced from the readme, the team declaration, and the member instruction files.*

## Scope

- **Covers:** the four members and their canonical instructions; guidance for search, growth
  analytics, market and customer research, competitor research, data verification, requirements,
  documentation, and landing pages; and the declared dependencies on shared integration catalogs.
- **Refuses:**
  - Presenting an uncertified number as fact. First-party analysis carries a denominator or is
    returned as unestablished.
  - An external claim with no published source behind it.
  - Shipping its own service commands. Integrations are borrowed from declared catalogs.
  - Turning consumer documentation into maintainer state.
  - Promising an evidence class a member cannot actually deliver — the gaps are written down rather
    than worked around.

## External systems

- Shared integration catalogs, declared as dependencies rather than vendored, for analytics, search,
  and product data.
- Rundesk — installs the catalog and its dependencies, creates and reconciles the members.
- GitHub — hosts the repository and serves the release an install fetches.
