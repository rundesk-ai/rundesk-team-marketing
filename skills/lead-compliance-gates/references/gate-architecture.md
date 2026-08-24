# Gate Architecture and Proof

Use this reference to turn ratified legal and policy profiles into a deterministic, auditable decision system.
The controls below are engineering recommendations, not statements of law.

## Separate the planes

Keep four boundaries explicit:

1. **Policy plane:** versioned, counsel-approved applicability, rules, exceptions, effective dates, sources,
   interpretations, and owners.
2. **Evidence plane:** append-only consent, disclosure, acquisition, list check, revocation, rights, license,
   contract, and vendor artifacts.
3. **Decision plane:** synchronous evaluation immediately before every disclosure or contact attempt.
4. **Execution plane:** pings, posts, dialers, messaging vendors, email providers, transfers, retries, and queues
   that cannot bypass the decision token or current suppression.

Do not put legal interpretation inside a vendor adapter. Normalize providers into evidence and let the policy
plane decide.

## Model immutable facts and derived state

Prefer append-only events plus reproducible projections. Do not overwrite history when consent is revoked,
a DNC list changes, a license expires, or a rule is amended.

Useful entities include:

- `party`: legal entity, role, aliases, relationships, registrations, exemptions, licenses, appointments;
- `consumer_key`: privacy-safe identifiers and authorized matching methods;
- `contact_point`: normalized number/email, ownership evidence, reassignment checks, jurisdiction evidence;
- `campaign`: seller, telemarketer, purpose, product, vertical, channels, technologies, jurisdictions;
- `consent_artifact`: consumer, seller/recipients, number, purpose, channels, technologies, exact disclosure,
  render, signature event, source, creative, timestamp, version, chain of custody;
- `suppression_event`: scope, actor, source, wording, channel, reason, received time, propagation status;
- `registry_check`: seller SAN, subscribed scope, list source/version, check time, result, campaign;
- `authority_record`: registration, bond, license, appointment, carrier enrollment, scope, effective window;
- `rule_profile`: jurisdiction, authority, section, interpretation, effective window, checked date, owner;
- `contact_attempt`: seller, consumer, subject, vendor, channel, technology, UTC/local time, caller ID, script,
  outcome, opt-out, transfer, delivery, and retry lineage; and
- `decision`: facts snapshot/hash, policy version, evidence references, result, reasons, expiry, evaluator version.

Encrypt and tightly authorize sensitive evidence. Put tokens, hashes, and reason codes—not raw lead payloads—
in ordinary logs, metrics, traces, alerts, tickets, and exported reports.

## Use explicit scopes

Scope suppression and permission separately by fields such as:

- seller legal entity and on-whose-behalf entity;
- affiliate group only when approved and reasonably expected;
- contact point and matched consumer identity;
- purpose, subject, product, and campaign;
- channel and technology;
- data collection, use, transfer, sale/sharing, or contact;
- recipient/buyer; and
- effective and expiry time.

Store the consumer's original words and a derived legal scope. Never discard the original request when the
interpretation changes.

## Define a narrow decision contract

A decision service can expose:

```text
evaluate(action, actor_set, consumer, destination, campaign, payload_fields, proposed_at)
  -> result: allow | deny | legal-review-required
     reason_codes[]
     applied_rule_versions[]
     evidence_refs[]
     missing_facts[]
     valid_until
     decision_token
```

The execution plane must bind the token to the exact action, seller, destination, payload-field set, purpose,
channel, and time. A token for a ping must not authorize a post, call, alternate buyer, retry, or another channel.

Use short validity. Recheck suppression and time-sensitive rules at dispatch, even when selection or auction
happened earlier. Make the final suppression read and work release atomic enough that a concurrent revocation
cannot leak queued work.

## Evaluate in deterministic precedence

Recommended precedence:

1. malformed, untrusted, or missing identity/evidence;
2. explicit consumer suppression and privacy rights;
3. current party authority and campaign eligibility;
4. contact-point ownership/reassignment and DNC lists;
5. channel/technology/seller/purpose consent or approved exception;
6. data-transfer permission and minimization;
7. local-time, frequency, caller ID, script, abandonment, and carrier controls;
8. release and immutable audit.

Return all useful denial reasons without exposing private rules to unauthorized parties. Do not evaluate consent
first and stop before discovering an active DNC request.

## Version rules and exceptions

Every production rule should include:

```text
rule_id, version, jurisdiction, authority_kind, authority_url, section,
effective_from, effective_to, checked_at, facts_required, decision,
interpretation_owner, approved_by, supersedes, recheck_trigger
```

Distinguish `law`, `court_decision`, `agency_order`, `agency_guidance`, `proposal`, `industry_policy`,
`contract`, and `engineering_recommendation`.

Exceptions need the same rigor: exact provision skipped, facts, evidence, owner, approval, expiry, monitoring,
and remaining gates. An exception must never return a global allow.

Use effective-date tests around every change. Alert before waivers, registrations, licenses, contracts, consent,
or rule profiles expire. Block traffic when a required profile is stale.

## Normalize provider evidence

Wrap DNC, consent-certificate, reassigned-number, carrier, license, and privacy vendors behind typed adapters.
Capture request identity, source version, requested facts, response, latency, error class, checked time, expiry,
and raw evidence reference.

Reject provider booleans that hide scope. For example, `dnc_pass=true` must become seller, list sources,
versions, SAN, state profiles, entity suppression, check time, and results.

