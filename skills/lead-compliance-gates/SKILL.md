---
name: lead-compliance-gates
description: Use when designing, implementing, reviewing, or operating U.S. compliance gates for performance-marketing leads, ping/post marketplaces, outbound calls, robocalls, artificial or prerecorded or AI voice, or marketing SMS; or when evaluating TCPA, FTC TSR, National or state DNC, consent, suppression, revocation, lead transfer, or audit evidence. It supplies a source-backed workflow for resolving concurrent federal, state, privacy, vertical, and carrier rules into fail-closed, reconstructable decisions. Do not use it as legal advice, for non-U.S. campaigns, or for privacy work unrelated to marketing contact.
---

# Lead Compliance Gates

Build a decision system, not a `consent=true` checkbox. A contact or data transfer is permitted only
when every applicable layer passes for the same consumer, seller, purpose, channel, technology,
jurisdiction, and moment.

This skill supplies engineering and review guidance. It does not determine legal strategy or replace
qualified counsel. Have counsel approve applicability, interpretations, exceptions, consent language,
retention conflicts, and the versioned rule profiles used for live traffic.

## Route the work

Read only the references needed for the task:

- Read [federal-telemarketing.md](references/federal-telemarketing.md) for TCPA, FCC, FTC TSR,
  National DNC, robocalls, robotexts, revocation, caller ID, or recordkeeping.
- Read [state-privacy-and-vertical-overlays.md](references/state-privacy-and-vertical-overlays.md)
  whenever real U.S. traffic, lead transfer, state law, privacy, health or insurance data, call
  recording, email, or carrier messaging is in scope.
- Read [gate-architecture.md](references/gate-architecture.md) when designing data models, APIs,
  decision services, vendor adapters, evidence, reason codes, testing, or operations.
- Read [sources.md](references/sources.md) before asserting a legal requirement, and recheck live
  primary sources when the decision affects current traffic.

Use a separate research workflow for current law. Do not rely on memory, snippets, vendor summaries,
or this skill's checked date as proof that a rule is still current.

## Establish the decision facts

Do not evaluate a campaign until these facts are explicit:

1. Identify every actor and role: publisher, lead generator, marketplace, seller legal entity,
   telemarketer, service provider, buyer, controller or processor, data broker, agent, and carrier.
2. Identify the consumer's likely residence and current location, the caller or sender location, and
   the source and confidence for each. An area code alone is not reliable location evidence.
3. Classify each event by channel and technology: manual live voice, ATDS, prerecorded or artificial
   or AI voice, SMS/MMS, email, voicemail, warm transfer, or data-only ping/post.
4. Classify purpose and content: advertising, telemarketing, informational, transactional, survey,
   charity, emergency, mixed, or another counsel-approved category. Mixed marketing content is not
   made informational by its label.
5. Identify the seller and product the consumer would reasonably understand, the exact recipients of
   the data or contact permission, and whether affiliates are involved.
6. Inventory the data fields, inferences, collection purpose, transfer purpose, downstream uses,
   vertical, and any sensitive, health, financial, insurance, precise-location, biometric, or minor data.
7. Locate the exact consent and acquisition evidence: rendered disclosure, affirmative action,
   signature, number, seller or recipients, channels, technology, purpose, timestamp, source, creative,
   form state, disclosure version, and subsequent revocations.
8. Record the proposed contact time, recipient-local time, prior attempts across every vendor and
   campaign, DNC list versions, registrations, licenses, and claimed exemption or business relationship.

If a material fact is unknown, return `legal-review-required` or `deny`; never fill the gap with a
favorable assumption.

## Research the applicable layers

Research current primary authorities for every live campaign. Apply the rules concurrently:

1. FCC/TCPA contact and technology rules.
2. FTC TSR, National DNC, and seller-specific DNC rules.
3. Every applicable state solicitation, mini-TCPA, DNC, registration, bonding, hours, frequency,
   caller-ID, and recording rule.
4. State privacy, sale/sharing, targeted-advertising, universal opt-out, sensitive-data, consumer
   health-data, and data-broker duties.
5. Vertical rules such as insurance producer licensing or Medicare TPMO requirements.
6. Carrier and provider messaging policies, kept distinct from law.

For each rule, store the authority, section, effective date, checked date, jurisdiction, scope,
interpretation owner, and supersession status. Use the most restrictive applicable result. Ask counsel
to resolve conflicts, exemptions, uncertain jurisdiction, or ambiguous definitions.

