# State, Privacy, and Vertical Overlays

Use this reference whenever a real lead, call, text, email, recording, or data transfer is in scope. It is
a routing guide checked August 12, 2026, not a complete 50-state digest or legal advice.

## Research every campaign's actual footprint

Before activation, use current official sources to research:

- consumer residence and location, caller/sender origin, seller and vendor locations, and which connecting
  facts each jurisdiction recognizes;
- definitions of solicitation, seller, caller, text, voicemail, automated dialing, prerecorded or artificial
  voice, EBR, inquiry, and consent;
- state DNC registries and cadence, federal-list incorporation, exemptions, hours, frequency limits, caller
  identity, registration, salesperson licensing, bonding, scripts, and records;
- privacy thresholds and exemptions, sale/sharing/targeted-advertising definitions, universal opt-out signals,
  sensitive data, assessments, consumer rights, appeals, and processor contracts;
- sector rules for the exact data, product, script, compensation, transfer, and actor; and
- current carrier and messaging-provider campaign rules.

Store effective and future-effective dates. Assign an owner to recheck changes. Do not infer residence from
area code or assume the caller's state is the only state that matters.

## State solicitation patterns

States can be stricter than, or define technology more broadly than, the federal TCPA. Representative
examples show the kinds of gates to research, not a universal rule:

- Florida includes calls, texts, and voicemail in its telephonic-sales framework; it has automated/recorded
  consent rules, a state DNC overlay, 8 a.m.–8 p.m. hours, a same-subject frequency rule, caller-ID duties,
  licensing, and bonding.
- Maryland's Stop the Spam Calls Act has its own written-consent and operational restrictions for calls,
  texts, and voicemail.
- Oklahoma has state automated-call, DNC, hours, frequency, registration, and bond requirements.
- Washington restricts automatic dialing/announcing devices, incorporates federal DNC into solicitation
  duties, requires registration in covered cases, and has its own identity, termination, time, and suppression
  rules.

Do not copy these requirements to another state. Build effective-dated profiles for the jurisdictions counsel
has approved, and default unresolved states to `legal-review-required`.

Centralize attempt counts across numbers, vendors, affiliates, and campaigns using the legally relevant seller,
consumer, and subject keys. Apply recipient-local time and a reliable timezone source. Require authorized,
reachable caller ID and jurisdiction-correct opening and termination behavior.

## Registration, licensing, and bonds

Consent cannot cure an unauthorized seller, call center, salesperson, agent, or campaign. Store each
registration, exemption, bond, license, line of authority, appointment, location, effective date, expiry,
permitted action, and approving source.

Do not inherit an exemption across affiliates or vendors. Block activation and dispatch when the exact actor,
jurisdiction, product, or action falls outside the approved authority.

## Privacy and lead transfer

Classify every ping, post, resale, warm transfer, enrichment, and downstream disclosure. Counsel must decide
whether it is a sale, sharing, targeted advertising, controller-to-processor delivery, service-provider use,
or another transfer under each applicable law.

Keep these gates independent from contact consent:

1. notice at collection and stated purpose;
2. field-level minimization and sensitive-data classification;
3. authority for collection and use;
4. authority for this recipient and transfer purpose;
5. sale/sharing/targeting opt-out and universal opt-out signals;
6. access, correction, deletion, appeal, and propagation workflows;
7. contracts, assessments, retention, and deletion conflicts; and
8. data-broker status, registration, deletion, and future-suppression duties.

California recognizes Global Privacy Control for covered sale/sharing opt-outs. Colorado, Connecticut, Oregon,
and other states have their own universal-signal requirements and effective dates. Capture the signal at every
collection surface, persist it to known identities as allowed, apply it before ping and post, propagate it, and
test actual network requests and downstream delivery.

California's DROP duties began affecting covered data brokers in 2026. Determine status with counsel; if
covered, run current official requirements for access cadence, identity matching, deletion, contractor
propagation, reporting, and future no-reacquisition suppression.

An entity- or data-level exemption such as HIPAA, GLBA, FCRA, or insurance status is not a blanket exemption.
Bind it to the exact entity, role, field, purpose, and jurisdiction. Apply ordinary privacy gates when that proof
is missing.

## Sensitive and consumer health data

