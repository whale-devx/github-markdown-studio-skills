import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/github-markdown-studio/scripts"
sys.path.insert(0, str(SCRIPTS))
import external_links as links


class ExternalLinkTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.page = "https://example.org/guide"
        self.curl = Path(sys.executable)  # An existing path. Every transport test replaces subprocess.run.
        (self.root / "guide.md").write_text(
            "[one][ref]\n\n[ref]: https://example.org/guide#one\n\n"
            '<a href="https://example.org/guide#two">two</a>\n\n'
            "`[code](https://example.org/code)`\n\n"
            "```md\n[example](https://example.org/example)\n```\n\n"
            "[contact](mailto:private@example.org) [signed](https://example.org/?key=private)\n",
            encoding="utf-8",
        )

    def test_dry_run_parses_visible_references_and_never_resolves_or_connects(self):
        with patch("socket.getaddrinfo", side_effect=AssertionError), patch("subprocess.run", side_effect=AssertionError):
            report = links.report(self.root, ["guide.md"], [], Path("missing"))
        page, = report["pages"]
        self.assertEqual((page["url"], page["status"]), (self.page, "not-run"))
        self.assertEqual([loc["line"] for loc in page["locations"]], [1, 5])
        self.assertEqual(len(report["omitted_locations"]), 2)
        self.assertNotIn("private", json.dumps(report))

    def test_invalid_selection_or_partial_scope_aborts_before_first_request(self):
        with patch("external_links.check", side_effect=AssertionError):
            with self.assertRaisesRegex(ValueError, "exact page"):
                links.report(self.root, ["guide.md"], [self.page, "https://other.org"], self.curl)
            with self.assertRaisesRegex(ValueError, "readable Markdown"):
                links.report(self.root, ["guide.md", "absent.md"], [self.page], self.curl)

    def test_page_check_leaves_nonempty_fragments_unchecked_at_their_source_locations(self):
        (self.root / "mixed.md").write_text(
            f"[page]({self.page}) and [section]({self.page}#private-section)\n\n"
            f'<a href="{self.page}#:~:text=private-text">passage</a>\n\n'
            f"[top]({self.page}#)\n\n[encoded]({self.page}%23part)\n",
            encoding="utf-8",
        )
        for selected in ([], [self.page]):
            with self.subTest(selected=selected), patch("external_links.check", return_value={
                "status": "pass", "http_status": 200,
            }) as check:
                report = links.report(self.root, ["mixed.md"], selected, self.curl)
                first, encoded = report["pages"]
                self.assertEqual(first["status"], "pass" if selected else "not-run")
                self.assertEqual([(loc["line"], loc.get("fragment_status")) for loc in first["locations"]],
                                 [(1, None), (1, "not-run"), (3, "not-run"), (5, None)])
                self.assertEqual(encoded["url"], self.page + "%23part")
                self.assertNotIn("fragment_status", encoded["locations"][0])
                self.assertNotIn("private-", json.dumps(report))
                if selected:
                    check.assert_called_once_with(self.page, self.curl)
                else:
                    check.assert_not_called()

    def test_unsupported_urls(self):
        for value in ("//example.org/a", "http://example.org", "https://user:secret@example.org/",
                      "https://example.org:444/", "https://127.0.0.1/", "https://localhost/",
                      "https://[::1]/", "https://example.org\\other", "https://example.org/a\nb"):
            with self.subTest(value=value):
                self.assertIsNone(links.page_url(value))

    def test_encoded_and_literal_international_paths_refer_to_one_page(self):
        page = "https://example.org/%E0%B9%84%E0%B8%97%E0%B8%A2"
        self.assertEqual(links.page_url("https://EXAMPLE.ORG:443/ไทย#section"), page)
        self.assertEqual(links.page_url(page), page)

    @patch("subprocess.run")
    @patch("socket.getaddrinfo")
    def test_private_or_mixed_resolution_blocks_before_http(self, resolve, run):
        for address in ("127.0.0.1", "10.0.0.2", "169.254.1.2", "::1", "224.0.0.5"):
            with self.subTest(address=address):
                resolve.return_value = [(None, None, None, None, (ip, 443)) for ip in ("1.1.1.1", address)]
                self.assertEqual(links.check(self.page, self.curl)["reason"], "public-address-required")
        run.assert_not_called()

    @patch("subprocess.run")
    @patch("socket.getaddrinfo")
    def test_one_pinned_head_per_selected_page_without_credentials_or_redirects(self, resolve, run):
        resolve.return_value = [(None, None, None, None, ("1.1.1.1", 443))]
        run.return_value = subprocess.CompletedProcess([], 0, b"200")
        with patch.dict("os.environ", HTTPS_PROXY="private", GITHUB_TOKEN="private", CURL_HOME="private"):
            result = links.report(self.root, ["guide.md"], [self.page, self.page], self.curl)
        self.assertEqual(result["pages"][0]["http_status"], 200)
        run.assert_called_once()
        args, = run.call_args.args
        self.assertEqual(args[1], "--disable")
        self.assertIn("example.org:443:1.1.1.1", args)
        self.assertIn("--head", args)
        self.assertEqual(args[-2:], ["--", self.page])
        self.assertNotIn("--location", args)
        self.assertNotIn("private", run.call_args.kwargs["env"].values())

    @patch("subprocess.run")
    @patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("1.1.1.1", 443))])
    def test_failures_are_distinct_from_inconclusive_responses(self, resolve, run):
        for status, expected in ((204, "pass"), (301, "blocked"), (403, "blocked"), (404, "fail"),
                                 (405, "blocked"), (410, "fail"), (429, "blocked"), (503, "blocked")):
            with self.subTest(status=status):
                run.return_value = subprocess.CompletedProcess([], 0, str(status).encode())
                self.assertEqual(links.check(self.page, self.curl)["status"], expected)
        run.return_value = subprocess.CompletedProcess([], 60, b"000")
        self.assertEqual(links.check(self.page, self.curl), {"status": "blocked", "reason": "transport", "curl_exit": 60})
