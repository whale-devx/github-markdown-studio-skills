# Changelog

## Unreleased

- Count visible text when checking SVG label widths so RTL labels can isolate command-line flags at the column limit.
- Preserve the SVG manifest's byte hashes when writing files on Windows.
- Ignore footnote examples inside inline code when auditing wiki Markdown.
- Exercise Windows in CI and document a live bilingual GitHub showcase check and a Copilot CLI audit.

## 0.3.0 (in development) — advanced formatting

Source-backed coverage of all ten GitHub advanced-formatting topics; Mermaid, GeoJSON, TopoJSON and ASCII STL examples; English/Thai showcases; transformation guidance and a machine-readable coverage inventory. The offline audit adds explicit surface/PR-target context and bounded structure checks while preserving provider neutrality. A footnote-reference guard fixes false local-link errors for single-word definitions. Live rendering and workflow effects remain unverified.

The `improve` workflow now asks editors to identify a reader difficulty and review what the reader loses when a passage is cut. See the [editorial review questions](skills/github-markdown-studio/references/verification.md#review-an-editorial-diff).

## 0.2.0 (in development) — portable agent execution

Standard Agent Skills workflow across compatible hosts, capability-based dispatch, explicit `true`/`false`/`unknown` inputs, conservative fallback for absent image/browser tools, installation guidance and provider-invariance regression tests. No provider SDK or agent-specific fork added. CLI install/activation and cross-provider end-to-end verification remain untested.

## 0.1.0 — initial implementation

One skill for GitHub repository Markdown, with document-specific writing guidance, light/dark visual pairing, multilingual workflows, honest host image-generation instructions, an offline audit helper, a deterministic SVG renderer, English/Thai examples, regression tests and an evaluation plan.

This is not a tagged release or a comparative benchmark result. Consult the [validation record](docs/validation.md) for what has actually been exercised.
