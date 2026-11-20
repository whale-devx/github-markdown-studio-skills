# Formatting decisions and transformations

Read [advanced formatting](advanced-formatting.md) for syntax and surface constraints. These are project design rules, not new GitHub capabilities.

## Understand and select

Identify the reader's question, document type and destination before changing syntax. Read evidence behind facts, diagrams, equations and completion states. Keep `.md` pages, conversation bodies, commit messages, MDX and GitHub Pages distinct. Read the relevant topic only; do not load every reference or invoke every tool for a small edit.

## Generate and explain

Use the smallest useful format, explain why it helps, and preserve a readable text equivalent. Start from the bilingual showcase but replace synthetic examples with verified project content. Do not force maps, equations or 3D models into documents that do not need them. Preserve language, anchors, code, metadata, approved image identity and dark/light parity. Unknown host tools remain unavailable until confirmed.

## Transform without changing meaning

| Before | Appropriate transformation | Safety condition |
| --- | --- | --- |
| Repeated options in prose | Compact table | Same defaults, units and caveats; no lost cells |
| Long troubleshooting evidence | Details with a clear summary | Keep required actions/warnings visible |
| Interleaved commands and results | Labeled fenced blocks | Preserve commands; mark hypothetical output |
| Verified process in paragraphs | Mermaid plus prose | No invented edges; keep original order |
| Actual location dataset | GeoJSON/TopoJSON plus explanation | Preserve coordinate order and source provenance |
| Relevant mesh source | ASCII STL preview plus file link | Do not imply manufacturing validity |
| Dense formula in prose | Inline or display math | Same variables, units and assumptions |
| Bare issue number in a guide | Explicit verified link | No fabricated issue ID or cross-repo target |
| Moving code reference | Verified commit permalink | Resolve revision and lines before replacement |
| Informal action list | Ordinary task list | Do not mark unfinished work complete |
| PR prose with closing intent | Supported closing keyword | Explicit authorization and checked target branch |
| Attachment placeholder | Real local asset or returned upload URL | No implicit upload or exposure of private data |

Do not automatically rewrite intentional literal syntax or apply every warning's suggested fix. Preview the diff and keep edits limited to the requested files.

## Audit in layers

Run the offline audit only when the host can execute reviewed scripts. Select a rendering surface explicitly and record what was supplied versus verified. A warning-free report means only that implemented checks found nothing. Review semantics and unsupported grammar manually; use a real renderer when available. Keep `static`, `local-visual` and `github-preview` results separate.

For each changed format, inspect the live surface in both themes and a narrow viewport, expand details, inspect code wrapping, compare localized labels and follow navigation. If any capability is absent, state `blocked` or `not-run`. Never publish a test comment, upload a file, close an issue or call a paid service merely to satisfy an audit.

## Completion report

Record files, destination, source evidence, selected transformations, automated findings, manual review and unexecuted checks. Maintain translation hashes only after reviewing source and target together. Helper tests establish deterministic behavior, not agent quality, universal rendering or superiority over another skill.
