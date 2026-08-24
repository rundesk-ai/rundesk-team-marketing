<h1 align="center">
  <img src="assets/readme/rundesk-team-marketing-banner.png" alt="Rundesk Marketing Team — Beacon, Scout, Signal, and Quill." width="100%">
</h1>

<p align="center">
  <a href="https://github.com/rundesk-ai/rundesk-team-marketing/actions/workflows/build.yml?query=branch%3Amain"><img src="https://github.com/rundesk-ai/rundesk-team-marketing/actions/workflows/build.yml/badge.svg?branch=main" alt="Build and tests"></a>
  <a href="manifest.json"><img src="https://img.shields.io/badge/catalog-v0.1.0-blue?style=flat-square" alt="Catalog version 0.1.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/rundesk-ai/rundesk-team-marketing?style=flat-square" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#-team"><strong>👥 Team</strong></a>
  &nbsp;·&nbsp;
  <a href="#-skills"><strong>🧠 Skills</strong></a>
  &nbsp;·&nbsp;
  <a href="#-install"><strong>🚀 Install</strong></a>
  &nbsp;·&nbsp;
  <a href="#-development"><strong>🛠️ Development</strong></a>
</p>

A versioned Rundesk marketing team: four specialists, their canonical instructions, and the
research, growth, analytics, and service skills they use. This repository is both an installable
skill catalog and a team declaration for the [Rundesk CLI](https://github.com/rundesk-ai/rundesk-cli).

## 👥 Team

| Member | Responsibility |
|---|---|
| `beacon` | Maps SEO, AI-search, content, acquisition, and competitor-site opportunities. |
| `scout` | Researches markets, customers, competitors, products, and general topics. |
| `signal` | Analyzes first-party product and marketing data and forecasts. |
| `quill` | Produces messaging and content from an approved brief and evidence base. |

Each member is an inbound-only specialist. The requesting agent chooses the specialist, retains the
overall outcome, and integrates the returned evidence or artifact.

Quill intentionally starts with no packaged skills in v0.1.0. Its focused instructions provide the
initial messaging boundary while dedicated content-production skills are developed.

## 🧠 Skills

### Growth and acquisition

- `conversion-landing-pages` — Plan and evaluate measurable campaign landing pages and experiments.
- `lead-compliance-gates` — Identify consent, suppression, privacy, and vertical-specific gates before lead traffic goes live.
- `seo` — Audit and plan technical SEO, on-page content, structured data, AI-search visibility, and measurement.

### External research

- `researching-topics` — Plan, source, evaluate, synthesize, and cite reproducible research.

### First-party analytics

- `analyzing-growth-data` — Define and analyze funnels, cohorts, retention, attribution, experiments, segments, and forecasts.
- `google-analytics` — Read bounded GA4 acquisition, audience, event, ecommerce, historical, and realtime reports.
- `posthog` — Read bounded PostHog events, persons, trends, insights, recordings, web analytics, and HogQL results.

### Search evidence and access

- `google-auth` — Connect and inspect the Google accounts used by this catalog's Google integrations.
- `google-pagespeed-insights` — Retrieve bounded Lighthouse and field evidence for public webpages.
- `google-search-console` — Retrieve organic search performance, index inspection, and sitemap evidence.

`google-auth` is shipped as the provider declaration that makes the Google integration packages
self-contained; it is not granted to a member by default.

## 🚀 Install

Preview first, then confirm.

### Complete team

Install all skills and four managed agents:

```sh
rundesk teams install https://github.com/rundesk-ai/rundesk-team-marketing --provider <provider>
rundesk teams install https://github.com/rundesk-ai/rundesk-team-marketing --provider <provider> --confirm
```

Team installation creates the agents with their gateways stopped. Start only the agents you want:

```sh
rundesk gateways start <agent>
```

Update the team later with:

```sh
rundesk teams update rundesk-team-marketing --confirm
```

### Skills only

Install the catalog without creating agents:

```sh
rundesk skills install https://github.com/rundesk-ai/rundesk-team-marketing
rundesk skills install https://github.com/rundesk-ai/rundesk-team-marketing --confirm
```

This installs only the skills. You can add the complete team later without reinstalling them.

## ✅ Requirements

- A Rundesk CLI release that supports team catalogs.
- Public GitHub access to this repository.
- For complete-team installation: a provider and unused local names for all four members.
- A configured PostHog profile for live PostHog reads.
- A connected Google account and permitted GA4 or Search Console resources for Google reads.
- A PageSpeed Insights API key for PageSpeed reads.

This catalog carries its own Google OAuth provider declaration. Do not install it alongside another
catalog that declares the same `google` provider; Rundesk refuses ambiguous provider ownership.
Read each integration package's `references/cli.md` before configuring access.

## 🛠️ Development

Read [AGENTS.md](AGENTS.md), then run the offline gate:

```sh
python3 -m unittest discover -s tests -v
python3 skills/posthog/scripts/posthog.d/test-posthog.py -q
python3 skills/google-auth/scripts/google-auth.d/test-google-auth.py -q
python3 skills/google-analytics/scripts/google-analytics.d/test-google-analytics.py -q
python3 skills/google-pagespeed-insights/scripts/google-pagespeed-insights.d/test-google-pagespeed-insights.py -q
python3 skills/google-search-console/scripts/google-search-console.d/test-google-search-console.py -q
git diff --check
```

See [team validation](docs/team-validation.md) for the lifecycle and member-behavior contract.

## 🤝 Contributing

Use the repository templates:

- [Report a bug](.github/ISSUE_TEMPLATE/bug-report.md)
- [Propose a change](.github/ISSUE_TEMPLATE/change-proposal.md)
- [Prepare a pull request](.github/pull_request_template.md)

Keep the README, manifest, tests, team declaration, member instructions, package tree, and
[third-party notices](THIRD_PARTY_NOTICES.md) aligned.

## 📄 License

MIT. Adapted package provenance is recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
