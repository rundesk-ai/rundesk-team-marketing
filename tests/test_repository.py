"""The marketing team catalog owns its specialist guidance and declares only integrations."""

import json
import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MEMBERS = {"beacon", "quill", "scout"}
# A shared package must not assume this team's topology, so no member name may appear in
# `skills/seo`, in any case, nor either agent name a prior draft leaked from one installation.
TOPOLOGY = re.compile(r"\b(?:beacon|quill|scout|milo|magenta)\b")
PRODUCT_OWNED = {"managing-rundesk", "delegating-work", "managing-github"}
MEMBER_HEADINGS = ("## Before you act", "## Routing", "## Scope", "## Return")
README_HEADINGS = (
    "## 👥 Team",
    "## 🧠 Skills",
    "## 🚀 Install",
    "## ✅ Requirements",
    "## 🛠️ Development",
    "## 🤝 Contributing",
    "## 📄 License",
)
AGENT_HEADINGS = (
    "# AGENTS",
    "## Purpose",
    "## Before you work",
    "## Repository layout",
    "## Package and artifact contract",
    "## Safety and approval gates",
    "## Delegation",
    "## Architecture and conventions",
    "## Documentation duties",
    "## Build, test, and run",
    "## Pull requests and releases",
    "## Definition of done",
)
EXPECTED_GRANTS = {
    "beacon": {
        "rundesk-skills-google/google-analytics",
        "rundesk-skills-google/google-crux",
        "rundesk-skills-google/google-merchant",
        "rundesk-skills-google/google-pagespeed-insights",
        "rundesk-skills-google/google-search-console",
        "rundesk-skills-integrations/posthog",
        "rundesk-skills-integrations/stripe",
        "rundesk-team-marketing/analyzing-growth-data",
        "rundesk-team-marketing/lead-compliance-gates",
        "rundesk-team-marketing/seo",
        "rundesk-team-marketing/verifying-datasets",
    },
    "quill": {
        "rundesk-team-marketing/writing-advertising-copy",
        "rundesk-team-marketing/writing-editorial-content",
        "rundesk-team-marketing/writing-prds",
        "rundesk-team-marketing/writing-social-content",
    },
    "scout": {
        "rundesk-team-marketing/researching-competitors",
        "rundesk-team-marketing/researching-customers",
        "rundesk-team-marketing/researching-markets",
        "rundesk-team-marketing/researching-topics",
    },
}
EXPECTED_CATALOGS = {
    "rundesk-skills-google": "https://github.com/rundesk-ai/rundesk-skills-google",
    "rundesk-skills-integrations": "https://github.com/rundesk-ai/rundesk-skills-integrations",
}


def markdown_without_code(text):
    text = re.sub(r"(?ms)^```.*?^```", "", text)
    return re.sub(r"`[^`\n]*`", "code", text)


class RepositoryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.team = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))

    def skill_names(self):
        return {
            path.name
            for path in (ROOT / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }

    def members(self):
        return {member["name"]: member for member in self.team["members"]}

    def test_manifest_and_banner_define_v_2_1_0(self):
        self.assertEqual({"schema", "name", "version", "description"}, set(self.manifest))
        self.assertEqual(1, self.manifest["schema"])
        self.assertEqual("rundesk-team-marketing", self.manifest["name"])
        self.assertEqual("2.1.0", self.manifest["version"])
        self.assertTrue((ROOT / "assets/readme/rundesk-team-marketing-banner-v2.png").is_file())

    def test_readme_lists_the_exact_team_capabilities(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        listed = set(re.findall(r"(?m)^- `([a-z0-9-]+)` —", readme))
        granted = {address.rsplit("/", 1)[1] for skills in EXPECTED_GRANTS.values()
                   for address in skills}
        self.assertEqual(granted | {"google-auth", "managing-marketing-work"}, listed)
        self.assertEqual(README_HEADINGS, tuple(re.findall(r"^## .+$", readme, re.MULTILINE)))
        self.assertIn("assets/readme/rundesk-team-marketing-banner-v2.png", readme)
        self.assertIn('<h1 align="center">Rundesk Marketing Team</h1>', readme)
        self.assertIn('<p align="center">\n  <a href="https://github.com/rundesk-ai/', readme)
        for anchor in ("#-team", "#-skills", "#-install", "#️-development"):
            self.assertIn(f'href="{anchor}"', readme)
        self.assertIn("A versioned Rundesk team for research, growth, analytics,", readme)
        title = '<h1 align="center">Rundesk Marketing Team</h1>'
        banner = "assets/readme/rundesk-team-marketing-banner-v2.png"
        self.assertTrue(readme.startswith('<p align="center">\n  <img src="' + banner))
        self.assertLess(
            readme.index(banner),
            readme.index(title),
        )
        self.assertLess(
            readme.index(title),
            readme.index("A versioned Rundesk team for research, growth, analytics,"),
        )
        self.assertLess(
            readme.index("A versioned Rundesk team for research, growth, analytics,"),
            readme.index("## 👥 Team"),
        )
        self.assertIn("catalog-v2.1.0-blue", readme)
        self.assertLess(readme.index("### Complete team"), readme.index("### Skills only"))
        self.assertIn("gateways stopped", readme)

    def test_every_skill_has_valid_frontmatter_and_a_self_contained_package(self):
        for name in self.skill_names():
            with self.subTest(skill=name):
                self.assertRegex(name, NAME)
                self.assertNotIn(name, PRODUCT_OWNED)
                package = ROOT / "skills" / name
                page = (package / "SKILL.md").read_text(encoding="utf-8")
                parts = page.split("---", 2)
                self.assertEqual(3, len(parts))
                fields = [line for line in parts[1].strip().splitlines() if line.strip()]
                self.assertEqual(["name", "description"], [line.partition(":")[0] for line in fields])
                self.assertEqual(f"name: {name}", fields[0])
                self.assertTrue(fields[1].partition(":")[2].strip())
                self.assertLessEqual(len(fields[1]), 1024)
                self.assertLessEqual(len(page.splitlines()), 500)
                for path in package.rglob("*"):
                    self.assertNotIn("..", path.relative_to(package).parts)
                for script in (package / "scripts").glob("*") if (package / "scripts").is_dir() else ():
                    if script.is_file() and "." not in script.name:
                        self.assertTrue(os.access(script, os.X_OK), f"{script} must be executable")

    def test_google_provider_stays_in_its_shared_catalog_and_is_not_granted(self):
        declarations = list((ROOT / "skills").glob("*/oauth-provider.json"))
        self.assertEqual([], declarations)
        grants = {skill for member in self.team["members"] for skill in member["skills"]}
        self.assertFalse(any(skill.endswith("/google-auth") for skill in grants))

    def test_caller_orchestration_is_installed_and_not_member_granted(self):
        self.assertIn("managing-marketing-work", self.skill_names())
        grants = {skill for member in self.team["members"] for skill in member["skills"]}
        self.assertNotIn("managing-marketing-work", grants)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "rundesk-team-marketing/managing-marketing-work",
            readme,
        )

    def test_marketing_review_briefs_require_artifact_role_fit(self):
        orchestration = " ".join((
            ROOT / "skills/managing-marketing-work/SKILL.md"
        ).read_text(encoding="utf-8").split())
        for phrase in (
            "Choose role fit before writing an independent-review brief",
            "reviewer must own judgment of the finished artifact type",
            "completed-code-change reviewer does not become a marketing",
            "reviewer must not have produced the artifact",
            "producer is the only artifact-qualified reviewer",
            "only after the exact artifact is finished and inspectable",
            "report that routing gap",
            "exact artifact and version",
            "few change-specific highest-risk invariants",
            "Omit the reviewer's generic role and checklist",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, orchestration)

    def test_interface_design_remains_outside_the_marketing_team(self):
        self.assertNotIn("conversion-landing-pages", self.skill_names())
        grants = {skill for member in self.team["members"] for skill in member["skills"]}
        self.assertFalse(any("landing-pages" in skill for skill in grants))
        orchestration = (
            ROOT / "skills/managing-marketing-work/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Do not use for software or interface design", orchestration)

    def test_technical_documentation_remains_outside_the_marketing_team(self):
        self.assertNotIn("writing-technical-docs", self.skill_names())
        quill = self.members()["quill"]
        self.assertFalse(any("technical-doc" in skill for skill in quill["skills"]))
        self.assertNotIn(
            "technical documentation",
            (ROOT / "agents/quill/AGENTS.md").read_text(encoding="utf-8").lower(),
        )

    def test_quill_owns_evidence_based_editorial_writing(self):
        quill = (ROOT / "agents/quill/AGENTS.md").read_text(encoding="utf-8")
        skill = (ROOT / "skills/writing-editorial-content/SKILL.md").read_text(encoding="utf-8")
        forms = (
            ROOT / "skills/writing-editorial-content/references/forms-and-structure.md"
        ).read_text(encoding="utf-8")
        editing = (
            ROOT / "skills/writing-editorial-content/references/editing-and-language.md"
        ).read_text(encoding="utf-8")

        self.assertIn("blogs, development logs, articles, columns, stories", quill)
        self.assertIn("Do not write it into a repository", quill)
        self.assertIn("Audience and reading situation:", skill)
        self.assertIn("Author voice, product voice, tone, and English variant:", skill)
        self.assertIn("Do not fabricate", skill)
        self.assertIn("Use separate passes", skill)
        self.assertIn("Drafting authority is not placement", skill)
        self.assertIn("## Development log", forms)
        self.assertIn("## Column or essay", forms)
        self.assertIn("Never invent dialogue", forms)
        self.assertIn("There is no universal best word count", editing)

    def test_quill_owns_platform_true_social_copy_without_posting(self):
        quill = (ROOT / "agents/quill/AGENTS.md").read_text(encoding="utf-8")
        skill = (ROOT / "skills/writing-social-content/SKILL.md").read_text(encoding="utf-8")
        platforms = (
            ROOT / "skills/writing-social-content/references/platform-forms.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Instagram captions and carousel or", quill)
        self.assertIn("Writing a `post` means drafting its content", quill)
        self.assertIn("Platform, surface, and organic/paid status:", skill)
        self.assertIn("never invent what an unseen", skill)
        self.assertIn("do not merely truncate", skill)
        self.assertIn("do not post, schedule, upload, or engage", skill)
        self.assertIn("## Instagram", platforms)
        self.assertIn("## Pinterest", platforms)
        self.assertIn("Do not hard-code universal", platforms)

    def test_quill_owns_voice_true_keyword_aware_ad_copy_without_campaigns(self):
        quill = (ROOT / "agents/quill/AGENTS.md").read_text(encoding="utf-8")
        skill = (ROOT / "skills/writing-advertising-copy/SKILL.md").read_text(encoding="utf-8")
        keywords = (
            ROOT / "skills/writing-advertising-copy/references/keywords-and-message-match.md"
        ).read_text(encoding="utf-8")
        forms = (
            ROOT / "skills/writing-advertising-copy/references/ad-forms.md"
        ).read_text(encoding="utf-8")

        self.assertIn("search-ad assets, paid social and sponsored copy", quill)
        self.assertIn("Advertiser, product, service, or offer being promoted:", skill)
        self.assertIn("preserve voice", skill.lower())
        self.assertIn("Use keywords to express message match", skill)
        self.assertIn("do not operate or publish the campaign", skill)
        self.assertIn("query intent -> headline recognition", keywords)
        self.assertIn("## Responsive search ads", forms)
        self.assertIn("## Paid social", forms)

    def test_team_declaration_has_exact_members_and_grants(self):
        self.assertEqual({"schema", "name", "catalogs", "members"}, set(self.team))
        self.assertEqual(2, self.team["schema"])
        self.assertEqual(self.manifest["name"], self.team["name"])
        self.assertEqual(EXPECTED_CATALOGS,
                         {one["name"]: one["source"] for one in self.team["catalogs"]})
        names = [member["name"] for member in self.team["members"]]
        self.assertEqual(sorted(names), names)
        self.assertEqual(MEMBERS, set(names))
        local = self.skill_names()
        for name, member in self.members().items():
            with self.subTest(member=name):
                self.assertEqual(
                    {"name", "description", "instructions", "skills", "delegates_to", "self_improve"},
                    set(member),
                )
                self.assertLessEqual(len(member["description"]), 200)
                self.assertEqual(member["description"], member["description"].strip())
                self.assertTrue(member["description"].endswith("."))
                self.assertEqual(sorted(member["skills"]), member["skills"])
                self.assertEqual(EXPECTED_GRANTS[name], set(member["skills"]))
                self.assertTrue(all(skill.count("/") == 1 for skill in member["skills"]))
                self.assertFalse({skill.rsplit("/", 1)[1] for skill in member["skills"]}
                                 & PRODUCT_OWNED)
                for catalog, package in (skill.split("/") for skill in member["skills"]):
                    if catalog == self.team["name"]:
                        self.assertIn(package, local)
                    else:
                        self.assertIn(catalog, EXPECTED_CATALOGS)
                self.assertEqual([], member["delegates_to"])
                self.assertIs(False, member["self_improve"])
                self.assertEqual(f"agents/{name}/AGENTS.md", member["instructions"])

    def test_member_routing_descriptions_and_beacon_measurement_contract(self):
        self.assertNotIn("signal", self.members())
        beacon = self.members()["beacon"]
        for skill in (
            "rundesk-skills-integrations/posthog",
            "rundesk-skills-integrations/stripe",
            "rundesk-team-marketing/verifying-datasets",
        ):
            self.assertIn(skill, beacon["skills"])

        beacon_instructions = " ".join((
            ROOT / "agents/beacon/AGENTS.md"
        ).read_text(encoding="utf-8").split())
        self.assertIn("measurement contract", beacon_instructions)
        self.assertIn("file provenance", beacon_instructions)
        self.assertIn("physical inputs into the displayed formula", beacon_instructions)
        self.assertIn("percentage-point difference", beacon_instructions)
        self.assertIn("bounded script or query in a disposable workspace", beacon_instructions)
        self.assertIn("never bypass authentication, crawler rules, bot controls, or rate limits", beacon_instructions)
        self.assertIn("Stop without a yes/no answer, ranking, recommendation, verdict, or decision", beacon_instructions)

        analysis = (
            ROOT / "skills/analyzing-growth-data/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Expose every calculation", analysis)
        self.assertIn("numerator / denominator × 100 = rate", analysis)
        self.assertIn("percentage-point change", analysis)
        self.assertIn("A zero prior value makes relative change undefined", analysis)
        self.assertIn("Substitute the physical values", analysis)
        self.assertIn("Do not inspect or reconcile an adjacent", analysis)
        self.assertIn("Do not calculate an interval", analysis)
        self.assertIn("compare it with the unrounded calculated value", analysis)
        self.assertIn("inspection command is not the analytics source", analysis)
        self.assertIn("source-trail status complete or incomplete", analysis)
        self.assertIn("do not tell the requester what they should conclude", analysis)
        self.assertIn("Stop before ranking options", analysis)

        verification = (
            ROOT / "skills/verifying-datasets/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Process reproducibly", verification)
        self.assertIn("input name and checksum", verification)
        self.assertIn("counts before and after every", verification)
        self.assertIn("A local command proves how the supplied file was processed", verification)

        description = beacon["description"]
        for trigger in (
            "first-party analytics",
            "supplied datasets",
            "organic/search measurement",
            "funnels",
            "conversion",
            "retention",
            "attribution",
            "experiments",
            "CSVs",
            "spreadsheets",
        ):
            self.assertIn(trigger, description)
        for reserved in ("never ranks", "recommends", "decides"):
            self.assertIn(reserved, description)
        self.assertLessEqual(len(description), 200)

        scout_description = self.members()["scout"]["description"]
        for trigger in (
            "markets",
            "customers",
            "competitor businesses",
            "products",
            "topics",
            "published sources",
            "cited findings",
        ):
            self.assertIn(trigger, scout_description)
        for boundary in ("analytics", "content", "rankings", "decisions"):
            self.assertIn(boundary, scout_description)
        self.assertLessEqual(len(scout_description), 200)

        quill_description = self.members()["quill"]["description"]
        for trigger in (
            "PRDs",
            "messaging",
            "blogs",
            "articles",
            "organic social posts",
            "paid advertising copy",
            "approved direction and evidence",
        ):
            self.assertIn(trigger, quill_description)
        for boundary in ("never publishes", "operates campaigns"):
            self.assertIn(boundary, quill_description)
        self.assertLessEqual(len(quill_description), 200)

        scout_instructions = (ROOT / "agents/scout/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("never go looking for a codebase", scout_instructions)
        self.assertIn("Do not write it into a repository", scout_instructions)

        beacon_instructions = " ".join((
            ROOT / "agents/beacon/AGENTS.md"
        ).read_text(encoding="utf-8").split())
        for phrase in (
            "dated SEO baselines across impressions, clicks, organic landing behavior, leads or sales",
            "available lead dispositions",
            "traffic quality is established or blocked by missing outcomes",
            "The requester ranks options, makes verdicts, and decides what to do",
        ):
            self.assertIn(phrase, beacon_instructions)

    def test_seo_lifecycle_separates_evidence_decision_and_verification(self):
        lifecycle = (
            ROOT / "skills/managing-marketing-work/references/seo-lifecycle.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(lifecycle.split())
        for heading in (
            "## 1. Frame the decision",
            "## 2. Establish traceable evidence",
            "## 3. Rank and recommend",
            "## 4. Record the owner decision",
            "## 5. Brief and implement",
            "## 6. Independently verify",
            "## 7. Observe and read out",
            "## 8. Operate the cadence",
        ):
            self.assertIn(heading, lifecycle)
        for boundary in (
            "## Ownership",
            "The `seo` skill owns the method",
            "The domain caller owns planning",
            "Beacon owns evidence",
            "`managing-marketing-work` owns orchestration",
            "A shared method does not merge these roles",
            "A user-agent string alone does not prove crawler identity",
            "Do not relabel ordinary Bing search metrics as citation evidence",
            "Search Console absence is not zero demand",
            "measurement repair is the first planned outcome",
            "measurement readiness and baseline, technical quality and red-flag resolution, growth planning, then content expansion",
            "Beacon independently verifies",
            "must label that focus pending",
        ):
            self.assertIn(boundary, normalized)

    def test_seo_planning_is_domain_owned_and_decision_ready(self):
        planning = " ".join((
            ROOT / "skills/seo/references/planning.md"
        ).read_text(encoding="utf-8").split())
        orchestration = " ".join((
            ROOT / "skills/managing-marketing-work/SKILL.md"
        ).read_text(encoding="utf-8").split())
        for phrase in (
            "The domain owner applies this method and retains the decision",
            "Do not retrieve missing specialist evidence while ranking",
            "Foundational defects",
            "Evidence-supported enhancements",
            "Coverage expansion",
            "### 1. Measurement readiness and baseline",
            "### 2. Technical quality and red-flag resolution",
            "### 3. Growth plan",
            "### 4. Content expansion",
            "SEO quality scorecard",
            "qualified-lead rate",
            "disposition completeness",
            "the first planned outcome is to repair that measurement path",
            "A new red flag found in any later phase returns the program to this gate",
            "Do not advance a phase merely because its report exists",
            "Do not split one change into separate planning, implementation, verification, and readout outcomes",
            "If the evidence supports fewer outcomes than the requested count",
            "Do not multiply invented numeric scores",
            "Decision state: Pending owner decision",
            "the evidence specialist — not the domain owner and not the implementer —",
            "independently verifies the affected production surface",
        ):
            self.assertIn(phrase, planning)
        shared = sorted((ROOT / "skills/seo").rglob("*.md"))
        self.assertGreaterEqual(len(shared), 13)
        for path in shared:
            named = TOPOLOGY.findall(path.read_text(encoding="utf-8").lower())
            self.assertEqual(
                [],
                named,
                f"{path.relative_to(ROOT)} names team topology: {sorted(set(named))}",
            )
        for phrase in (
            "Domain-owned planning",
            "caller owns the domain decision",
            "does not transfer evidence retrieval",
            "keeps the recommendation visibly pending",
        ):
            self.assertIn(phrase, orchestration)

    def test_seo_measurement_covers_search_business_and_disposition_baselines(self):
        measurement = " ".join((
            ROOT / "skills/seo/references/measurement.md"
        ).read_text(encoding="utf-8").split())
        sources = " ".join((
            ROOT / "skills/seo/references/sources.md"
        ).read_text(encoding="utf-8").split())
        for phrase in (
            "Search Console records what happened before arrival",
            "Analytics records onsite behavior after arrival",
            "CRM or commerce system establishes whether a lead qualified",
            "working_lead",
            "qualify_lead",
            "disqualify_lead",
            "close_convert_lead",
            "close_unconvert_lead",
            "missing disposition data means traffic quality is unestablished",
        ):
            self.assertIn(phrase, measurement)
        for phrase in (
            "The four-gate order in `planning.md` is this catalog's operational synthesis",
            "The SEO quality scorecard deliberately has no combined numeric grade",
        ):
            self.assertIn(phrase, sources)

    def test_member_instructions_are_bounded_and_role_specific(self):
        declared = {member["instructions"] for member in self.team["members"]}
        found = {str(path.relative_to(ROOT)) for path in (ROOT / "agents").glob("*/AGENTS.md")}
        self.assertEqual(declared, found)
        for name in MEMBERS:
            page = ROOT / "agents" / name / "AGENTS.md"
            text = page.read_text(encoding="utf-8")
            with self.subTest(member=name):
                headings = tuple(re.findall(r"^#{1,2} .+$", text, re.MULTILINE))
                self.assertEqual((f"# {name.title()}",) + MEMBER_HEADINGS, headings)
                self.assertLessEqual(len(text.splitlines()), 50)
                self.assertIn("subagent", text.lower())
                self.assertEqual(0, page.stat().st_mode & 0o111)
                for skill in self.skill_names():
                    self.assertNotIn(skill, text)

    def test_repository_guides_are_identical_and_ordered(self):
        agents = (ROOT / "AGENTS.md").read_bytes()
        self.assertEqual(agents, (ROOT / "CLAUDE.md").read_bytes())
        self.assertEqual(
            AGENT_HEADINGS,
            tuple(re.findall(r"^#{1,2} .+$", agents.decode("utf-8"), re.MULTILINE)),
        )

    def test_markdown_local_links_resolve(self):
        for page in ROOT.rglob("*.md"):
            if ".git" in page.parts:
                continue
            text = markdown_without_code(page.read_text(encoding="utf-8"))
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = target.split("#", 1)[0]
                with self.subTest(page=page.relative_to(ROOT), target=target):
                    self.assertTrue((page.parent / path).resolve().exists())

    def test_provenance_names_every_source_commit_and_license(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        for commit in (
            "826953197c01c7816fdd480e1eb91ee4fe708a8b",
            "4e3908ab733b9f09525d8674c01daead8de7f83d",
        ):
            self.assertIn(commit, notices)
        self.assertGreaterEqual(notices.count("MIT License"), 2)
        for name in self.skill_names():
            self.assertIn(f"`{name}`", notices)

    def test_workflows_pin_actions_and_run_the_repository_gate(self):
        for name in ("build.yml", "release.yml"):
            workflow = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
            with self.subTest(workflow=name):
                self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40}")
                self.assertRegex(workflow, r"actions/setup-python@[0-9a-f]{40}")
                self.assertIn("python -m unittest discover -s tests -v", workflow)
                self.assertIn("git diff --check", workflow)

    def test_text_files_have_clean_endings(self):
        for path in ROOT.rglob("*"):
            if (
                not path.is_file()
                or ".git" in path.parts
                or "__pycache__" in path.parts
                or path.suffix == ".png"
            ):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(text.endswith("\n"))
                self.assertIsNone(re.search(r"[ \t]+$", text, re.MULTILINE))


if __name__ == "__main__":
    unittest.main()
