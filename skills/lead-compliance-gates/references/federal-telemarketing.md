# Federal Telemarketing Baseline

Use this reference to classify the federal FCC/TCPA and FTC TSR layers. It is a researched engineering
aid checked August 12, 2026, not legal advice. Recheck the cited primary sources before live use.

## Start with the event, not the dialer label

Classify the seller, on-whose-behalf identity, purpose, destination, channel, and actual technology for
each outbound event. A single campaign can contain different legal paths.

| Event | Federal starting point | Do not infer |
|---|---|---|
| Manual live sales call | National and seller-specific DNC, hours, disclosures, caller ID, TSR records, state rules | “Not ATDS” does not mean allowed |
| ATDS call to wireless | Prior express consent; prior express written consent (PEWC) for advertising or telemarketing; all DNC/TSR layers | Equipment classification does not decide prerecorded voice or state law |
| Artificial, prerecorded, cloned, or AI voice | Consent or PEWC by destination and purpose; identification and opt-out mechanics; FTC direct-seller rule for prerecorded sales calls | An interactive or human-sounding AI voice is still artificial voice |
| Marketing SMS/MMS | FCC treats texts as calls; DNC applies technology-neutrally to marketing texts; consent, revocation, state, and carrier layers also apply | `Duguid` does not remove DNC |
| Commercial email | CAN-SPAM and privacy/suppression layers | Email is not outside the compliance system |

## Apply FCC/TCPA consent precisely

Current 47 C.F.R. § 64.1200 requires, absent a narrow exception:

- prior express consent for ATDS or artificial/prerecorded calls to covered wireless and similar lines;
- PEWC when those calls advertise or constitute telemarketing; and
- PEWC for artificial/prerecorded telemarketing to residential lines.

PEWC is a signed written agreement with a clear and conspicuous disclosure authorizing the seller to
deliver or cause advertising or telemarketing calls using an ATDS or artificial/prerecorded voice to the
specified number. It cannot be required as a condition of purchase. Electronic signatures can qualify.

`Facebook v. Duguid` requires random or sequential number generation for the federal ATDS definition.
Treat equipment-specific capacity questions as legal-review items. The decision affects only the ATDS
branch; it does not alter prerecorded/artificial voice, DNC, or state definitions.

AI-generated or cloned voice is an “artificial voice” under FCC 24-17. The FCC proposed a separate AI-use
disclosure in FCC 24-84, but no such final federal disclosure appears in the checked current rule. Label a
disclosure as transparency or state/policy control unless current authority says otherwise.

## Handle the one-to-one issue without overclaiming

The Eleventh Circuit vacated Part III.D of FCC 23-107, which had added categorical one-seller-at-a-time and
logical/topical relationship restrictions. FCC DA 25-621 restored the prior PEWC text effective August 29,
2025.

That does not authorize blanket partner consent:

- PEWC still requires clear authorization of the seller on the facts.
- For a number on National DNC, 47 C.F.R. § 64.1200(c)(2)(ii) separately requires a signed agreement between
  the consumer and seller saying this seller may contact the number.
- The FTC's prerecorded sales-call rule independently requires the specific seller to obtain permission
  directly from the consumer.
- Medicare TPMO, state, privacy, carrier, contract, and deception rules may be more specific.

Encode these as separate gates. Never use `fcc_one_to_one_vacated=true` as an allow condition.

## Apply National and entity-specific DNC independently

Use National DNC data no more than 31 days old. Each seller needs its own Registry subscription/SAN and
the area codes it calls. A telemarketer may work through a seller account, but must not buy once, split the
cost, reuse one seller's data for another, or use DNC data as a lead or enrichment list.

A Registry-listed number may receive a covered live sales call only when the seller proves an applicable
exception, such as:

- seller-specific signed permission; or
- a seller-specific established business relationship (EBR): generally a purchase or transaction within
  18 months, or inquiry/application within 3 months.

An entity-specific DNC request terminates EBR. Do not inherit EBR across affiliates unless counsel has
approved the exact facts and reasonable-consumer-expectation analysis.

Maintain the entity-specific DNC process as its own highest-precedence suppression. FCC procedures include
capturing the request at receipt, honoring it within no more than 10 business days, staff training, caller
and seller identification, affiliate scope based on the request and reasonable expectations, and the FCC's
five-year honoring period. The engineering default is immediate, indefinite enforcement unless a subsequent,
unambiguous, consumer-initiated re-permission event is separately validated under a counsel-approved profile.
Preserve the suppression and later event; do not let old, bundled, or seller-mismatched consent override it.

National registration is honored indefinitely; the FCC's five-year period is for honoring company-specific
DNC requests. FTC recordkeeping is a separate obligation. Do not conflate them.

