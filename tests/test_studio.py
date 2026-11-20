"""Regression tests for the offline helpers, not end-to-end LLM evaluations."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/github-markdown-studio/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit = load("audit")
render = load("render_diagram")
capability_plan = load("capability_plan")


def make_test_symlink(link, target):
    try:
        link.symlink_to(target)
    except OSError as error:
        if getattr(error, "winerror", None) == 1314:
            raise unittest.SkipTest("Windows requires permission to create symlinks") from error
        raise


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)

    def put(self, path, content):
        output = self.root / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        return output

    def report(self, text, files=None):
        self.put("README.md", text)
        for path, content in (files or {}).items():
            self.put(path, content)
        return audit.Auditor(self.root).run(["README.md"])

    def codes(self, report):
        return {finding["code"] for finding in report["findings"]}

    def test_valid_relative_link(self):
        self.assertEqual(self.report("[Guide](docs/guide.md)", {"docs/guide.md": "# Guide"})["counts"]["error"], 0)

    def test_broken_relative_link(self):
        self.assertIn("BROKEN_LOCAL_LINK", self.codes(self.report("[Gone](missing.md)")))

    def test_reference_style_link(self):
        self.assertIn("BROKEN_LOCAL_LINK", self.codes(self.report("[Guide][g]\n\n[g]: missing.md")))

    def test_link_in_table(self):
        self.assertIn("BROKEN_LOCAL_LINK", self.codes(self.report("| A |\n|---|\n| [Link](missing.md) |")))

    def test_fenced_code_is_not_a_link(self):
        self.assertEqual(self.report("```md\n[Example](missing.md)\n<img src='bad'>\n```")["counts"]["error"], 0)

    def test_inline_code_is_not_a_link(self):
        self.assertEqual(self.report("`[Example](missing.md)`")["counts"]["error"], 0)

    def test_comments_are_not_active_html(self):
        self.assertEqual(self.report("<!-- <img src='missing'> -->")["counts"]["error"], 0)

    def test_image_alt_warning(self):
        self.assertIn("IMAGE_ALT", self.codes(self.report("![](image.svg)", {"image.svg": "<svg/>"})))

    def test_meaningful_alt(self):
        self.assertNotIn("IMAGE_ALT", self.codes(self.report("![A process](image.svg)", {"image.svg": "<svg/>"})))

    def test_html_decorative_image(self):
        self.assertNotIn("IMAGE_ALT", self.codes(self.report('<img src="image.svg" alt="" role="presentation">', {"image.svg": "<svg/>"})))

    def test_picture_missing_fallback(self):
        result = self.report('<picture>\n<source srcset="image.svg">\n</picture>', {"image.svg": "<svg/>"})
        self.assertIn("PICTURE_FALLBACK", self.codes(result))

    def test_picture_missing_theme(self):
        result = self.report('<picture><source media="(prefers-color-scheme: dark)" srcset="a.svg"><img alt="A" src="a.svg"></picture>', {"a.svg": "<svg/>"})
        self.assertIn("PICTURE_THEMES", self.codes(result))

    def test_picture_complete(self):
        result = self.report('<picture>\n<source media="(prefers-color-scheme: dark)" srcset="a.svg">\n<source media="(prefers-color-scheme: light)" srcset="b.svg">\n<img src="b.svg" alt="Steps">\n</picture>', {"a.svg": "<svg/>", "b.svg": "<svg/>"})
        self.assertEqual(result["counts"], {"error": 0, "warning": 0})

    def test_picture_unclosed(self):
        self.assertIn("PICTURE_UNCLOSED", self.codes(self.report("<picture>")))

    def test_script_flagged(self):
        self.assertIn("UNSAFE_HTML", self.codes(self.report("<script>alert(1)</script>")))

    def test_style_warning(self):
        self.assertIn("INLINE_STYLE", self.codes(self.report('<div style="color:red">Text</div>')))

    def test_event_handler_flagged(self):
        self.assertIn("EVENT_HANDLER", self.codes(self.report('<img src="a.svg" alt="A" onerror="x()">', {"a.svg": "<svg/>"})))

    def test_html_javascript_url(self):
        self.assertIn("UNSAFE_URL", self.codes(self.report('<a href="javascript:alert(1)">Bad</a>')))

    def test_heading_jump(self):
        self.assertIn("HEADING_JUMP", self.codes(self.report("# Heading\n\n### Skipped")))

    def test_unicode_anchor(self):
        self.assertNotIn("ANCHOR_REVIEW", self.codes(self.report("# เริ่มต้นใช้งาน\n\n[ไป](#เริ่มต้นใช้งาน)")))

    def test_duplicate_anchor(self):
        self.assertNotIn("ANCHOR_REVIEW", self.codes(self.report("# Hello\n\n## Hello\n\n[Go](#hello-1)")))

    def test_duplicate_slug_collision(self):
        self.assertNotIn("ANCHOR_REVIEW", self.codes(self.report("# X\n\n## X\n\n## X-1\n\n[Go](#x-1-1)")))

    def test_explicit_named_anchor(self):
        self.assertNotIn("ANCHOR_REVIEW", self.codes(self.report('<a name="stable"></a>\n\n[Go](#stable)')))

    def test_broken_anchor_warns_not_errors(self):
        report = self.report("# Present\n\n[Go](#absent)")
        self.assertIn("ANCHOR_REVIEW", self.codes(report))
        self.assertEqual(report["counts"]["error"], 0)

    def test_encoded_spaces(self):
        self.assertEqual(self.report("[A](a%20b.md)", {"a b.md": "# A"})["counts"]["error"], 0)

    def test_parent_traversal_rejected(self):
        self.assertIn("LINK_PATH", self.codes(self.report("[Outside](../outside.md)")))

    def test_encoded_traversal_rejected(self):
        self.assertIn("LINK_PATH", self.codes(self.report("[Outside](%2e%2e/outside.md)")))

    def test_null_byte_rejected(self):
        self.assertIn("LINK_PATH", self.codes(self.report("[Bad](a%00b.md)")))

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as external:
            target = Path(external) / "outside.md"
            target.write_text("# Private", encoding="utf-8")
            make_test_symlink(self.root / "linked.md", target)
            self.assertIn("LINK_PATH", self.codes(self.report("[Outside](linked.md)")))

    def test_external_links_not_fetched(self):
        report = self.report("[Web](https://example.com/) [Email](mailto:test@example.com)")
        self.assertEqual(report["external_references_skipped"], 2)
        self.assertEqual(report["verification"]["external_links"], "not-run")

    def test_yaml_safe_loader(self):
        report = self.report("---\na: !!python/object/apply:os.system ['echo unsafe']\n---\n# Test")
        self.assertIn("DOCUMENT_PARSE", self.codes(report))

    def test_skill_metadata(self):
        self.put("skills/example/SKILL.md", '---\nname: example\ndescription: A useful skill.\nmetadata:\n  version: "0.1"\n---\n# Example')
        self.assertEqual(audit.Auditor(self.root).run([])["counts"]["error"], 0)

    def test_skill_wrong_name(self):
        self.put("skills/example/SKILL.md", "---\nname: other\ndescription: Good.\n---\n# Example")
        self.assertIn("SKILL_METADATA", self.codes(audit.Auditor(self.root).run([])))

    def test_skill_missing_frontmatter(self):
        self.put("skills/example/SKILL.md", "# Example")
        self.assertIn("SKILL_METADATA", self.codes(audit.Auditor(self.root).run([])))

    def test_skips_dependency_directories(self):
        self.put("node_modules/README.md", "[Broken](missing.md)")
        self.put("docs/ok.md", "# Good")
        self.assertEqual(audit.Auditor(self.root).run([])["files_checked"], 1)

    def test_invalid_scope(self):
        self.assertIn("SCOPE", self.codes(audit.Auditor(self.root).run(["../elsewhere"])))

    def test_mdx_is_not_certified(self):
        self.put("guide.mdx", "# JSX")
        self.assertIn("UNSUPPORTED_DOCUMENT", self.codes(audit.Auditor(self.root).run(["guide.mdx"])))

    def manifest(self, target="```bash\necho hello\n```", stale=False):
        source = self.put("README.md", "# Hello\n\n```bash\necho hello\n```")
        translated = self.put("README.th.md", "# สวัสดี\n\n" + target)
        data = {"version": 1, "translations": [{"source": "README.md", "target": "README.th.md", "language": "th", "source_sha256": "outdated" if stale else audit.digest(source), "target_sha256": audit.digest(translated)}]}
        self.put("i18n-manifest.json", json.dumps(data))
        return audit.Auditor(self.root).run([], "i18n-manifest.json")

    def test_translation_current(self):
        self.assertEqual(self.manifest()["counts"]["warning"], 0)

    def test_translation_stale(self):
        self.assertIn("TRANSLATION_STALE", self.codes(self.manifest(stale=True)))

    def test_translation_code_difference(self):
        self.assertIn("TRANSLATION_CODE", self.codes(self.manifest("```bash\necho changed\n```")))

    def test_translation_target_change(self):
        self.manifest()
        self.put("README.th.md", "# เปลี่ยนแล้ว")
        self.assertIn("TRANSLATION_REVIEW", self.codes(audit.Auditor(self.root).run([], "i18n-manifest.json")))

    def test_translation_invalid_manifest(self):
        self.put("i18n-manifest.json", "[]")
        self.assertIn("TRANSLATION_MANIFEST", self.codes(audit.Auditor(self.root).run([], "i18n-manifest.json")))

    def test_audit_does_not_change_files(self):
        self.manifest()
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        audit.Auditor(self.root).run([], "i18n-manifest.json")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_cli_strict_and_json(self):
        self.put("README.md", "# A\n\n### C")
        result = subprocess.run([sys.executable, str(SCRIPTS / "audit.py"), str(self.root), "--strict", "--json"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["counts"]["warning"], 1)

    def test_cli_error_for_missing_root(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "audit.py"), str(self.root / "absent")], capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT / "examples/workflow.json").read_text(encoding="utf-8"))

    def test_four_svg_variants(self):
        assets = render.build_assets(self.spec)
        self.assertEqual(sum(name.endswith(".svg") for name in assets), 4)
        for name, content in assets.items():
            if name.endswith(".svg"):
                self.assertTrue(ET.fromstring(content).tag.endswith("svg"))

    def test_theme_geometry_and_text_match(self):
        assets = render.build_assets(self.spec)
        for language in ("en", "th"):
            roots = [ET.fromstring(assets[f"workflow.{language}.{theme}.svg"]) for theme in ("light", "dark")]
            def geometry(root):
                return [(element.tag, {key: value for key, value in element.attrib.items() if key not in {"fill", "stroke"}}, element.text) for element in root.iter()]
            self.assertEqual(geometry(roots[0]), geometry(roots[1]))

    def test_provenance_is_not_ai(self):
        assets = render.build_assets(self.spec)
        manifest = json.loads(assets["workflow.manifest.json"])
        self.assertFalse(manifest["ai_generated"])
        for name, expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256(assets[name].encode()).hexdigest(), expected)

    def test_written_svg_hashes_match_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            render.write_assets(output, render.build_assets(self.spec))
            manifest = json.loads((output / "workflow.manifest.json").read_bytes())
            for name, expected in manifest["files"].items():
                self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), expected)

    def test_deterministic(self):
        self.assertEqual(render.build_assets(self.spec), render.build_assets(self.spec))

    def test_xml_escaping(self):
        self.spec["locales"]["en"]["title"] = "A < B & C"
        content = render.build_assets(self.spec)["workflow.en.light.svg"]
        ET.fromstring(content)
        self.assertIn("A &lt; B &amp; C", content)

    def test_long_label_rejected(self):
        self.spec["locales"]["en"]["title"] = "A" * 100
        with self.assertRaises(ValueError):
            render.build_assets(self.spec)

    def test_control_character_rejected(self):
        self.spec["locales"]["en"]["title"] = "Bad\x00"
        with self.assertRaises(ValueError):
            render.build_assets(self.spec)

    def test_path_in_name_rejected(self):
        self.spec["name"] = "../escape"
        with self.assertRaises(ValueError):
            render.build_assets(self.spec)

    def test_locale_topology_count_consistent(self):
        self.spec["locales"]["th"]["steps"].pop()
        with self.assertRaises(ValueError):
            render.build_assets(self.spec)

    def test_rtl_smoke(self):
        content = copy.deepcopy(self.spec["locales"]["en"])
        content["direction"] = "rtl"
        content["title"] = "دليل التوثيق"
        self.spec["locales"] = {"ar": content}
        svg = render.build_assets(self.spec)["workflow.ar.light.svg"]
        ET.fromstring(svg)
        self.assertIn('direction="rtl"', svg)
        self.assertIn('xml:lang="ar"', svg)

    def test_no_overwrite_without_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            render.write_assets(output, {"a.svg": "first"})
            with self.assertRaises(ValueError):
                render.write_assets(output, {"a.svg": "second"})
            self.assertEqual((output / "a.svg").read_text(), "first")
            render.write_assets(output, {"a.svg": "second"}, True)
            self.assertEqual((output / "a.svg").read_text(), "second")

    def test_symlink_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "target").write_text("original")
            make_test_symlink(root / "a.svg", root / "target")
            with self.assertRaises(ValueError):
                render.write_assets(root, {"a.svg": "replacement"}, True)
            self.assertEqual((root / "target").read_text(), "original")

    def test_palette_text_contrast(self):
        def luminance(color):
            values = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
            return sum(value * weight for value, weight in zip(linear, [0.2126, 0.7152, 0.0722]))
        for palette in render.PALETTES.values():
            for foreground, background in [("text", "background"), ("muted", "background"), ("text", "surface"), ("muted", "surface"), ("surface", "accent")]:
                values = sorted([luminance(palette[foreground]), luminance(palette[background])])
                self.assertGreaterEqual((values[1] + 0.05) / (values[0] + 0.05), 4.5)



class ProviderPortabilityTests(unittest.TestCase):
    """Preflight is a policy check, not a claim to have invoked real agents."""

    def profile(self, agent=None, **overrides):
        capabilities = {key: None for key in capability_plan.CAPABILITIES}
        capabilities.update(overrides)
        return {
            "agent": agent,
            "capabilities": capabilities,
            "tasks": [
                "static_audit", "edit_markdown", "mermaid_diagram", "svg_diagram",
                "ai_illustration", "paired_ai_illustration", "dark_light_assets",
                "multilingual_draft", "local_preview", "github_preview",
            ],
        }

    def task(self, report, name):
        return next(row for row in report["tasks"] if row["task"] == name)

    def test_same_capabilities_are_provider_invariant(self):
        p = self.profile(read_files=True, write_files=True, run_commands=True, python=True)
        outputs = []
        for agent in ("codex", "claude-code", "gemini-cli", "cursor", "opencode", "unknown-agent"):
            p["agent"] = agent
            outputs.append(capability_plan.plan(p)["tasks"])
        self.assertTrue(all(value == outputs[0] for value in outputs))

    def test_unprovided_capabilities_are_unknown(self):
        p = self.profile()
        self.assertIsNone(capability_plan.plan(p)["capabilities"]["image_generate"])
        self.assertEqual(self.task(capability_plan.plan(p), "ai_illustration")["status"], "unverified")

    def test_all_true_uses_host_capabilities(self):
        p = self.profile(**{key: True for key in capability_plan.CAPABILITIES})
        result = capability_plan.plan(p)
        self.assertEqual(self.task(result, "ai_illustration")["method"], "host-image-generation")
        self.assertEqual(self.task(result, "paired_ai_illustration")["status"], "ready")
        self.assertEqual(self.task(result, "github_preview")["status"], "ready")
        self.assertEqual(self.task(result, "multilingual_draft")["status"], "review-required")
        self.assertTrue(all(row["execution"] == "not-run" for row in result["tasks"]))

    def test_declared_absent_ai_tool_not_faked(self):
        p = self.profile(read_files=True, write_files=True, image_generate=False, run_commands=True, python=True)
        result = capability_plan.plan(p)
        self.assertEqual(self.task(result, "ai_illustration")["status"], "blocked")
        self.assertEqual(self.task(result, "dark_light_assets")["method"], "offline-deterministic-svg")

    def test_no_image_edit_blocks_consistent_ai_pair(self):
        result = capability_plan.plan(self.profile(write_files=True, image_generate=True, image_edit=False))
        self.assertEqual(self.task(result, "ai_illustration")["status"], "ready")
        self.assertEqual(self.task(result, "paired_ai_illustration")["status"], "blocked")

    def test_mermaid_without_python(self):
        result = capability_plan.plan(self.profile(write_files=True, python=False, run_commands=False))
        self.assertEqual(self.task(result, "mermaid_diagram")["status"], "ready")
        self.assertEqual(self.task(result, "svg_diagram")["status"], "fallback")
        self.assertEqual(self.task(result, "svg_diagram")["method"], "github-mermaid-code-block")

    def test_no_file_write_cannot_edit(self):
        result = capability_plan.plan(self.profile(read_files=True, write_files=False))
        self.assertEqual(self.task(result, "edit_markdown")["status"], "blocked")
        self.assertEqual(self.task(result, "mermaid_diagram")["status"], "blocked")

    def test_no_python_static_audit_fallback(self):
        result = capability_plan.plan(self.profile(read_files=True, python=False))
        self.assertEqual(self.task(result, "static_audit")["method"], "manual-readonly-review")

    def test_browser_without_network_not_github_preview(self):
        result = capability_plan.plan(self.profile(browser=True, network=False))
        self.assertEqual(self.task(result, "local_preview")["status"], "ready")
        self.assertEqual(self.task(result, "github_preview")["status"], "blocked")

    def test_no_file_access_cannot_audit_repo(self):
        result = capability_plan.plan(self.profile(read_files=False))
        self.assertEqual(self.task(result, "static_audit")["status"], "blocked")

    def test_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            capability_plan.plan({"capabilities": {"vendor_specific_flag": True}, "tasks": ["static_audit"]})

    def test_invalid_types_rejected(self):
        with self.assertRaises(ValueError):
            capability_plan.plan({"capabilities": {"browser": "yes"}, "tasks": ["github_preview"]})

    def test_duplicate_tasks_rejected(self):
        with self.assertRaises(ValueError):
            capability_plan.plan({"capabilities": {}, "tasks": ["static_audit", "static_audit"]})

    def test_cli_json_and_no_side_effects(self):
        case = ROOT / "examples/host-capabilities.json"
        before = case.read_bytes()
        proc = subprocess.run([sys.executable, str(SCRIPTS / "capability_plan.py"), "--input", str(case)], capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(self.task(result, "ai_illustration")["status"], "blocked")
        self.assertEqual(case.read_bytes(), before)

    def test_cli_bad_json_exit_two(self):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "capability_plan.py")], input="{unclosed", capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Capability preflight", proc.stderr)

    def test_examples_are_stable_and_covered(self):
        profile = json.loads((ROOT / "examples/host-capabilities.json").read_text())
        report = capability_plan.plan(profile)
        self.assertEqual(report["agent"], "example-host-do-not-assume-provider")
        self.assertEqual(len(report["tasks"]), len(profile["tasks"]))

if __name__ == "__main__":
    unittest.main()