Set hard deadlines and circuit breakers. Timeout, malformed response, stale cache, unknown result, mismatched
seller, or unverifiable certificate yields hold or review—not allow. Cache only within the source's lawful and
operational freshness window and key it to every fact that can change the outcome.

## Preserve reconstructable consent

Evidence should show what the consumer actually experienced:

- creative/ad and offer;
- page/audio/script and URL/source;
- complete rendered disclosure and visible recipient list;
- control state, affirmative action, signature method, and no-purchase-condition presentation;
- seller legal name, purposes, channels, technologies, number, recipients, and data fields;
- UTC timestamp, relevant local context, source IP/device only when lawful and necessary;
- disclosure, partner-list, and application versions plus hashes;
- certificate/vendor lineage and integrity checks; and
- every amendment, revocation, clarification, re-permission, and propagation outcome.

A URL that now renders different content is insufficient. Preserve a versioned render or equivalent artifact.

## Centralize suppression

The suppression service should:

- accept voice, text, email, web, agent, privacy-signal, partner, complaint, and regulator inputs;
- preserve free text and derive counsel-approved scope;
- apply before auction/ping when transfer is barred and again before post/contact;
- cancel queues, retries, transfers, and vendor work synchronously;
- propagate to authorized downstream processors without disclosing lists to unrelated sellers;
- record acknowledgements, failures, deadlines, retries, and escalation; and
- retain enough history to prove the state at any prior decision time.

Never use suppression data as targeting, enrichment, or a “do-call” list.

## Design reason codes for action

Use stable, specific reason families, for example:

```text
FACT_JURISDICTION_UNKNOWN
PARTY_LICENSE_EXPIRED
EVIDENCE_CONSENT_MISSING
EVIDENCE_SELLER_MISMATCH
SUPPRESSION_ENTITY_DNC
SUPPRESSION_NATIONAL_DNC
SUPPRESSION_CONSENT_REVOKED
SUPPRESSION_SCOPE_REVIEW
SUPPRESSION_PRIVACY_TRANSFER
DNC_REGISTRY_STALE
CONTACT_REASSIGNED_OR_UNKNOWN
CONTACT_OUTSIDE_LOCAL_WINDOW
CONTACT_FREQUENCY_EXCEEDED
TRANSFER_PURPOSE_UNAUTHORIZED
VENDOR_TIMEOUT_FAIL_CLOSED
RULE_PROFILE_STALE
LEGAL_EXEMPTION_UNRATIFIED
```

Map each code to operator guidance, consumer-safe wording, retryability, owner, and evidence without embedding
raw PII.

## Test invariants and failure modes

Use deterministic clocks, versioned fixtures, concurrent dispatch/revocation tests, and fake provider responses.
Prove at least:

- no explicit suppression can be overridden by EBR, older or mismatched consent, priority, price, retry, or
  another buyer; only a later, consumer-initiated re-permission event can alter the exact scope after separate
  validation under a counsel-approved profile;
- no payload field or contact event is released without a fresh action-bound allow token;
- the same historical facts and rule versions reproduce the same result;
- a new rule version changes only its effective window;
- expired/stale/unknown evidence cannot pass;
- a seller, affiliate, purpose, number, channel, technology, or recipient mismatch cannot pass;
- revocation racing a queued dispatch prevents release;
- stale or deceptive “reconsent” remains blocked while valid later consumer-initiated re-permission is modeled
  as a new ordered event, never a history rewrite;
- provider timeout, malformed response, partial outage, and stale cache fail closed;
- timezones, DST boundaries, unknown location, and stricter state windows are conservative;
- attempt counts aggregate across vendors and originating numbers;
- ping-safe fields never include post-only PII;
- privacy opt-out blocks transfer before buyer disclosure;
- every decision can be reconstructed without relying on current mutable state; and
- logs and reports contain no prohibited PII or complete suppression lists.

Property tests should assert safety invariants. Scenario tests should cover legal and policy profiles. Contract
tests should verify every execution adapter refuses missing, expired, or mismatched decision tokens.

## Operate and monitor

Monitor by seller, campaign, vendor, source, jurisdiction, channel, and reason:

- denied and review-required rates;
- list and rule-profile freshness;
- consent/evidence mismatch;
- opt-out capture-to-suppression and downstream acknowledgement latency;
- queued-work cancellation failures;
- vendor errors, timeouts, and circuit state;
- attempts near legal/policy frequency and abandonment ceilings;
- complaint and DNC-request rates;
- caller-ID, script, license, registration, and carrier drift; and
- missing or irreconstructable audit events.

Provide kill switches at seller, source, campaign, buyer, jurisdiction, channel, technology, and vendor scope.
Treat compliance ambiguity and unexplained evidence gaps as incidents, not conversion losses to work around.

## Produce a gate matrix

For each gate, document:

| Field | Meaning |
|---|---|
| Action | Ping, post, call, text, email, record, transfer, retry, or other event |
| Facts | Exact inputs and confidence/source |
| Rule | Versioned authority or policy |
| Pass | Observable conditions for this event |
| Deny/review | Specific reason and missing facts |
| Evidence | Immutable references retained |
| Failure behavior | Hold, cancel, retry, or escalate |
| Owner | Policy, system, vendor, operations, or counsel |
| Recheck | Dispatch, expiry, revocation, rule change, or incident |

The matrix is incomplete if `consent passed` is its only contact criterion.