Do not freeze a 50-state matrix into code or prose without effective dates and an owner. State and
carrier rules change too frequently.

## Keep permissions separate

Never infer one permission from another. Model and test these independently:

- permission to collect data;
- permission or legal basis to use data for the stated purpose;
- authority to transfer, sell, or share data with a specific recipient;
- National DNC permission or an established-business-relationship exception;
- consent for a particular seller, number, channel, technology, and purpose;
- authority to record, transcribe, or analyze a call;
- carrier permission to send under a registered messaging campaign.

A privacy notice does not create TCPA consent. A TCPA disclosure does not erase a privacy opt-out. An
established business relationship does not override a seller-specific DNC request. A vendor certificate
is evidence to validate, not a legal decision.

## Evaluate the gates in order

Evaluate again immediately before each ping, post, call, text, email, transfer, retry, or queued send.

1. **Resolve applicability.** Bind the event to actors, jurisdictions, local time, channel, technology,
   purpose, vertical, and versioned rule profile.
2. **Verify party authority.** Check effective registrations, bonds, licenses, appointments, carrier
   programs, contracts, and the precise scope of any approved exemption.
3. **Verify evidence integrity.** Authenticate the source, preserve what the consumer actually saw or
   heard, validate chain of custody, and reject missing, altered, ambiguous, expired, or mismatched evidence.
4. **Resolve suppression and registry state.** Check seller and marketplace revocation, entity-specific
   DNC, National and state DNC, buyer suppression, privacy sale/sharing or targeting opt-outs, universal
   opt-out signals, email unsubscribe, SMS STOP, and applicable data-broker deletion suppression.
5. **Verify contact authority.** Give applicable consumer-directed suppression and opt-outs precedence.
   Treat a National or state registry match as an input to its own exception-aware gate: match the seller,
   number, purpose, channel, technology, disclosure, signature, recipients, effective time, and any current
   seller-specific permission, EBR, or state exception to the exact event.
6. **Authorize data transfer.** Classify the ping/post or warm transfer as sale, sharing, targeted
   advertising, processor delivery, or another disclosure and confirm the purpose, contract role, and
   consumer choice allow it before exposing data.
7. **Enforce contact policy.** Apply the strictest recipient-local hours and centralized frequency cap;
   verify caller ID, opening disclosures, scripts, abandonment controls, callback, and opt-out behavior.
8. **Minimize disclosure.** Send only fields necessary and authorized for that stage. Keep full lead PII
   out of non-winning pings and routine logs, metrics, alerts, reports, and exports. When a legal or regulatory
   evidence bundle needs consumer-linked proof, include only the necessary PII in an encrypted,
   access-controlled, audited export.
9. **Emit and preserve the decision.** Return `allow`, `deny`, or `legal-review-required` with rule and
   evidence references, missing facts, reason codes, policy version, and expiration or recheck time.

Applicable consumer-directed suppression has precedence over older consent, retries, auctions, and routing.
A later buyer or alternate channel must not be used to evade the consumer's applicable request. A National
or state DNC registry match is not automatically equivalent to a revocation: apply only the exceptions the
current rule profile allows for the exact seller and event.

## Default failure behavior

Fail closed when a required scrub, consent artifact, seller identity, jurisdiction, license, rule
profile, or vendor response is missing, stale, conflicting, or unavailable. Queue the event for bounded
recheck or legal review without releasing contact data.

An exception to fail-closed behavior needs a counsel-approved, versioned policy that states its exact
scope, evidence, owner, expiry, monitoring, and rollback. A vendor timeout must never silently become
permission.

## Process revocation and suppression

Accept clear revocations through any reasonable channel or language. Do not force consumers through one
exclusive method. Capture the request immediately, append an immutable event, derive current suppression,
cancel queued work, and propagate it synchronously to every relevant seller-side caller and vendor.

Use an internal SLA of immediate suppression even when a legal rule supplies a longer outer limit. Scope
the request according to the consumer's words and the counsel-approved rule profile. Preserve clarification
and confirmation messages without adding marketing.

Older, bundled, seller-mismatched, or out-of-scope consent never overrides a later suppression. Only a
subsequent, unambiguous, consumer-initiated re-permission event may alter its exact scope, and only after
separate validation under a counsel-approved rule profile. Preserve both events and their effective order.

