"""Surface-aware structural regressions, not tests of live GitHub rendering."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/github-markdown-studio/scripts"
spec = importlib.util.spec_from_file_location("audit_advanced_tests", SCRIPTS / "audit.py")
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)
SHA = "e921dd88511db4361980b5cd4531001a9576dd93"


class AdvancedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def report(self, text, surface="repository", target="unknown"):
        (self.root / "doc.md").write_text(text, encoding="utf-8")
        return audit.Auditor(self.root, surface, target).run(["doc.md"])

    def codes(self, text, surface="repository", target="unknown"):
        return {f["code"] for f in self.report(text, surface, target)["findings"]}

    def test_table_extra_cells_warn(self):
        self.assertIn("TABLE_COLUMNS", self.codes("| A | B |\n|---|---|\n|1|2|3|"))

    def test_table_missing_cells_warn(self):
        self.assertIn("TABLE_COLUMNS", self.codes("| A | B |\n|---|---|\n|1|"))

    def test_table_escaped_pipe(self):
        self.assertNotIn("TABLE_COLUMNS", self.codes("| A | B |\n|---|---|\n|`a\\|b`|2|"))

    def test_table_even_backslash_not_escape(self):
        self.assertEqual(audit.advanced.cells(r"| a\\|b | c |"), 3)

    def test_table_optional_outer_pipes(self):
        self.assertNotIn("TABLE_COLUMNS", self.codes("A | B\n---|---\n1|2"))

    def test_details_missing_summary(self):
        self.assertIn("DETAILS_SUMMARY", self.codes("<details>text</details>"))

    def test_details_unclosed(self):
        self.assertIn("DETAILS_UNCLOSED", self.codes("<details>\n<summary>More</summary>"))

    def test_details_duplicate_summary(self):
        self.assertIn("DETAILS_SUMMARY", self.codes("<details><summary>A</summary><summary>B</summary></details>"))

    def test_details_orphan(self):
        self.assertIn("DETAILS_ORPHAN", self.codes("</details>"))

    def test_summary_orphan(self):
        self.assertIn("SUMMARY_ORPHAN", self.codes("<summary>More</summary>"))

    def test_nested_details_valid(self):
        self.assertFalse(self.codes("<details open><summary>A</summary><details><summary>B</summary></details></details>"))

    def test_unclosed_fence_warns_not_error(self):
        result = self.report("```python\nprint(1)")
        self.assertIn("FENCE_UNCLOSED", {f["code"] for f in result["findings"]})
        self.assertEqual(result["counts"]["error"], 0)

    def test_longer_outer_fence(self):
        self.assertFalse(self.codes("````md\n```python\nprint(1)\n```\n````"))

    def test_quote_and_list_fences(self):
        for text in ("> ```python\n> print(1)\n> ```", "- Example\n\n  ~~~text\n  value\n  ~~~"):
            with self.subTest(text=text):
                self.assertNotIn("FENCE_UNCLOSED", self.codes(text))

    def test_empty_special_blocks(self):
        for language in ("mermaid", "math", "stl"):
            with self.subTest(language=language):
                self.assertIn("SPECIAL_BLOCK_EMPTY", self.codes(f"```{language}\n```"))

    def test_bad_map_json(self):
        self.assertIn("DIAGRAM_JSON", self.codes("```geojson\n{broken}\n```"))

    def test_non_json_constants(self):
        self.assertIn("DIAGRAM_JSON", self.codes('```geojson\n{"type":"Point","coordinates":[NaN,0]}\n```'))

    def test_map_top_level_types(self):
        for data in ({"type": []}, {"type": {}}, {"type": None}, [], False, {"type": "Point"}, {"type": "Feature"}):
            with self.subTest(data=data):
                self.assertIn("DIAGRAM_STRUCTURE", self.codes("```geojson\n" + json.dumps(data) + "\n```"))

    def test_geojson_shapes(self):
        for data in ({"type":"FeatureCollection","features":[]}, {"type":"Point","coordinates":[0,0]}, {"type":"Feature","geometry":None,"properties":None}, {"type":"GeometryCollection","geometries":[]}):
            with self.subTest(data=data):
                self.assertFalse(self.codes("```geojson\n" + json.dumps(data) + "\n```"))

    def test_topojson_shapes(self):
        self.assertFalse(self.codes('```topojson\n{"type":"Topology","objects":{},"arcs":[]}\n```'))
        self.assertIn("DIAGRAM_STRUCTURE", self.codes('```topojson\n{"type":"Topology","objects":[]}\n```'))

    def test_map_not_full_geometry_validator(self):
        report = self.report('```geojson\n{"type":"Point","coordinates":[]}\n```')
        self.assertEqual(report["verification"]["map_render"], "not-run")

    def test_stl_incomplete_facet(self):
        self.assertIn("STL_STRUCTURE", self.codes("```stl\nsolid x\nfacet normal 0 0 1\nvertex 0 0 0\nendfacet\nendsolid x\n```"))

    def test_math_fence_extra_delimiters(self):
        self.assertIn("MATH_FENCE_DELIMITERS", self.codes("```math\n$$x^2$$\n```"))

    def test_standalone_math_unclosed(self):
        self.assertIn("MATH_BLOCK_UNCLOSED", self.codes("$$\nx^2"))

    def test_standalone_math_closed(self):
        self.assertNotIn("MATH_BLOCK_UNCLOSED", self.codes("$$\nx^2\n$$"))

    def test_inline_math_currency_not_guessed(self):
        self.assertFalse(self.codes("Cost $10. Math $`x_1 + x_2`$. Escaped \\$5.\n\n`$$`"))

    def test_repo_autolinks_warn(self):
        for ref in ("#123", "GH-123", "owner/repo#123"):
            with self.subTest(ref=ref):
                self.assertIn("AUTOLINK_SURFACE", self.codes("See " + ref))

    def test_conversation_autolinks_allowed(self):
        for surface in ("issue", "pull-request", "discussion", "comment"):
            self.assertNotIn("AUTOLINK_SURFACE", self.codes("See #123", surface))

    def test_explicit_link_and_literal_reference(self):
        self.assertNotIn("AUTOLINK_SURFACE", self.codes("[#123](https://github.com/o/r/issues/123) and `#123` and \\#123"))

    def test_closing_context(self):
        self.assertIn("CLOSING_CONTEXT", self.codes("Fixes #123"))
        self.assertIn("CLOSING_CONTEXT", self.codes("Fixes #123", "comment"))

    def test_all_closing_keywords(self):
        for keyword in ("close", "closes", "closed", "fix", "fixes", "fixed", "resolve", "resolves", "resolved"):
            with self.subTest(keyword=keyword):
                self.assertIn("CLOSING_TARGET", self.codes(keyword.upper() + ": #123", "pull-request"))

    def test_pr_default_target(self):
        self.assertNotIn("CLOSING_TARGET", self.codes("Resolves #123", "pull-request", "default"))
        self.assertIn("CLOSING_TARGET", self.codes("Resolves #123", "pull-request", "non-default"))

    def test_commit_message_context(self):
        self.assertNotIn("CLOSING_CONTEXT", self.codes("Fixes owner/repo#123", "commit-message"))

    def test_duplicate_comment_context(self):
        self.assertIn("DUPLICATE_CONTEXT", self.codes("Duplicate of #123", "issue"))
        self.assertNotIn("DUPLICATE_CONTEXT", self.codes("Duplicate of #123", "comment"))

    def test_tasklist_retirement(self):
        self.assertIn("TASKLIST_RETIRED", self.codes("```tasklist\n- [ ] Item\n```"))

    def test_malformed_task_markers(self):
        for text in ("- [] Item", "- [x]Item", "- [-] Item"):
            with self.subTest(text=text):
                self.assertIn("TASK_MARKER", self.codes(text))

    def test_ordinary_tasks(self):
        self.assertNotIn("TASK_MARKER", self.codes("- [ ] First\n- [x] Second\n- [X] Third"))

    def test_moving_permalink(self):
        self.assertIn("PERMALINK_MUTABLE", self.codes("[Code](https://github.com/o/r/blob/main/a.py#L1)"))

    def test_stable_permalink(self):
        self.assertFalse(self.codes(f"[Code](https://github.com/o/r/blob/{SHA}/a.py#L1-L2)"))

    def test_bad_permalink_ranges(self):
        for fragment in ("L0", "L2-L1", "Lx", "L2-L0"):
            with self.subTest(fragment=fragment):
                self.assertIn("PERMALINK_LINES", self.codes(f"[Code](https://github.com/o/r/blob/{SHA}/a.py#{fragment})"))

    def test_huge_line_number_does_not_crash(self):
        self.codes(f"[Code](https://github.com/o/r/blob/{SHA}/a.py#L{'9'*5000}-L1)")

    def test_markdown_plain_permalink(self):
        self.assertIn("PERMALINK_MARKDOWN", self.codes(f"[Code](https://github.com/o/r/blob/{SHA}/a.md#L1)"))
        self.assertFalse(self.codes(f"[Code](https://github.com/o/r/blob/{SHA}/a.md?plain=1#L1)"))

    def test_relative_urls_non_repository(self):
        result = self.codes("[Asset](../blob/main/asset.png)", "comment")
        self.assertIn("RELATIVE_SURFACE_REVIEW", result)
        self.assertNotIn("BROKEN_LOCAL_LINK", result)

    def test_unknown_alert(self):
        self.assertIn("ALERT_TYPE", self.codes("> [!DANGER]\n> Text"))

    def test_nested_alert(self):
        for text in ("> > [!NOTE]\n> > Text", "- > [!NOTE]\n  > Text", "<details>\n<summary>More</summary>\n\n> [!NOTE]\n> Text\n\n</details>"):
            with self.subTest(text=text):
                self.assertIn("ALERT_NESTED", self.codes(text))

    def test_five_alert_types(self):
        for name in audit.advanced.ALERTS:
            self.assertFalse(self.codes(f"> [!{name}]\n> Text"))

    def test_thai_footnote_not_a_file(self):
        self.assertNotIn("BROKEN_LOCAL_LINK", self.codes("หมายเหตุ[^r]\n\n[^r]: ตัวอย่างข้อความภาษาไทย"))

    def test_footnote_link_still_audited(self):
        self.assertIn("BROKEN_LOCAL_LINK", self.codes("Note[^r]\n\n[^r]: [Missing](missing.md)"))

    def test_wiki_footnotes_warn(self):
        self.assertIn("FOOTNOTE_SURFACE", self.codes("Note[^r]\n\n[^r]: Details", "wiki"))

    def test_code_and_comments_not_audited_as_prose(self):
        self.assertFalse(self.codes("```text\nFixes #123\n<details>\n> [!BAD]\n$$\n```\n\n<!-- <details> Fixes #123 -->"))

    def test_frontmatter_preserves_lines(self):
        result = self.report("---\ntitle: Example\n---\n```math\n$$x$$\n```")
        finding = next(f for f in result["findings"] if f["code"] == "MATH_FENCE_DELIMITERS")
        self.assertEqual(finding["line"], 4)

    def test_render_and_workflow_never_claimed(self):
        result = self.report("# Document")
        for key in ("github_render", "mermaid_render", "math_render", "map_render", "stl_render", "workflow_effects"):
            self.assertEqual(result["verification"][key], "not-run")

    def test_cli_surface_and_strict_exit(self):
        self.report("Fixes #123")
        before = (self.root / "doc.md").read_bytes()
        command = [sys.executable, str(SCRIPTS / "audit.py"), str(self.root), "doc.md", "--json", "--strict", "--surface", "pull-request"]
        bad = subprocess.run(command, capture_output=True, text=True)
        good = subprocess.run(command + ["--pr-target", "default"], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1, bad.stderr)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["pr_target"], "default")
        self.assertEqual((self.root / "doc.md").read_bytes(), before)

    def test_invalid_surface_rejected(self):
        with self.assertRaises(ValueError):
            audit.Auditor(self.root, "unrecognized")


class CoverageTests(unittest.TestCase):
    def test_all_ten_topics_have_sources_examples_and_limits(self):
        manifest = json.loads((ROOT / "skills/github-markdown-studio/assets/formatting-coverage.json").read_text())
        ids = {t["id"] for t in manifest["topics"]}
        self.assertEqual(ids, {"tables","collapsed-sections","code-blocks","diagrams","mathematics","autolinks","attachments","task-lists","permalinks","keywords"})
        for topic in manifest["topics"]:
            self.assertTrue(topic["source"].startswith("https://docs.github.com/"))
            self.assertTrue(topic["manual_review"])
            self.assertTrue(topic["automated_rules"])
            for target in topic["examples"]:
                path, anchor = target.split("#")
                self.assertIn(f'<a name="{anchor}"></a>', (ROOT / path).read_text())

    def test_showcases_are_clean_with_four_diagram_types(self):
        for language in ("en", "th"):
            path = ROOT / f"examples/advanced-formatting.{language}.md"
            result = audit.Auditor(ROOT).run([str(path.relative_to(ROOT))])
            self.assertEqual(result["counts"], {"error":0,"warning":0}, result["findings"])
            tokens, _ = audit.Auditor(ROOT).load(path)
            types = {t.info for t in tokens if t.type == "fence"}
            self.assertTrue({"mermaid","geojson","topojson","stl","math","diff"}.issubset(types))

    def test_localized_executable_blocks_match(self):
        auditor = audit.Auditor(ROOT)
        def code(lang):
            tokens, _ = auditor.load(ROOT / f"examples/advanced-formatting.{lang}.md")
            return [(t.info,t.content) for t in tokens if t.type == "fence" and t.info not in {"text","mermaid"}]
        self.assertEqual(code("en"), code("th"))


if __name__ == "__main__":
    unittest.main()
