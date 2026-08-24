# Product-requirements source map

Use this file to audit a lesson, not as another PRD procedure. This package synthesizes product
practice, public-service guidance, systems standards, community methods, and empirical requirements
research. It does not impose one organization's template.

Verified 7 August 2026 against the linked pages, except the domain-vocabulary entry under
"Requirement quality and acceptance", which was added and verified on 13 August 2026.

## Product intent and readable shape

- [GOV.UK: Learning about users and their needs](https://www.gov.uk/service-manual/user-research/start-by-learning-user-needs)
  distinguishes high-level user needs from solution-shaped user stories, recommends wording users
  recognize, treats unsupported suggestions as assumptions, and links stories back to needs. This
  supports separating explicit direction, observed need, proposed solution, and evidence.
- Marty Cagan's [How to Write a Good PRD](https://svpg.com/assets/Files/goodprd.pdf) is a 2005
  practitioner essay that separates market opportunity, product strategy, and one release; emphasizes
  value proposition, target users, goals, priority, release criteria, and keeping the PRD useful
  through launch. It is respected but dated, high-tech-oriented, and non-empirical.
- Cagan's [Requirements Are Not](https://www.svpg.com/requirements-are-not/) and
  [The End of Requirements](https://www.svpg.com/the-end-of-requirements/) argue that many customer
  and stakeholder “requirements” are solution hypotheses for unstated problems and that product
  discovery remains iterative. This package applies that warning without dismissing explicit user
  authority, genuine constraints, or the need for an approved product contract.
- [Atlassian's PRD guidance](https://www.atlassian.com/agile/product-management/requirements) is
  vendor/practitioner evidence for concise “just enough” context, goals, assumptions, questions,
  design links, explicit non-goals, team collaboration, regular updates, and leaving ordinary
  implementation detail to delivery specialists. Its product incentives mean it is corroborating
  practice, not causal evidence.
- Ryan Singer's [Shape Up: Write the Pitch](https://basecamp.com/shapeup/1.5-chapter-06) provides
  practitioner examples organized around problem, appetite, solution, rabbit holes, and no-gos. The
  package borrows the failure-preventing shape—problem before solution, visible risks, explicit
  exclusions—not Basecamp's fixed process or cycle length.
- AWS Prescriptive Guidance,
  [Developing product strategies that deliver measurable business value](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/strategy-product-development/strategy-product-development.pdf),
  describes working backward from the current and target customer journey to clarify scope, customer
  value, and business outcomes before feature planning. It supports plain customer-facing product
  framing without requiring Amazon's PR/FAQ artifact.

## Requirement quality and acceptance

- [NASA: How to Write a Good Requirement](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/)
  supplies checks for clear, concise, singular, feasible, consistent, and verifiable requirements;
  visible assumptions; and measurable qualities. NASA's engineering rigor is scaled here to product-
  consequential ambiguity rather than imposed wholesale on ordinary feature work.
- [INCOSE's Requirements Working Group](https://www.incose.org/group/requirements-working-group/)
  maintains guidance spanning needs, requirements, verification, and validation. Its published
  [Guide to Writing Requirements v4 summary](https://www.incose.org/docs/default-source/working-groups/requirements-wg/guidetowritingrequirements/incose_rwg_gtwr_v4_summary_sheet.pdf)
  supports necessary, unambiguous, singular, feasible, comprehensible, and verifiable requirement
  statements. The full guide is a systems-engineering practice, not a required PRD schema.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) defines a product-quality model that
  can inform requirements, measures, testing objectives, and acceptance criteria. The package uses
  quality categories as a coverage prompt and explicitly rejects enumerating every quality for every
  product.
- Eric Evans' [Domain-Driven Design Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
  (March 2015) supports the one-term-per-concept rule. Its Ubiquitous Language pattern commits a team
  to one language "in all communication within the team and in the code", holds that "a change in the
  language is a change to the model", and expects domain experts to "object to terms or structures
  that are awkward or inadequate to convey domain understanding". This package applies that to the
  document's vocabulary only; identifier form in code and schemas belongs to `database-design`.
  The measured cost of leaving a term unstated comes from
  [Feitelson et al., "How Developers Choose Names", arXiv:2103.07487](https://arxiv.org/pdf/2103.07487)
  (2021, 334 subjects): across 47 instances "the median probability" that two developers chose the
  same name "was only 6.9%", so an unfixed term is resolved by guesswork rather than convention. The
  study measures developers naming code, not stakeholders reading a PRD; it establishes the
  divergence, not a PRD-specific effect size.
- The Agile Alliance's [Definition of Done](https://agilealliance.org/glossary/definition-of-done/)
  is community guidance for one shared quality bar across product increments. It supports separating
  a team-wide done contract from feature-specific acceptance and post-release product success.
- The official [Scrum Guide](https://scrumguides.org/scrum-guide.html) defines the product backlog as
  emergent, ties it to a product goal, and distinguishes the increment's Definition of Done from the
  actionable implementation plan. The package uses only those transferable boundaries; it does not
  require Scrum or user-story syntax.

## Outcome and implementation evidence

- [Department for Education product principle: Be accountable for your outcomes](https://ddt.beta.education.gov.uk/guides/product-management-principles/principle-3-be-accountable-for-your-outcomes)
  distinguishes the benefit or change users experience from the output shipped, recommends a small
  useful measure set, and asks teams to observe adverse as well as desired effects.
- [GOV.UK: Define what success looks like](https://www.gov.uk/service-manual/service-standard/point-10-define-success-publish-performance-data)
  requires metrics that show whether a service solves its intended problem and combines performance
  data with user research. This is authoritative public-service practice, not proof that any chosen
  metric captures value.
- [Productboard's PRD overview](https://www.productboard.com/glossary/product-requirements-document/)
  is vendor/practitioner support for concise outcome, user, scope, success, assumption, risk,
  constraint, and dependency sections; it specifically favors user-value measures and warns that
  volatile release tracking may belong elsewhere. The package does not adopt its product tooling.
- [NASA SWE-055: Requirements Validation](https://swehb.nasa.gov/spaces/7150/pages/16449673/SWE-055%2B-%2BRequirements%2BValidation)
  distinguishes validation of the right product from verification that it was built correctly,
  recommends objective techniques such as prototypes and demonstrations, and calls for stakeholder
  reconfirmation after conflicting or infeasible requirements are resolved. Its safety- and mission-
  oriented rigor must be proportional to product risk.
- [GOV.UK Government Functional Standard GovS 005: Digital](https://www.gov.uk/government/publications/government-functional-standard-govs-005-digital/government-functional-standard-govs-005-digital-html)
  likewise distinguishes verification against specification from validation against business need
  and describes traceability from user need through requirements. This supports separate delivery
  and outcome evidence.

## Lifecycle, change, and empirical limits

- [SEBoK: Requirements Management](https://sebokwiki.org/wiki/Requirements_Management), maintained
  by named INCOSE contributors, covers ownership, source and rationale, baselines, changes, impact,
  unknowns, status, and traceability to verification and validation across the lifecycle. It also
  says the management approach should fit project scale and complexity; the package therefore avoids
  mandatory code-line trace matrices.
- [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html), confirmed in 2024, establishes
  requirements engineering as lifecycle processes and information items rather than a one-time
  document. Detailed clauses are paywalled, so this package relies on it only for that high-level
  contract and uses open guidance for specific rules.
- Mund, Femmer, Fernández, and Eckhardt (2017),
  [Does Quality of Requirements Specifications Matter?](https://arxiv.org/pdf/1702.07656), combined
  a survey with 46 completions at one German multinational and an experiment with 41 student
  participants. It found context-dependent views of needed detail and showed selected semantic
  defects propagating into test work. Non-random sampling, one organization, selected defects, and
  a student-heavy experiment limit generalization; it supports tailored review and warns against
  equating document length with quality.
- Montgomery, Fucci, Bouraffa, Scholz, and Maalej (2022),
  [Empirical research on requirements quality](https://doi.org/10.1007/s00766-021-00367-z), is a
  systematic mapping study that filtered 6,905 records from six databases to 105 primary studies and
  found ambiguity, completeness, consistency, and correctness prominent but defined through many
  sub-attributes. It supports targeted quality checks, not a claim that one checklist predicts
  product success.

## Good/bad pair provenance

- Feature-versus-need, current-versus-requested behavior, and problem/outcome/solution pairs apply
  GOV.UK user-needs guidance, Cagan's practitioner warning, and Atlassian's PRD boundary.
- Vague, compound, quality, and acceptance pairs apply NASA and INCOSE requirement characteristics,
  narrowed by the empirical studies' context-dependent findings.
- Code-link, passing-suite, shipped-output, and post-launch mismatch pairs apply NASA verification
  and validation guidance, the DfE outcome principle, and SEBoK lifecycle management.
- The shifting-term pair (`party` against the domain's own `buyer`) applies Evans' Ubiquitous
  Language and the 6.9% naming-divergence finding, with INCOSE's unambiguous and consistent
  characteristics as the requirement-level frame.
- All angle-bracket examples are explicitly drafting templates, not generated customer facts.

## Deliberate exclusions

- No universal PRD template, mandatory page count, or one-page limit.
- No claim that stakeholder requests are automatically user needs—or that stakeholder direction is
  never authoritative.
- No frozen sign-off model; approved requirements may change through an explicit product decision.
- No claim that a PRD, passing test suite, shipped feature, adoption count, or code link proves user
  value.
- No mandatory exhaustive quality checklist or trace from every requirement to every code line.
- No invented percentage of product failures attributed to poor requirements.