The FCC's cross-category revocation scope is temporarily and partially waived through January 31, 2027
as of the checked sources. Treat that date as volatile, recheck the current FCC order, and do not depend
on the waiver to keep sending marketing after an opt-out.

## Distinguish the common traps

- The Eleventh Circuit vacated the FCC's 2023 categorical one-to-one and logical/topical PEWC additions.
  It did not create blanket permission for undisclosed buyers. Current PEWC and National DNC rules still
  require seller-linked proof, and other FTC, CMS, state, privacy, and deception rules remain independent.
- `Facebook v. Duguid` narrowed the federal ATDS definition. It did not remove prerecorded, artificial or
  AI voice, DNC, text, state-dialer, privacy, or carrier obligations.
- Under the FTC TSR, prerecorded sales-call permission must be obtained directly by the specific seller;
  a third-party lead generator's generic consent is not a substitute.
- A manual call can avoid an ATDS rule and still violate DNC, hours, registration, caller-ID, script,
  privacy, licensing, or state law.
- Passing the National DNC scrub does not pass entity-specific suppression, consent, privacy, state,
  recording, or vertical gates.
- Current FTC telemarketing recordkeeping is five years. Do not copy the stale two-year statement still
  present in an FTC long-form guide.
- CTIA and carrier requirements can be stricter than law, but label them `industry_policy`, not statute.

## Review consent and lead acquisition

Reject “consent farm” evidence that hides recipients, uses prechecked controls, misstates the offer,
implies false government or brand affiliation, changes content after capture, or cannot reproduce the
consumer experience.

Prefer a specific, affirmative, unbundled choice with visible seller identities and no purchase condition.
Archive the creative, landing page, partner list, rendered disclosure, form state, and event chain. Validate
that downstream product, script, seller, and use match those artifacts.

Bad:

```text
consent = true
trustedform_url = "..."
```

Good:

```text
seller = "Example Insurance Agency LLC"
number = "+15551234567"
channels = ["sms", "artificial_voice"]
purpose = "auto-insurance quote follow-up"
disclosure_version = "2026-08-12.3"
rendered_artifact_hash = "..."
affirmative_action = "unchecked_checkbox_selected"
captured_at_utc = "2026-08-12T16:04:05Z"
source = "publisher.example/auto-quote"
revocation_state = "none"
```

The good record is still evidence to test against current rules; it is not automatic permission.

## Require proof, not a green flag

Test at least:

- manual live calls to DNC-listed numbers;
- non-ATDS prerecorded or AI voice and non-ATDS marketing texts;
- stale National or state DNC data and the wrong seller's SAN or list;
- entity-specific DNC overriding consent or established business relationship;
- seller, affiliate, recipient, purpose, number, channel, technology, and disclosure mismatches;
- queued and retried work after revocation through voice, text, email, or a free-text request;
- stale or deceptive “reconsent” and valid later consumer-initiated re-permission;
- reassigned numbers and inconclusive lookup results;
- vendor timeouts, stale caches, partial propagation, and out-of-order events;
- recipient-local time, DST, uncertain location, and cross-vendor frequency aggregation;
- state rules stricter or broader than the federal ATDS or hours rule;
- privacy sale/sharing opt-out before ping and post;
- sensitive or health data, recording, insurance licensing, and Medicare-specific paths;
- exact historical reconstruction after rules, consent copy, vendors, or contracts change.

Do not claim safe harbor from the existence of written procedures alone. Prove training, list freshness,
monitoring, vendor enforcement, error isolation, correction, and complete records for the exact safe harbor.

## Deliver an actionable result

For design or review work, report:

1. scope, assumptions, actors, channels, technologies, jurisdictions, and missing facts;
2. applicable layers and current primary sources, clearly separating law, guidance, proposal, policy,
   recommendation, and inference;
3. a gate matrix with inputs, pass condition, denial or review reason, evidence, owner, and recheck trigger;
4. consent, suppression, revocation, data-transfer, and evidence models;
5. outage and failure behavior;
6. adversarial tests and operational monitoring;
7. legal-counsel decisions and volatile rules requiring live verification.

Never end with “TCPA compliant.” State which exact event may proceed, for which seller and purpose, under
which rule versions and evidence, and what would invalidate that decision.
