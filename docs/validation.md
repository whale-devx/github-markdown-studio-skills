# Validation record

[Home](../README.md)

This record separates actual local checks from planned integration work. It is not an agent benchmark or a claim of universal GitHub compatibility.

## v0.3 advanced-formatting validation (2026-11-20)

Executed against this development change with Python 3.13.5, markdown-it-py 4.2.0 and PyYAML 6.0.3. No dependency was added.

| Check | Actual result |
| --- | --- |
| Full regression suite | 131 tests passed (74 previous and 57 added) |
| Strict repository audit | 20 Markdown files, 0 errors, 0 warnings |
| English/Thai code/data parity | Passed for executable, math, GeoJSON, TopoJSON and STL fences |
| Translation snapshots | README pair and new showcase pair synchronized after author review |
| Coverage inventory | All ten official topics have sources, bilingual anchors, rule IDs and manual limits |
| Existing visual assets | Regenerated offline; identical to the baseline Git files |

Negative and false-positive cases cover every new diagnostic family, surface differences, all nine closing keywords, nested fences/details, table pipes, malformed map types, mathematical delimiters, retired tasklist blocks, code-line links, alerts, footnotes and inert code/comments. CLI tests check strict exit status and that audited files are unchanged.

**Not run for v0.3:** live GitHub rendering, local visual review of the new showcases, Mermaid/MathJax/map/STL rendering, upload/issue workflow effects, external URL checks, installation or activation in actual agents, and comparative model evaluations. The pre-existing browser results below are historical, not validation of these new pages. English/Thai text was reviewed as authored content, not by an independent language reviewer. Static footnote handling is a prose approximation, not a complete footnote parser.

## Historical v0.1/v0.2 local checks

| Check | Result | Scope |
| --- | --- | --- |
| Python regression suite | 74 tests passed | Markdown links and HTML, path boundaries, skill metadata, translation drift, SVG generation and overwrite protection |
| SVG variants | Four generated and parsed | English/Thai, light/dark |
| Theme pair consistency | Passed | Identical geometry and text for each locale; palette-only differences |
| Palette contrast | Passed | Tested text/background pairs are at least 4.5:1; not a full accessibility certification |
| Local browser preview | Eight combinations passed | English/Thai × light/dark × 360/1280-pixel viewports |
| Picture source selection | Passed in local preview | The chosen image bytes match the requested theme and locale |
| Document width | No page-level horizontal overflow in local preview | Code and table containers may scroll as intended |
| SVG text bounds | Four variants passed | Text stayed within the SVG canvas in the local browser |
| Visual inspection | English light and Thai dark inspected | Legible labels and consistent four-step composition |

Local environment: Python 3.13.5, markdown-it-py 4.2.0, PyYAML 6.0.3, Chromium 144.0.7559.96 and Playwright 1.57.0. Browser previews used locally rendered Markdown and in-memory copies of generated SVGs. They did not use GitHub's renderer; navigation to local URLs was restricted in the execution environment.

## Additional provider-neutral checks (v0.2.0 development)

The local suite now includes **16 extra preflight tests** (74 total) for agent-label invariance, unknown vs false, read/write boundaries, AI imagery without an image tool, matched AI image editing, SVG/Mermaid fallback, local vs live GitHub preview, malformed inventories and CLI execution. These tests use simulated host capabilities and standard Python only. **They do not run Codex, Claude Code, Gemini CLI, Cursor or any other agent**, and do not prove that a host can discover or activate this skill.

The preflight is deliberately host-supplied. Every task's execution status stays `not-run` even when its prerequisites are marked `ready`. Installing with a provider's CLI is still a separate verification step.

## Reproduce the deterministic checks

```bash
python -m pip install -r skills/github-markdown-studio/scripts/requirements.txt
python -m unittest discover -s tests -v
python skills/github-markdown-studio/scripts/capability_plan.py --input examples/host-capabilities.json
python skills/github-markdown-studio/scripts/audit.py . --translations i18n-manifest.json --strict
python skills/github-markdown-studio/scripts/render_diagram.py examples/workflow.json --output /tmp/studio-assets
```

The browser review is a local development check, not part of the bundled regression suite. The GitHub Actions workflow is configured for Python 3.10 and 3.13; a workflow configuration is not proof that a remote run has passed. Dependency ranges allow compatible minor updates, so record the resolved versions when reproducing a result.

## Not yet verified

Actual `npx skills` installation and invocation in an agent; actual GitHub light/dark rendering; live Mermaid rendering; remote link availability; image generation through an AI model; native review of additional languages; comparative agent benchmarks. Local CLI installation was not executed because the environment could not reach GitHub/package services and its Node.js 22.16.0 is below the current Skills CLI's documented 22.20 minimum.

The Arabic renderer test is a structural smoke test, not native linguistic or visual approval. English and Thai examples were reviewed as authored content, not certified by an independent translation reviewer.
