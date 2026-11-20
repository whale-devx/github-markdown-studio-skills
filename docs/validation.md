# Validation record

[Home](../README.md)

This record separates actual local checks from planned integration work. It is not an agent benchmark or a claim of universal GitHub compatibility.

## Follow-up on the first-run guide, 2026-11-21

Codex desktop 26.1111.2228.0 on Windows explicitly used GitHub Markdown Studio
in maintainer mode with the [first-run fixture](../evals/first-run-guide.json)
from `f223281`. In a temporary directory the agent inspected both inputs,
retained the original prerequisite and command, and appended one sentence
giving the expected output as `Ready`. Running the fixture's Python command
printed exactly `Ready`. The script's SHA-256 stayed unchanged, and the
original guide remained an exact prefix of the edited guide. The strict audit
of the edited file reported one file, zero errors and zero warnings.

The evaluator could see the rubric. This is a repeatable explicit-edit
observation. Blinded reader trials, project-only discovery and the blocked
Copilot CLI edit trial are still open.

## Windows beta-readiness check (2026-11-20)

The starting revision was `785bf30`. On Windows with Python 3.12, the original 131-test suite had three errors: one locale-dependent read of a Thai fixture and two attempts to create symlinks without the Windows privilege. After the fixes, 133 tests ran, 131 passed and only the two privilege-dependent cases skipped locally. SVG regeneration matched the tracked assets byte for byte. The new on-disk digest test covers Windows newline conversion.

### Fresh project installation and runtime

In a temporary Git repository, Skills CLI 1.9.0 installed the checkout with `npx skills add <checkout> --skill github-markdown-studio -a codex -a claude-code -a github-copilot -y`. It reported universal installation for Codex and GitHub Copilot and a link for Claude Code. Each client received the same skill. A user-level copy was also present, so the successful invocation does not isolate project discovery from global discovery.

| Windows host | Explicit invocation and file access | Result |
| --- | --- | --- |
| GitHub Copilot CLI 1.0.44 | The trace showed skill activation and reads of both fixture files. It identified the missing output as `Ready`. The read-only run reported zero edits. | Audit passed. A subsequent edit run was blocked during model credential lookup. |
| Codex CLI 0.164.0 | Both model requests were rejected by the account before the guide task ran. | Fresh CLI execution blocked. The earlier explicit Codex desktop use is recorded below. |
| Claude Code 2.1.161 | The client returned HTTP 401 for expired OAuth credentials before the task ran. | Runtime blocked. |

To reproduce the audit, create `hello.py` containing `print("Ready")` and a one-line guide containing “Prerequisite: Python 3.10+. Run `python hello.py`.” Ask the client to use the skill to audit the guide against the script and report the missing expected output. Check the activation trace, the answer and the unchanged files. For the edit trial, request the expected output in the guide and verify the prerequisite and command survive. Automatic activation and optional image/browser tools inside these CLI clients remain unverified.

### Live GitHub showcase inspection

Edge 157.0.4341.60 opened both [English](https://github.com/whale-devx/github-markdown-studio-skills/blob/785bf30485ed01e32ef03774583fe841b8e140c3/examples/advanced-formatting.en.md) and [Thai](https://github.com/whale-devx/github-markdown-studio-skills/blob/785bf30485ed01e32ef03774583fe841b8e140c3/examples/advanced-formatting.th.md) on github.com. Playwright used fresh signed-out contexts with light/dark OS preferences and viewport widths of 360 and 1280 pixels, height 800. All eight pages returned HTTP 200. Each rendered article had one table, five details elements and ten preformatted blocks. Clicking the first summary opened its details. The picture loaded the matching locale/theme SVG at intrinsic width 640 in every context.

The article DOM also contained one alert, a footnote reference, two checkboxes, two pinned line links, six math elements and four diagram frames per page. These counts verify the surrounding markup. Inspect the interactive Mermaid, map and STL contents, highlighting, line navigation and mobile readability separately before claiming visual acceptance. These observations apply to repository files at the linked revision. Other GitHub surfaces and comparative reader evaluations remain outstanding.

## Global skill update on Windows (2026-11-20)

Ran `npx skills update github-markdown-studio -g -y` against an existing installation. The CLI reported one updated skill. The installed entry point matched the repository text at `9a966ad`, and the installed references contained the new editorial review guidance. This exercised an update followed by explicit use in Codex. Fresh installation and automatic discovery remain separate checks.

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

## Outstanding checks after the dated runs

The Windows entries above cover installation, explicit host use and the GitHub showcase in two themes. Project-only discovery, interactive diagram contents, remote link availability, host image generation, native review of additional languages and comparative agent benchmarks remain open.

The Arabic renderer test is a structural smoke test, not native linguistic or visual approval. English and Thai examples were reviewed as authored content, not certified by an independent translation reviewer.
