#!/usr/bin/env python3
"""Read-only, offline Markdown checks. This is not GitHub's renderer."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

try:
    from markdown_it import MarkdownIt
    import yaml
except ImportError:
    raise SystemExit("Install audit dependencies: python -m pip install -r <skill>/scripts/requirements.txt")

MAX_BYTES = 2 * 1024 * 1024
EXCLUDED = {".git", ".venv", "venv", "node_modules", "vendor", "dist", "build", "__pycache__"}
LOCALE = re.compile(r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*\Z")
PARSER = MarkdownIt("commonmark").enable(["table", "strikethrough"])


@dataclass
class Finding:
    severity: str
    code: str
    path: str
    line: int
    message: str


def contained(root: Path, path: Path) -> Path:
    """Reject traversal and symlinks that escape the explicitly selected root."""
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Path escapes repository root")
    return resolved


def read_text(path: Path) -> str:
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Expected a regular file no larger than 2 MiB")
    return path.read_text(encoding="utf-8-sig")


def digest(path: Path) -> str:
    # Hash bytes, not normalized text: a changed source always needs review.
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Expected a regular file no larger than 2 MiB")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_frontmatter(text: str) -> tuple[object, str, int]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text, 0
    for index, line in enumerate(lines[1:], 1):
        if line.strip() in {"---", "..."}:
            header = yaml.safe_load("".join(lines[1:index]))
            return header, "".join(lines[index + 1:]), index + 1
    raise ValueError("Unclosed YAML frontmatter")


def slug(text: str) -> str:
    """Conservative Unicode heading approximation, not a GitHub parity claim."""
    value = "".join(c for c in text.lower() if c in " -_" or unicodedata.category(c)[0] in "LNM")
    return value.replace(" ", "-")


def heading_ids(tokens: list) -> set[str]:
    used: set[str] = set()
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or index + 1 >= len(tokens):
            continue
        inline = tokens[index + 1]
        label = "".join(t.content for t in inline.children or [] if t.type in {"text", "code_inline", "image"})
        base = slug(label)
        candidate, count = base, 0
        while candidate in used:
            count += 1
            candidate = f"{base}-{count}"
        used.add(candidate)
    return used


class HTMLChecks(HTMLParser):
    """Inspect HTML tokens only; never interpret comments or code examples."""
    def __init__(self, add, references):
        super().__init__(convert_charrefs=True)
        self.add = add
        self.references = references
        self.pictures: list[dict] = []
        self.anchors: set[str] = set()
        self.base = 1
        self.start = 1

    def fragment(self, content: str, line: int) -> None:
        self.base, self.start = line, self.getpos()[0]
        self.feed(content)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        values = dict(attrs)
        line = self.base + self.getpos()[0] - self.start
        if tag in {"script", "iframe", "style", "object", "embed"}:
            self.add("error", "UNSAFE_HTML", line, f"Remove unsupported or active <{tag}> content.")
        if any(key.startswith("on") for key in values):
            self.add("error", "EVENT_HANDLER", line, "Remove HTML event-handler attributes.")
        if "style" in values:
            self.add("warning", "INLINE_STYLE", line, "GitHub sanitizes inline styles; use native Markdown/HTML features.")
        if tag == "a":
            if values.get("name"):
                self.anchors.add(values["name"])
            if values.get("href"):
                self.references.append((values["href"], line))
        if tag == "picture":
            self.pictures.append({"line": line, "fallback": False, "themes": set()})
        if tag == "source":
            if self.pictures:
                media = values.get("media") or ""
                for theme in ("dark", "light"):
                    if re.search(r"prefers-color-scheme\s*:\s*" + theme + r"\b", media):
                        self.pictures[-1]["themes"].add(theme)
            srcset = values.get("srcset") or ""
            if srcset.lower().lstrip().startswith("data:"):
                self.add("error", "UNSAFE_URL", line, "Do not embed data URLs in GitHub documentation.")
            else:
                for item in srcset.split(","):
                    parts = item.strip().split()
                    if parts:
                        self.references.append((parts[0], line))
        if tag == "img":
            src = values.get("src") or ""
            if src:
                self.references.append((src, line))
            else:
                self.add("error", "IMAGE_SRC", line, "Image is missing a non-empty src.")
            decorative = values.get("role") == "presentation" or values.get("aria-hidden") == "true"
            if not (values.get("alt") or "").strip() and not decorative:
                self.add("warning", "IMAGE_ALT", line, "Provide meaningful alt text, or explicitly mark a decorative HTML image.")
            if self.pictures and src:
                self.pictures[-1]["fallback"] = True

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "picture" and self.pictures:
            picture = self.pictures.pop()
            if not picture["fallback"]:
                self.add("error", "PICTURE_FALLBACK", picture["line"], "Add an <img src=... alt=...> fallback inside <picture>.")
            if picture["themes"] and picture["themes"] != {"dark", "light"}:
                self.add("warning", "PICTURE_THEMES", picture["line"], "Declare both dark and light sources for a theme-aware picture.")

    def finish(self) -> None:
        self.close()
        for picture in self.pictures:
            self.add("error", "PICTURE_UNCLOSED", picture["line"], "Close the <picture> element.")


class Auditor:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.findings: list[Finding] = []
        self.documents: dict[Path, tuple[list, set[str]]] = {}
        self.external_links = 0
        self.checked = 0

    def add(self, path: Path, severity: str, code: str, line: int, message: str) -> None:
        name = str(path.relative_to(self.root)) if path.is_relative_to(self.root) else str(path)
        self.findings.append(Finding(severity, code, name, line, message))

    def load(self, path: Path) -> tuple[list, set[str]]:
        if path in self.documents:
            return self.documents[path]
        metadata, body, offset = split_frontmatter(read_text(path))
        tokens = PARSER.parse(body)
        for token in tokens:
            if token.map:
                token.map = [number + offset for number in token.map]
        anchors = heading_ids(tokens)
        html = HTMLChecks(lambda *args: None, [])
        for token in tokens:
            if token.type == "html_block":
                html.fragment(token.content, 1)
            for child in token.children or []:
                if child.type == "html_inline":
                    html.fragment(child.content, 1)
        anchors.update(html.anchors)
        self.documents[path] = (tokens, anchors)
        return tokens, anchors

    def check_skill(self, path: Path, metadata: object) -> None:
        def error(message):
            self.add(path, "error", "SKILL_METADATA", 1, message)
        if not isinstance(metadata, dict):
            error("SKILL.md needs YAML frontmatter containing name and description.")
            return
        name = metadata.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64 or name != path.parent.name:
            error("name must match the parent directory and use 1-64 lowercase letters/digits with single hyphens.")
        description = metadata.get("description")
        if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
            error("description must be a non-empty string of at most 1024 characters.")
        compatibility = metadata.get("compatibility")
        if compatibility is not None and (not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500):
            error("compatibility must be a string of 1-500 characters.")
        extra = metadata.get("metadata", {})
        if not isinstance(extra, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in extra.items()):
            error("metadata must map strings to strings; quote version numbers.")

    def check_link(self, source: Path, url: str, line: int) -> None:
        try:
            parsed = urlsplit(url)
            scheme = parsed.scheme.lower()
            if scheme or parsed.netloc:
                if scheme and scheme not in {"http", "https", "mailto", "tel"}:
                    self.add(source, "error", "UNSAFE_URL", line, "Use repository-relative paths or ordinary web/contact URLs.")
                else:
                    self.external_links += 1
                return
            raw = unquote(parsed.path)
            if "\x00" in raw or "\\" in raw:
                raise ValueError("Invalid local URL path")
            base = self.root if raw.startswith("/") else source.parent
            target = contained(self.root, base / raw.lstrip("/")) if raw else source
            if not target.exists():
                self.add(source, "error", "BROKEN_LOCAL_LINK", line, f"Local target does not exist: {raw}")
            elif parsed.fragment and target.is_file() and target.suffix.lower() in {".md", ".markdown"}:
                _, anchors = self.load(target)
                if unquote(parsed.fragment) not in anchors:
                    self.add(source, "warning", "ANCHOR_REVIEW", line, "Fragment not found by the local heading approximation; verify on GitHub.")
        except (ValueError, OSError, UnicodeError, yaml.YAMLError) as exc:
            self.add(source, "error", "LINK_PATH", line, f"Cannot safely resolve local link ({type(exc).__name__}).")

    def check_document(self, path: Path) -> None:
        try:
            text = read_text(path)
            metadata, _, _ = split_frontmatter(text)
            if path.name == "SKILL.md":
                self.check_skill(path, metadata)
                if len(text.splitlines()) >= 500:
                    self.add(path, "warning", "SKILL_LENGTH", 1, "Move detailed material to references; keep SKILL.md under 500 lines.")
            tokens, _ = self.load(path)
        except (ValueError, OSError, UnicodeError, yaml.YAMLError) as exc:
            self.add(path, "error", "DOCUMENT_PARSE", 1, f"Cannot read/parse document ({type(exc).__name__}).")
            return
        self.checked += 1
        references: list[tuple[str, int]] = []
        html = HTMLChecks(lambda severity, code, line, message: self.add(path, severity, code, line, message), references)
        previous = 0
        for token in tokens:
            line = token.map[0] + 1 if token.map else 1
            if token.type == "heading_open":
                level = int(token.tag[1:])
                if previous and level > previous + 1:
                    self.add(path, "warning", "HEADING_JUMP", line, "Avoid skipping heading levels.")
                previous = level
            if token.type == "html_block":
                html.fragment(token.content, line)
            for child in token.children or []:
                if child.type == "link_open":
                    references.append((child.attrGet("href") or "", line))
                elif child.type == "image":
                    references.append((child.attrGet("src") or "", line))
                    if not child.content.strip():
                        self.add(path, "warning", "IMAGE_ALT", line, "Describe meaningful images; review empty alt text manually.")
                elif child.type == "html_inline":
                    html.fragment(child.content, line)
        html.finish()
        for url, line in references:
            self.check_link(path, url, line)

    def check_translations(self, manifest: Path) -> None:
        try:
            manifest = contained(self.root, manifest)
            data = json.loads(read_text(manifest))
            if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("translations"), list):
                raise ValueError("Expected version 1 and a translations array")
            for item in data["translations"]:
                if not isinstance(item, dict) or not LOCALE.fullmatch(str(item.get("language", ""))):
                    raise ValueError("Invalid translation entry/language tag")
                source = contained(self.root, self.root / item["source"])
                target = contained(self.root, self.root / item["target"])
                if source == target:
                    raise ValueError("Source and translation must be different files")
                current_source, current_target = digest(source), digest(target)
                if current_source != item.get("source_sha256"):
                    self.add(target, "warning", "TRANSLATION_STALE", 1, "Source bytes changed or have not been recorded after translation review.")
                if current_target != item.get("target_sha256"):
                    self.add(target, "warning", "TRANSLATION_REVIEW", 1, "Translation bytes changed or have not been recorded after review.")
                def code(path):
                    tokens, _ = self.load(path)
                    return [(t.info, t.content) for t in tokens if t.type == "fence" and t.info.split(maxsplit=1)[0:1] not in [[], ["text"], ["plaintext"], ["mermaid"]]]
                if code(source) != code(target):
                    self.add(target, "warning", "TRANSLATION_CODE", 1, "Executable/configuration examples differ from the source; review intentionally localized exceptions.")
        except (ValueError, OSError, UnicodeError, KeyError, TypeError, yaml.YAMLError) as exc:
            self.add(manifest, "error", "TRANSLATION_MANIFEST", 1, f"Invalid or unreadable translation manifest ({type(exc).__name__}).")

    def run(self, scopes: list[str], manifest: str | None = None) -> dict:
        files: set[Path] = set()
        for scope in scopes or ["."]:
            try:
                chosen = contained(self.root, self.root / scope)
                if not chosen.exists():
                    raise ValueError("Scope does not exist")
                if chosen.is_file():
                    files.add(chosen)
                else:
                    for directory, dirs, names in os.walk(chosen, followlinks=False):
                        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(directory) / d).is_symlink())
                        for name in names:
                            candidate = Path(directory) / name
                            if candidate.suffix.lower() in {".md", ".markdown"}:
                                files.add(contained(self.root, candidate))
            except (ValueError, OSError) as exc:
                self.add(self.root, "error", "SCOPE", 1, f"Invalid or unsafe scan scope ({type(exc).__name__}).")
        for path in sorted(files):
            if path.suffix.lower() not in {".md", ".markdown"}:
                self.add(path, "warning", "UNSUPPORTED_DOCUMENT", 1, "Only .md and .markdown are parsed; MDX needs its own toolchain.")
            else:
                self.check_document(path)
        if manifest:
            self.check_translations(self.root / manifest)
        counts = {level: sum(f.severity == level for f in self.findings) for level in ("error", "warning")}
        return {
            "version": 1, "files_checked": self.checked, "counts": counts,
            "findings": [asdict(f) for f in self.findings],
            "verification": {
                "local_static_checks": "fail" if counts["error"] else "pass",
                "translation_hashes": "checked" if manifest else "not-run",
                "translation_semantics": "not-run", "external_links": "not-run",
                "github_render": "not-run", "visual_accessibility": "not-run",
                "mermaid_render": "not-run", "quick_start_execution": "not-run",
            },
            "external_references_skipped": self.external_links,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Repository boundary; never read linked files outside it")
    parser.add_argument("paths", nargs="*", help="Files/directories relative to root (default: entire repository)")
    parser.add_argument("--translations", help="Root-relative JSON translation manifest")
    parser.add_argument("--json", action="store_true", help="Write a JSON report to stdout")
    parser.add_argument("--strict", action="store_true", help="Return exit 1 for warnings as well as errors")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root must be an existing directory")
    report = Auditor(args.root).run(args.paths, args.translations)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in report["findings"]:
            print(f'{item["path"]}:{item["line"]}: {item["severity"]} {item["code"]}: {item["message"]}')
        print(f'{report["files_checked"]} files; {report["counts"]["error"]} errors; {report["counts"]["warning"]} warnings')
        print("Not run: remote links, GitHub rendering, visual/accessibility review, translation semantics, Mermaid rendering, quick-start execution.")
    return int(bool(report["counts"]["error"] or (args.strict and report["counts"]["warning"])))


if __name__ == "__main__":
    sys.exit(main())
