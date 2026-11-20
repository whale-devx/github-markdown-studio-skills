"""Bounded, offline formatting checks; never a GitHub/MathJax/Mermaid renderer.

Consumes markdown-it tokens with source-line offsets already applied. Findings
are authored-document diagnostics, not a complete grammar or security validator.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

SURFACES = ("repository", "issue", "pull-request", "discussion", "wiki", "comment", "commit-message")
TARGETS = ("unknown", "default", "non-default")
ALERTS = {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}
REFERENCE = r"(?<![\w/\\])(?:[\w.-]+/[\w.-]+)?(?:#|GH-)\d+\b"
CLOSING = re.compile(r"\b(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?):?\s+(?:[\w.-]+/[\w.-]+)?#\d+\b", re.I)


class DetailsChecks(HTMLParser):
    def __init__(self, add):
        super().__init__(convert_charrefs=True)
        self.add, self.stack = add, []
        self.base = self.start = 1

    def fragment(self, text, line):
        self.base, self.start = line, self.getpos()[0]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        line = self.base + self.getpos()[0] - self.start
        if tag == "details":
            self.stack.append([line, 0])
        elif tag == "summary":
            if not self.stack:
                self.add("warning", "SUMMARY_ORPHAN", line, "Place <summary> inside <details>.")
            else:
                self.stack[-1][1] += 1

    def handle_endtag(self, tag):
        if tag != "details":
            return
        line = self.base + self.getpos()[0] - self.start
        if not self.stack:
            self.add("warning", "DETAILS_ORPHAN", line, "Closing </details> has no matching opener.")
            return
        start, count = self.stack.pop()
        if count != 1:
            self.add("warning", "DETAILS_SUMMARY", start, "Use exactly one descriptive <summary> per <details>.")

    def finish(self):
        self.close()
        for line, _ in self.stack:
            self.add("warning", "DETAILS_UNCLOSED", line, "Close this <details> section explicitly.")


def cells(line):
    """Count source cells, respecting odd/even backslash escapes before pipes."""
    line = re.sub(r"^\s*(?:>\s*)*", "", line).strip()
    parts, part, escaped = [], [], False
    for char in line:
        if char == "|" and not escaped:
            parts.append("".join(part))
            part = []
        else:
            part.append(char)
        escaped = not escaped if char == "\\" else False
    parts.append("".join(part))
    if parts and not parts[0].strip():
        parts.pop(0)
    if parts and not parts[-1].strip():
        parts.pop()
    return len(parts)


def check_map(content, kind, add, line):
    def reject_constant(value):
        raise ValueError("Non-JSON numeric constant")
    try:
        data = json.loads(content, parse_constant=reject_constant)
    except (ValueError, RecursionError):
        add("error", "DIAGRAM_JSON", line, "Map block must contain valid JSON; NaN/Infinity are not JSON.")
        return
    valid = isinstance(data, dict)
    if valid and kind == "topojson":
        valid = data.get("type") == "Topology" and isinstance(data.get("objects"), dict) and isinstance(data.get("arcs"), list)
    elif valid:
        kind_name = data.get("type")
        if kind_name == "FeatureCollection":
            valid = isinstance(data.get("features"), list)
        elif kind_name == "Feature":
            valid = "geometry" in data and (data["geometry"] is None or isinstance(data["geometry"], dict)) and "properties" in data and (data["properties"] is None or isinstance(data["properties"], dict))
        elif kind_name == "GeometryCollection":
            valid = isinstance(data.get("geometries"), list)
        else:
            valid = isinstance(kind_name, str) and kind_name in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"} and isinstance(data.get("coordinates"), list)
    if not valid:
        add("error", "DIAGRAM_STRUCTURE", line, f"Review required top-level {kind} type and members; nested geometry is not validated.")


def check_permalink(url, add, line):
    try:
        parsed = urlsplit(url)
    except ValueError:
        return  # The base URL checker owns malformed URLs.
    match = re.match(r"^/[^/]+/[^/]+/blob/([^/]+)/(.+)$", parsed.path)
    if parsed.hostname != "github.com" or not match or not parsed.fragment.startswith("L"):
        return
    ref, path = match.groups()
    if not re.fullmatch(r"[0-9a-fA-F]{40}", ref):
        add("warning", "PERMALINK_MUTABLE", line, "Use Copy permalink / a full commit SHA for stable line evidence, not a moving branch or tag.")
    numbers = re.fullmatch(r"L([1-9]\d*)(?:-L([1-9]\d*))?", parsed.fragment)
    if not numbers or (numbers[2] and (len(numbers[2]), numbers[2]) < (len(numbers[1]), numbers[1])):
        add("warning", "PERMALINK_LINES", line, "Use #Lstart or #Lstart-Lend with positive ascending line numbers.")
    if path.lower().endswith((".md", ".markdown")) and parse_qs(parsed.query).get("plain") != ["1"]:
        add("warning", "PERMALINK_MARKDOWN", line, "Use ?plain=1 before a Markdown source-line fragment.")


def prose(token):
    """Ignore linked labels, inline code, and inline HTML/comments in prose rules."""
    result, depth = [], 0
    for child in token.children or []:
        if child.type == "link_open":
            depth += 1
        elif child.type == "link_close":
            depth -= 1
        elif child.type == "text" and depth == 0:
            result.append(child.content)
        else:
            result.append(" ")
    return "".join(result)


def check(text, tokens, add, surface="repository", pr_target="unknown"):
    if surface not in SURFACES or pr_target not in TARGETS:
        raise ValueError("Invalid rendering surface or pull-request target")
    lines, details = text.splitlines(), DetailsChecks(add)
    display_open = None
    for token in tokens:
        line = token.map[0] + 1 if token.map else 1
        if token.type == "html_block":
            details.fragment(token.content, line)
        for child in token.children or []:
            if child.type == "html_inline":
                details.fragment(child.content, line)
            if child.type == "link_open":
                check_permalink(child.attrGet("href") or "", add, line)
        if token.type == "table_open" and token.map:
            start, end = token.map
            width = cells(lines[start])
            for row in range(start + 2, end):
                if cells(lines[row]) != width:
                    add("warning", "TABLE_COLUMNS", row + 1, "Table row has a different cell count; escape literal pipes and review omitted/truncated cells.")
        if token.type == "fence":
            info = token.info.split(maxsplit=1)[0] if token.info.strip() else ""
            if token.map:
                last = lines[token.map[1] - 1]
                ending = r"\s*(?:>\s*)*" + re.escape(token.markup[0]) + "{" + str(len(token.markup)) + r",}\s*"
                if token.map[1] - token.map[0] < 2 or not re.fullmatch(ending, last):
                    add("warning", "FENCE_UNCLOSED", line, "Explicitly close the fence; GFM permits implicit closure but following prose may become code.")
            if info in {"geojson", "topojson"}:
                check_map(token.content, info, add, line)
            elif info in {"mermaid", "math", "stl"} and not token.content.strip():
                add("warning", "SPECIAL_BLOCK_EMPTY", line, "Add content or remove the empty diagram/math block.")
            if info == "math" and "$$" in token.content:
                add("warning", "MATH_FENCE_DELIMITERS", line, "A math fence already delimits the expression; remove extra $$ wrappers.")
            if info == "stl" and token.content.strip():
                body = token.content.strip().splitlines()
                facets = re.findall(r"\bfacet\s+normal\b", token.content)
                ends = re.findall(r"\bendfacet\b", token.content)
                vertices = re.findall(r"(?m)^\s*vertex\s+", token.content)
                if not body[0].lstrip().startswith("solid ") or not body[-1].lstrip().startswith("endsolid") or not facets or len(facets) != len(ends) or len(vertices) != 3 * len(facets):
                    add("warning", "STL_STRUCTURE", line, "Review ASCII solid/endsolid and triangular facet boundaries; this is not a mesh validator.")
            if info == "tasklist":
                add("warning", "TASKLIST_RETIRED", line, "Tasklist blocks are retired; use ordinary Markdown tasks or authorized sub-issue workflows.")
        if token.type != "inline":
            continue
        content = prose(token)
        if surface in {"repository", "wiki"}:
            refs = [m for m in re.finditer(REFERENCE, content) if "\\" + m[0] not in token.content]
            if refs:
                add("warning", "AUTOLINK_SURFACE", line, "Issue/PR shorthand is not autolinked in repository files or wikis; use explicit Markdown links.")
        if CLOSING.search(content):
            if surface not in {"pull-request", "commit-message"}:
                add("warning", "CLOSING_CONTEXT", line, "Closing keywords act in PR descriptions or commit messages, not this destination; do not imply an issue was closed.")
            elif surface == "pull-request" and pr_target != "default":
                add("warning", "CLOSING_TARGET", line, "Verify the PR targets the default branch; other targets ignore closing keywords.")
        if re.search(r"\bDuplicate of\s+#\d+", content, re.I) and surface != "comment":
            add("warning", "DUPLICATE_CONTEXT", line, "Duplicate markers belong in a new issue/PR comment, with authorization.")
        alert = re.match(r"^\[!([A-Za-z]+)\](?:\s|$)", token.content)
        if alert:
            if alert[1] not in ALERTS:
                add("warning", "ALERT_TYPE", line, "Use NOTE, TIP, IMPORTANT, WARNING or CAUTION.")
            if token.level > 2 or details.stack:
                add("warning", "ALERT_NESTED", line, "GitHub alerts cannot be nested inside other elements.")
        if surface == "wiki" and re.search(r"\[\^[^\]]+\]", content):
            add("warning", "FOOTNOTE_SURFACE", line, "Footnotes are not supported in GitHub wikis; use ordinary links.")
        for index, raw in enumerate(token.content.splitlines()):
            # Only an exact standalone $$ line; do not guess whether currency is math.
            if raw.strip() == "$$":
                display_open = None if display_open is not None else line + index
        if token.map:
            raw = lines[token.map[0]]
            task = re.match(r"^\s*(?:>\s*)*(?:[-+*]|\d+[.)])\s+\[([ xX-]?)\](.*)$", raw)
            if task and (task[1] not in {" ", "x", "X"} or (task[2] and not task[2][0].isspace())):
                add("warning", "TASK_MARKER", line, "Use [ ] or [x] followed by whitespace for a Markdown task.")
        for match in re.finditer(r"https://github\.com/[^\s<>]+", content):
            check_permalink(match[0].rstrip(".,;"), add, line)
    details.finish()
    if display_open is not None:
        add("warning", "MATH_BLOCK_UNCLOSED", display_open, "Review the unmatched standalone $$ delimiter; MathJax was not executed.")
