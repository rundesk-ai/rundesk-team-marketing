"""The marketing team catalog is complete, self-contained, and safely bounded."""

import json
import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MEMBERS = {"beacon", "quill", "scout", "signal"}
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
        "conversion-landing-pages",
        "google-pagespeed-insights",
        "google-search-console",
        "lead-compliance-gates",
        "seo",
    },
    "quill": set(),
    "scout": {"researching-topics"},
    "signal": {"analyzing-growth-data", "google-analytics", "posthog"},
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

    def test_manifest_and_banner_define_v_0_1_0(self):
        self.assertEqual({"schema", "name", "version", "description"}, set(self.manifest))
        self.assertEqual(1, self.manifest["schema"])
        self.assertEqual("rundesk-team-marketing", self.manifest["name"])
        self.assertEqual("0.1.0", self.manifest["version"])
        self.assertTrue((ROOT / "assets/readme/rundesk-team-marketing-banner.png").is_file())

    def test_readme_lists_exactly_the_discovered_skills(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        listed = set(re.findall(r"(?m)^- `([a-z0-9-]+)` —", readme))
        self.assertEqual(self.skill_names(), listed)
        self.assertEqual(README_HEADINGS, tuple(re.findall(r"^## .+$", readme, re.MULTILINE)))
        self.assertIn("assets/readme/rundesk-team-marketing-banner.png", readme)
        self.assertIn("catalog-v0.1.0-blue", readme)
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

    def test_google_provider_is_declared_once_and_not_granted(self):
        declarations = list((ROOT / "skills").glob("*/oauth-provider.json"))
        self.assertEqual([ROOT / "skills/google-auth/oauth-provider.json"], declarations)
        provider = json.loads(declarations[0].read_text(encoding="utf-8"))
        self.assertEqual("google", provider["provider"])
        grants = {skill for member in self.team["members"] for skill in member["skills"]}
        self.assertNotIn("google-auth", grants)

    def test_team_declaration_has_exact_members_and_grants(self):
        self.assertEqual({"schema", "name", "members"}, set(self.team))
        self.assertEqual(1, self.team["schema"])
        self.assertEqual(self.manifest["name"], self.team["name"])
        names = [member["name"] for member in self.team["members"]]
        self.assertEqual(sorted(names), names)
        self.assertEqual(MEMBERS, set(names))
        skills = self.skill_names()
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
                self.assertLessEqual(set(member["skills"]), skills)
                self.assertFalse(set(member["skills"]) & PRODUCT_OWNED)
                self.assertEqual([], member["delegates_to"])
                self.assertIs(False, member["self_improve"])
                self.assertEqual(f"agents/{name}/AGENTS.md", member["instructions"])

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
            "9e5b911230844ffb9243ae2580c0987f2cd4b6ff",
            "5d419423122d8fa31115eeba516274160d37f7b8",
        ):
            self.assertIn(commit, notices)
        self.assertGreaterEqual(notices.count("MIT License"), 3)
        for name in self.skill_names():
            self.assertIn(f"`{name}`", notices)

    def test_workflows_pin_actions_and_run_the_repository_gate(self):
        for name in ("build.yml", "release.yml"):
            workflow = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
            with self.subTest(workflow=name):
                self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40}")
                self.assertRegex(workflow, r"actions/setup-python@[0-9a-f]{40}")
                self.assertIn("python -m unittest discover -s tests -v", workflow)
                for package in (
                    "posthog",
                    "google-auth",
                    "google-analytics",
                    "google-pagespeed-insights",
                    "google-search-console",
                ):
                    self.assertIn(f"test-{package}.py -q", workflow)
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