## Process revocation through every reasonable method

Current § 64.1200(a)(10)-(12) recognizes reasonable revocation, including:

- interactive/key opt-out;
- plain-language replies such as STOP, QUIT, END, REVOKE, OPT OUT, CANCEL, or UNSUBSCRIBE;
- a designated website or phone number; and
- other methods a reasonable person would understand, with some voicemail and email requests creating a
  rebuttable presumption.

Do not prescribe one exclusive route. Honor within a reasonable time no longer than 10 business days;
engineering should suppress immediately. A single nonmarketing confirmation text is allowed under the
rule's constraints. Preserve category clarification without sending new marketing.

FCC DA 26-12 temporarily waives part of the rule that would extend one category's revocation to unrelated
future robocalls/robotexts through January 31, 2027. Its wording and future are volatile. Recheck it live,
preserve the consumer's actual request, and use a conservative same-seller marketing suppression by default.

## Enforce artificial and prerecorded message behavior

For artificial/prerecorded messages, verify the current FCC and FTC script order and mechanics together:

- identify the responsible legal entity and provide a non-premium callback number;
- provide interactive voice/key automated opt-out for covered marketing calls;
- provide an automated toll-free opt-out for voicemail/answering-machine delivery;
- record the request, add seller suppression, and terminate as required; and
- keep the callback mechanism live for the campaign.

For prerecorded sales calls, the FTC requires a signed written agreement obtained directly by the specific
seller from the recipient. It must identify the seller, number, authorization, and signature and cannot be
a purchase condition. A lead generator's generic agreement and an EBR are not substitutes.

Digital soundboard, voice mimicry, and cloned voice can fall into prerecorded/artificial rules. Route novel
technology to counsel rather than relying on product labels.

## Enforce hours, identity, and predictive-dialing controls

The federal baseline is 8 a.m. through 9 p.m. at the recipient's location; use the stricter applicable state
window. Unknown location should block or use a counsel-approved conservative window.

Transmit authorized, nonblocked caller ID. The displayed number must satisfy current answer, callback, and
DNC-request requirements. Promptly disclose the seller, sales purpose, and nature of the goods or services.

For predictive dialing, monitor each campaign and period:

- connect a representative within two seconds of a completed greeting;
- keep abandoned live answers at or below 3% under the rule's measurement method;
- allow at least 15 seconds or four rings before ending unanswered calls;
- use only the prescribed identification and automated DNC message when no agent is available; and
- retain the records proving every safe-harbor element.

Operate below the legal ceiling so a burst cannot cross it.

## Treat safe harbors as proof obligations

The DNC safe harbors do not cure illegal robocalls, scripts, caller ID, hours, or consent. They require an
isolated error plus implemented procedures, training, entity-specific suppression, current Registry data,
monitoring, enforcement, and records. A high error rate is evidence the procedure is ineffective.

The Reassigned Numbers Database safe harbor is also narrow. The caller must previously have the required
consent, query the most recent database with the number and consent date, receive an erroneous “no,” and
prove reliance. “Yes,” “no data,” an unqueried number, or bad consent does not qualify.

Vendors do not remove seller responsibility. The FTC assistance rule and FCC agency principles make
due diligence, audit rights, opt-out propagation, and accessible evidence material.

## Retain current FTC records

Current 16 C.F.R. § 310.5 generally requires five-year records. The call-detail duties became mandatory
October 15, 2024. Preserve, as applicable:

- seller, telemarketer, service provider, purpose, product, and consumer/B2B classification;
- direction, prerecorded status, calling/called numbers, UTC time and duration to the nearest second;
- script or message version, caller-ID value and authority, disposition, and transfer destination;
- exact consent request, purpose, consent copy, consumer/number, date, and underlying required facts;
- ads, scripts, promotional material, unique prerecorded messages, contracts, and last-use/expiry dates;
- seller-specific DNC requests; and
- Registry access entity/date, SAN, list version, and campaign.

Written allocation can divide recordkeeping work, but missing or unclear allocation can leave both seller
and telemarketer responsible. Preserve access after vendor or corporate changes.

The FTC's long-form guide still contains stale two-year text. Use current § 310.5 and the 2024 final rule.

## Route exemptions rather than returning allow

Bank, carrier, nonprofit, insurance, investment, B2B, inbound, direct-mail, charity, survey, political,
informational, emergency, HIPAA, and EBR classifications are fact-specific and incomplete. For-profit
vendors, upsells, mixed marketing, high-risk products, technology rules, or state law can restore duties.

An exemption only skips its named provision. Return to every remaining federal, state, privacy, vertical,
recording, and carrier gate.