“Not HIPAA” does not mean unregulated. State consumer-health laws can cover contact details, health status,
medication, disability, precise location, and inferred health data outside HIPAA.

Classify raw fields and inferences before collection. Where applicable, keep collection, sharing, and sale
permissions separate; name purchasers when required; block undeclared secondary use; govern contractors;
and preserve authorization and revocation evidence for the required period.

Washington's My Health My Data Act and Connecticut's health-data provisions illustrate why ordinary lead
consent is insufficient. Have counsel approve health-data definitions, exemptions, authorization form,
geofencing restrictions, retention, and deletion conflicts for each jurisdiction.

## Insurance and Medicare

Insurance producer authority varies by state and exact activity. Qualification, recommendation, quoting,
policy-term discussion, steering, warm transfer, and outcome-based compensation can change the result.

Store agent licenses, lines of authority, appointments, state, product, and permitted script actions. Route only
to an appropriately authorized agent under a counsel-approved profile. Do not treat an NAIC model law as
enacted state law.

Medicare Advantage and Part D third-party marketing organizations (TPMOs) have a separate federal overlay.
Current CMS rules include actor-specific licensing/training, Scope of Appointment, lead-generation disclosures,
recording and six-year retention for covered calls, and one-to-one prior express written consent naming each
TPMO that receives personal beneficiary data. The FCC one-to-one vacatur did not remove this CMS rule.

Treat Medicare as a distinct profile. Verify the named recipient before transfer, licensed/appointed agent,
required disclosure, call recording, retention, plan oversight, and privacy/health-data duties.

## Call recording, transcription, and AI analysis

Interstate calls can implicate different participant-state consent rules. Federal law generally permits one-party
consent in defined circumstances; states such as California and Washington can require all-party consent for
covered communications.

Have counsel decide applicable jurisdictions and approve a recording state machine. Where lawful, start by
recording the notice and affirmative response. Where that preliminary recording is not lawful, deliver the
notice off-record, preserve separate timestamped consent evidence, and begin recording only after consent.
In both paths preserve the exact notice, evidence, recording start time, and a recording-disabled fallback.
Treat transcription, sentiment analysis, model training, and AI-derived inferences as additional purposes
requiring their own privacy and retention analysis.

## Email and carrier messaging

CAN-SPAM covers commercial email, including B2B. Validate accurate sender/header/subject, ad identification,
postal address, a clear unsubscribe mechanism that remains available for the required period, opt-out completion
within 10 business days, suppression protection, and vendor monitoring. Use a shorter internal SLA.

CTIA messaging principles and provider A2P requirements are industry policies, not statutes. Keep them in a
separate `industry_policy` rule family. Validate current brand, sender, and campaign registration; approved use
case; matching opt-in flow and sample content; STOP/HELP behavior; complaint rates; and provider-specific
changes. Legal consent alone does not guarantee carrier permission or delivery.

## Truthful acquisition and vendor oversight

The FTC's lead-generation cases show that formal checkbox evidence can fail when the ad, reward, quote,
government affiliation, buyer identity, or data use is deceptive. Archive the complete consumer journey and
substantiate its claims.

Monitor publishers and buyers for complaint spikes, script or creative drift, hidden partner lists, misuse,
unlicensed activity, and suppression failure. Contract language alone is not proof. Maintain audit rights,
evidence access, thresholds, pause controls, and kill switches.

## Require counsel to decide

Stop and request counsel approval for:

- governing jurisdictions when residence, location, area code, caller origin, and entity location differ;
- whether a transfer is sale, sharing, targeting, service-provider processing, or data-broker activity;
- every claimed EBR, inquiry, B2B, nonprofit, insurer, HIPAA, GLBA, FCRA, or other exemption;
- consent wording, seller identification, recipient enumeration, signature, revocation, and re-permission;
- sensitive or consumer-health classification and permissions;
- insurance licensing boundaries for the exact script, handoff, compensation, and product;
- Medicare TPMO status, named-recipient consent, Scope of Appointment, recording, and retention;
- interstate call-recording rules and transcript or AI-analysis purpose;
- deletion versus legal hold or regulatory retention; and
- campaign claims, government/brand affiliation, benefits, price, reward, or quote substantiation.
