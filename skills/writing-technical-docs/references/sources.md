# Technical-documentation source map

Use this file to audit a lesson, not as more documentation procedure. The package synthesizes
standards, project guidance, practitioner frameworks, and empirical studies; it does not copy one
style guide or documentation template.

Verified 7 August 2026 against the linked pages.

## Documentation type and audience

- [Diátaxis: start here](https://diataxis.fr/start-here/) — practitioner framework for separating
  tutorials, task-oriented how-to guides, factual reference, and explanatory understanding. The
  package uses the reader-need distinctions without imposing Diátaxis as a directory layout.
- [OASIS DITA 1.3](https://www.oasis-open.org/standard/ditav1-3/) — standards basis for focused,
  reusable concept, task, and reference topics. This package adopts topic separation, not DITA's XML
  implementation.
- [The Good Docs Project templates](https://www.thegooddocsproject.dev/template), including its
  [how-to](https://www.thegooddocsproject.dev/template/how-to) and
  [troubleshooting](https://www.thegooddocsproject.dev/template/troubleshooting) guidance —
  community-maintained basis for prerequisites, imperative steps, expected results, and organizing
  recovery around a reader's observable symptom.

## Accuracy, proof, and lifecycle

- [Google documentation best practices](https://google.github.io/styleguide/docguide/best_practices.html)
  — source for keeping docs short and current, updating them with code, deleting known-wrong
  material, documenting arguments/returns/restrictions/errors, putting the simplest example first,
  and treating implemented design documents as historical decisions rather than half-current user
  docs. Google says documented behavior should often have a verifying test while separately warning
  that compilation and complete line coverage do not finish the human explanation; this supports the
  package's bounded-test rule.
- Eric Holscher and the Write the Docs community,
  [Docs as Code](https://www.writethedocs.org/guide/docs-as-code/) — practitioner basis for managing
  documentation with plain text, version control, issue tracking, code review, and automated tests
  in the product workflow.
- [Rust documentation tests](https://doc.rust-lang.org/rustdoc/documentation-tests.html) and Go's
  [executable examples](https://pkg.go.dev/testing#hdr-Examples) — two mature official ecosystems
  that compile or execute examples and can check expected output. The package generalizes only the
  practice of using a repository's native executable-documentation support when available.
- Tan, Wagner, and Treude (2024),
  [Detecting outdated code element references](https://link.springer.com/article/10.1007/s10664-023-10397-6)
  — repository-history study of 800 popular open-source projects and 1,907 Google projects that found
  deleted identifiers surviving in documentation. Its regular-expression method detects only some
  stale references and can flag cases where functionality survives in another representation. The
  package uses it as evidence of a drift mechanism, not a complete drift detector.

## Interfaces and examples

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) — standards basis for a
  language-neutral HTTP API description that both humans and computers can use. The package treats a
  maintained description as structural contract evidence, not a complete tutorial or explanation.
- UK Government Digital Service,
  [Writing API reference documentation](https://www.gov.uk/guidance/writing-api-reference-documentation)
  and [Documenting APIs](https://www.gov.uk/guidance/how-to-document-apis) — basis for documenting
  purpose, authentication, resources, endpoints, methods, parameter types and constraints, requests,
  exact responses, errors and their causes, limits, and tested examples. The guidance also warns
  that examples alone do not communicate whether fields are required or constrained.
- Google developer documentation guidance for
  [code samples](https://developers.google.com/style/code-samples) and
  [command-line syntax](https://developers.google.com/style/code-syntax) — basis for marking omitted
  code, distinguishing placeholders from literal input, and separating one runnable task example
  from exhaustive optional syntax.
- Uddin and Robillard (2015),
  [How API Documentation Fails](https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf) — two surveys
  totaling 323 IBM professionals: an exploratory survey of 69 respondents supplied 179 examples
  across 131 documentation units and 72 APIs; a validation survey included 254 developers and
  architects. Ambiguity, incompleteness, and incorrectness were rated among the most serious content
  problems. Limits include a corporate IBM population, self-report, a low first-survey response rate,
  and the 2015 ecosystem.
- Meng, Steinhardt, and Schubert (2019),
  [How Developers Use API Documentation](https://www.mangold-international.com/_Resources/Persistent/a/7/1/2/a712bdd99343412abc60642ea624ae047ef00b27/Meng_et_al_How-Developers-Use-API-Documentation_2019.pdf)
  — observation and eye tracking of 11 developers completing five tasks with one unfamiliar REST API
  during 70-minute sessions. Participants used concepts, examples, and reference differently. Its
  small sample, single API, and constrained tasks justify multiple entry paths only as a bounded
  design signal, not a universal reading model.

## Architecture and maintenance

- Simon Brown's [C4 introduction](https://c4model.com/introduction) and
  [diagram guidance](https://c4model.com/diagrams) — practitioner evidence for maps of an existing
  codebase at audience-appropriate abstraction levels and for the failures caused by ambiguous
  elements, unlabeled relationships, missing technology, unexplained abbreviations, and mixed
  abstraction. C4 explicitly says to use only diagram levels that add value.
- [C4 notation guidance](https://c4model.com/diagrams/notation) — basis for diagram title, type,
  scope, legend, explicit element types, and understandable abbreviations.
- arc42's guidance on
  [architecture-documentation drift](https://faq.arc42.org/questions/H-3/) — practitioner basis for
  documenting economically, favoring stable high-level structure and cross-cutting concepts over
  exhaustive volatile internals, and giving documentation an owner.
- UK Government Digital Service,
  [Documenting architecture decisions](https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html)
  — source for keeping rationale in an explicit decision record with context, decision, status, and
  consequences. It supports refusing to infer rationale from current code shape.

## Human and agent readability

- W3C Web Accessibility Initiative,
  [Writing for Web Accessibility](https://www.w3.org/WAI/tips/writing/) and
  [headings guidance](https://www.w3.org/WAI/tutorials/page-structure/headings/) — standards-based
  support for informative titles, semantic descriptive headings, meaningful links, clear
  instructions and errors, concise language, expanded abbreviations, and text alternatives.
- [Google accessible documentation guidance](https://developers.google.com/style/accessibility) —
  practitioner examples for scannable sections, short direct sentences, descriptive headings and
  links, numbered procedures, and not relying on visual-only cues.
- [GitLab documentation style guide](https://docs.gitlab.com/development/documentation/styleguide/)
  — maintained project evidence for one canonical source of product truth and concise, precise,
  searchable, scannable topic types. The canonical-source lesson underpins routing agents to the same
  docs rather than maintaining provider-specific copies.
- [GitLab's AI agent instruction files for documentation](https://docs.gitlab.com/development/documentation/ai-instruction-files-documentation/)
  — project-maintainer evidence that vague or unverifiable descriptions of feature behavior should
  not be placed in agent instructions. This package's provider-neutral conclusion is limited to
  keeping technical truth evidence-backed and canonical; it does not claim that LLMs need a special
  prose dialect.

## Good/bad pair provenance

- Retry-policy and rationale pairs apply Google's test-backed contract guidance and the GDS decision-
  record boundary to minimized placeholder examples.
- Runnable-command and API error pairs apply Google code-sample guidance and the GDS API contract.
- Diagram pairs apply C4's published failure catalog and notation checklist.
- Mixed-page and duplicated-agent-doc pairs apply Diátaxis, GitLab's single-source practice, and the
  bounded API-usage study. Angle-bracket content is explicitly a template, never a factual product
  claim.

## Deliberate exclusions

- `llms.txt` is a proposal, not a required standard or replacement for canonical accessible docs.
- Tests do not prove prose beyond the cases and boundaries they exercise.
- Generated reference does not establish purpose, rationale, usability, or completeness by itself.
- The implementation is not silently promoted over a conflicting versioned public contract; the
  discrepancy must remain visible.
- No rule requires documenting every directory, class, endpoint, or runtime path.
