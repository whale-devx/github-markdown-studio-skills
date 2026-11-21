# Multilingual documentation

## Policy before translation

Read existing locale conventions. Define the canonical source only when the repository lacks one; do not assume the chat language is the source. Translate only the requested languages and paths. Use language labels such as English, ไทย, 日本語, العربية, not flags.

The starter repository demonstrates English and Thai. Other languages can use the same workflow and locale schema, but their linguistic quality, glyph coverage, line breaking and reading order still require review. Do not advertise all languages as tested.

For a few introductory pages, `README.md` and `README.th.md` are sufficient. For a larger corpus, retain the existing layout or use linked locale directories. Do not migrate a working structure just to match this example. Language selection is explicit navigation; GitHub Markdown does not automatically translate the page.

## Preserve contracts

Translate explanations, captions, alt text and user-facing diagram labels. Preserve command names, flags, file paths, environment variables, API identifiers, frontmatter keys, versions and literals whose exact value matters. Localize code comments only when appropriate and review any difference in executable examples. Avoid translating a canonical `SKILL.md` into an incompatible machine contract.

Keep a glossary of approved terms and non-translatable identifiers. Prefer natural domain language over literal word substitution. Check that warnings, defaults, constraints and feature maturity retain their original meaning.

## Drift manifest

The optional root-relative manifest has version 1 and a translations array. Each entry contains `source`, `target`, `language`, `source_sha256`, and `target_sha256`. Hash the exact UTF-8 file bytes after a translation has been reviewed. This metadata records a review snapshot, not semantic proof of translation quality.

A changed source produces `TRANSLATION_STALE`. A changed target produces `TRANSLATION_REVIEW`. Different fenced executable/configuration examples produce `TRANSLATION_CODE`. These are review signals; examples containing intentional localization may differ legitimately.

Never refresh hashes just to make a check green. Review the source diff, update the target, verify navigation and examples, then record new hashes. For CI, `--strict` makes drift warnings fail the command. Audit mode never writes the manifest.

## Visual localization

Use a single canonical diagram topology and translate labels into locale-specific assets. Keep theme variants derived from that locale's same layout. Prefer short labels and a text explanation outside the image. For RTL, inspect text direction, numbering, arrows, mixed Latin identifiers and alignment. Do not mirror a causal flow without checking its meaning.

The bundled SVG renderer accepts locale tags and an explicit `ltr` or `rtl` direction, but it is a fixed process-card layout, not a universal typography engine. It rejects long labels rather than silently clipping them. Browser/font review is still necessary.

In an RTL label, isolate a left-to-right command-line option so its leading
hyphens stay on the left. Write the Unicode escapes directly in the diagram
JSON. This step keeps the flag visible as `--output`.

```json
{"title":"حفظ التقرير","detail":"استخدم \u2066--output\u2069 لحفظ التقرير."}
```

`\u2066` begins the left-to-right span and `\u2069` ends it. The renderer
preserves both characters in the SVG and excludes them from the label width.
Check a rendered asset in both themes when punctuation carries meaning.
[W3C guidance on direction isolates](https://www.w3.org/International/questions/qa-bidi-unicode-controls.en)
