# Inference from public artifacts, and its ceiling

Each signal here is real evidence about something narrower than people usually claim. The pattern is
identical every time: the artifact establishes intent or configuration, and gets over-read as
outcome or scale.

## Job postings

Economic research uses vacancy postings legitimately, on a stated basis: adoption can be **partially
identified from the footprints it leaves** at adopting establishments as they hire workers specializing
in the relevant activities. Note "partially identified" — that is the honest framing.

The known biases of the underlying data, from that literature: it is assembled from tens of thousands
of company sites and job boards with a cap on how much comes from any one source, and online vacancy
postings **overrepresent technical and professional roles** relative to blue-collar and personal
service work.

**Legitimately establishes:** hiring intent, team composition, named tools and stack, and geography.
A rival posting for four roles naming a specific technology is real evidence they use it.
**Over-read as:** headcount — postings are a flow, not a stock; revenue; roadmap dates; or current
activity, when a stale unfilled posting may have sat there for months.

## Status pages

Operator-authored, not measured. The platform documentation makes this unavoidable: if you have
incidents but do not put components into one of the relevant states, **nothing appears on the
component's timeline**; you may have had an incident and forgotten to update the page; historical
uptime can be edited; components are updated manually; and third-party component status can be
overridden at any time.

**Legitimately establishes:** what the vendor chose to disclose about its own availability.
**Over-read as:** an independent availability measurement or an SLA verification. Published uptime is
a self-report with an editable history.

## Technology detection

Detection works from signals a site emits, indexed by crawling. The one vendor in this category with a
first-party accuracy statement puts it plainly: detections are **based on signature evidence and may
not be 100% accurate**, and completeness and accuracy are not warranted. It names the false-positive
causes — sites including unused technology code, signatures remaining after removal, and indexing
delays.

**Legitimately establishes:** that a signature associated with a technology was present at crawl time.
**Over-read as:** the current stack, an exclusive choice, or a contract. A removed tool leaves
signatures; an evaluated tool leaves code.

Where a detection matters to a conclusion, verify it directly against the live page rather than
trusting an aggregator — and note that verifying what a page serves is retrieval work with its own
evidence standard.

## Certificates and DNS

Certificate transparency exists to provide **publicly auditable, append-only logs of all issued
certificates**, and anyone can query a log and verify it is behaving. Importantly, **anyone can submit
a chain to a log.**

**Legitimately establishes:** hostnames and subdomains that appeared, and roughly when.
**Over-read as:** a launch date, a customer list, or a product decision. A subdomain in a log is a
certificate request, not a shipped feature — and because submission is open, presence is weaker
evidence than it looks.

## Funding announcements

See `filings-and-registries.md` for the statutory notice. The short version: the notice gives amount
sold within 15 days of first sale and **contains no valuation item**. A valuation is whatever the
announcement said, attributable only to whoever said it.

## Changelogs, release notes, and docs

The most honest signal in this file, because a vendor writing documentation is describing what they
built rather than what they want you to believe. Read them for:

- **Capability existence** — at the documented tier, not the reproduced one.
- **Constraints** stated in passing: limits, quotas, unsupported combinations. Documentation admits
  things marketing does not.
- **Deprecations**, which reveal direction more reliably than announcements.

Do not read them for roadmap dates, priorities, or relative investment. Cadence is a fact about a
team's process.

## The rule that covers all of them

Every signal here is a by-product of something the company did for another reason. That is why it is
credible about configuration and intent, and why it is worthless about outcome and scale. Write down
which of the two your claim needs — and where you have only intent evidence for an outcome claim, say
the claim is not established and name what would establish it.
