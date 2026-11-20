# GitHub advanced formatting

Use this reference for **understand → generate → audit → transform** work. Check the target surface first. Coverage follows all ten topics in GitHub's [advanced-formatting index](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting), reviewed 2026-11-20. It is a dated capability inventory, not a promise to support future GitHub features automatically.

[Coverage and check limits](../assets/formatting-coverage.json) · [Transformation patterns](formatting-patterns.md) · [English examples](../../../examples/advanced-formatting.en.md) · [Thai examples](../../../examples/advanced-formatting.th.md)

## Surface contract

Repository files and conversations do not have identical behavior. Choose `repository`, `wiki`, `issue`, `pull-request`, `discussion`, `comment`, or `commit-message`. The last is a workflow-text context, not a claim that GitHub renders commit messages like `.md` files. A locally saved PR template needs an explicitly selected target; its filename does not prove where it will be used.

The helper only performs bounded structural checks. **Mermaid, MathJax, map/STL viewers, highlighting, uploads and issue-closing effects are not executed.** Do not label their output verified from a clean static report. Review actual GitHub output separately, on the intended surface and revision, in light/dark and narrow/wide layouts. Keep native Markdown rather than converting text into images.

## Tables

Use a header, delimiter row and data rows. Use `:---`, `:---:` and `---:` for alignment; escape literal `\|`, including inside inline code. Prefer short cells; split long procedures into sections instead of forcing block content into a table. The checker flags differing body-row cell counts, which may be padded or truncated by GFM, as a **review warning**, not necessarily invalid syntax. Header syntax and visual overflow still need review. [GitHub tables](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-tables) · [GFM](https://github.github.io/gfm/)

## Collapsed sections

Use paired `<details>` tags with a descriptive `<summary>` and blank lines around inner Markdown. `open` expands by default. Do not hide the only install command, prerequisites, security warning or result. Audit missing/extra summaries and unmatched details; manually review summary wording, keyboard use and nested content. [GitHub collapsed sections](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections)

## Code blocks

Use fenced code with an appropriate language identifier; syntax coloring does not execute or validate the example. Wrap examples that contain triple backticks in a longer outer fence. Indent fences to match their list item. `diff` is a readable change example, not proof that a patch applies. Explicitly close fences: GFM permits implicit closure at a container/document end, so the helper's unclosed-fence warning is a readability safeguard. It does not check every Linguist identifier or execute code. [GitHub code blocks](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks)

## Diagrams

GitHub documents four native fenced formats: `mermaid`, `geojson`, `topojson`, and ASCII `stl`. Select by the information, not decoration. Mermaid fits relationships; GeoJSON/TopoJSON fit real geospatial data; STL fits a relevant 3D mesh. Preserve text explanations and label synthetic data. Check GitHub's Mermaid version with a separate `mermaid` block containing `info` before using version-sensitive syntax. [GitHub diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)

The helper checks map JSON and selected **top-level** members only; it does not validate nested geometry, coordinates, topology, arc references or geographic truth. GeoJSON positions use longitude before latitude; do not swap them when translating. TopoJSON is not simply a GeoJSON object renamed to `Topology`. STL checks only solid/facet/vertex boundary counts, not numbers, normals, closed surfaces, units or mesh quality. These remain manual/specialist checks. [GeoJSON specification](https://www.rfc-editor.org/rfc/rfc7946.html) · [TopoJSON specification](https://github.com/topojson/topojson-specification)

Keep Mermaid topology identical across localized labels and themes; prefer the host theme over hardcoded colors. If rendering is unavailable, retain the source and a prose explanation or clearly labeled static fallback. Do not call an offline SVG generator an AI image tool.

## Mathematical expressions

Use `$x^2$` or the protected inline form below. Display math uses paired `$$` or a `math` fence, not both. GitHub uses MathJax; do not assume every LaTeX package or custom macro is installed. Explain symbols and units in nearby text rather than an image. [GitHub mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)

```text
Inline: $`a^2 + b^2 = c^2`$
Dollar inside math: $`\$5`$
Literal dollar next to math: <span>$</span>10 and $10/2$
```

The checker finds extra `$$` wrappers in math fences and unmatched **standalone** `$$` lines. It deliberately does not guess whether an ordinary dollar amount is math, parse inline TeX, prove equations or certify MathJax output. Keep equations unchanged across translations unless a documented notation change is intended.

## Autolinked references

Issue/PR shorthand such as `#123`, `GH-123` and `owner/repo#123` is a conversation feature: GitHub does not create these autolinked references in repository files or wikis. Use explicit Markdown links there. A full URL being clickable is not the same as shorthand expansion. Discussions in lists, commit SHAs, same-repository label URLs and configured custom autolinks have additional rules; verify them on the target surface. Do not invent issue IDs, SHAs or external-ticket configuration. [GitHub autolinks](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/autolinked-references-and-urls)

The helper warns about issue/PR shorthand outside conversations, ignoring code examples and already-linked labels. It does not verify remote references or custom settings. A legitimate literal reference may still warrant manual review, not automatic rewriting.

## Attaching files

Distinguish a repository asset, an ordinary download link, and a GitHub-uploaded attachment. Browser attachment uploads happen immediately; authorization, redaction and destination visibility must be established **before** uploading. Use the actual returned URL, never a guessed attachment ID. Public-repository uploads are publicly accessible; private/internal access follows repository access. [GitHub attachments](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)

Link repository assets relatively, supply meaningful image alt text and a text alternative for video/animation. Verify current file-type, size and codec restrictions from GitHub rather than hardcoding a universal limit. The base audit checks local targets and image structure; it neither uploads files nor verifies remote attachment access, codecs or permissions. Opening a document to improve formatting does not authorize publishing its attachments.

## Task lists

Use ordinary `- [ ]` and `- [x]` lists. Tasklist **blocks** are retired; this does not retire Markdown checkboxes. Sub-issues are an authorized workflow alternative, not something a formatting edit may create silently. Issue-body tracking and interactive checkbox behavior are not guaranteed for repository documents. [GitHub tasklists](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/about-tasklists)

The helper flags retired `tasklist` fences and obvious malformed checkbox markers; it does not interact with GitHub task state. Keep completion status evidence-backed during translation or reformatting.

## Permanent code links

Use a full commit SHA and `#L10` or `#L10-L20` for stable code evidence. Confirm the file and range exist at that revision. Markdown source lines need `?plain=1` before the fragment. Snippet unfurling is limited to comments in the originating repository, not `.md` documents. [GitHub permanent snippets](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-a-permanent-link-to-a-code-snippet)

The helper warns about moving refs, malformed/reversed ranges and missing Markdown plain view for recognizable `github.com/.../blob/...#L...` URLs. It does not resolve SHAs, test authorization or verify snippets remotely. Links without a line fragment are not forced to use a pinned revision.

## Keywords and workflow effects

Closing keywords are `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`. They act in a PR description or commit message, not ordinary documentation. PR-description keywords are interpreted only when the PR targets the default branch; other targets ignore them. Commits close the referenced issue when merged into the default branch. Repeat the keyword for each issue and verify cross-repository targets. `Duplicate of #123` belongs in a new issue/PR comment. [GitHub keywords](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests) · [Linking PRs to issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

Use `--surface pull-request --pr-target default` only after actually checking the target; these are supplied observations, not API verification. The helper warns about inappropriate surfaces and unknown/non-default targets. It cannot prove workflow effects. Never publish a closing or duplicate marker merely to test rendering; inert code examples are safer.

## Related formatting

Also preserve relative/section links, explicit `<a name="...">` anchors, footnotes, alerts, inline HTML, line breaks and escaping. Footnotes do not work in wikis. Alerts use `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION` and cannot be nested in other elements; use sparingly. Color previews and mention notifications are conversation-specific, not portable page design. HTML comments are hidden visually, not private. [GitHub basic syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

Keep machine-readable frontmatter first. Do not inject CSS/JavaScript into GitHub Markdown. Use the existing theme, multilingual and verification references; new formatting never overrides their permission boundaries.
