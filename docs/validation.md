# Validation record

[Home](../README.md)

This record separates actual local checks from planned integration work. It is not an agent benchmark or a claim of universal GitHub compatibility.

## Windows validation on 2026-11-21

### External-project authoring

A maintainer searching for a literal version and an operator repairing a
Python environment need different documents. One Codex desktop session
(26.1111.2228.0, Windows build 26200) explicitly used the skill to turn
parts of the ripgrep 15.2.0 and uv 0.8.12 manuals into two GitHub repository
pages. The [tasks and acceptance checks](../evals/authoring/protocol.md)
were fixed locally before the source passages were opened. Neither project
appeared in the skill's evaluation materials. Prior model familiarity with
these public projects is unknown. Skills CLI 1.9.0 installed the local
candidate at `9edf0e8` into a new Codex project. All 17 installed files
matched the source after line-ending normalization.

| Document | Observed outcome |
| --- | --- |
| [ripgrep reference](../evals/authoring/ripgrep-reference.md) | The default search returned one file. Including hidden files returned two. Both respected the ignore file and excluded the regex lookalike. The absent literal exited 1 with empty output. A missing path exited 2 and named the path on stderr. All five fixture files kept their hashes. |
| [uv recovery runbook](../evals/authoring/uv-runbook.md) | The diagnostic identified the missing package. The offline repair installed the expected pip wheel in the named maintenance environment. Rollback removed it. The adjacent application environment still lacked pip, and all of its files kept their hashes after both operations. An empty wheel directory failed before installation. |

Two deliberately edited copies showed why the commands matter. Dropping
`-F` also matched `v2x0`. Omitting `--python .maintenance` made uv's
install exit successfully while the maintenance environment still lacked
pip. Both controls used disposable fixtures.

To replay, have the two named tool versions on PATH and use a CPython
installation with a pip wheel bundled in `ensurepip`. Run this command from
the repository root.

```sh
python evals/authoring/replay.py
```

The [replay](../evals/authoring/replay.py) checks the fenced commands against
the reviewed argument lists and runs those lists on temporary files and
unactivated virtual environments. It uses the local wheel with networking
disabled in uv. It passed on Python 3.12.8 with pip 24.3.1 and Python 3.14.0
with pip 25.2. These results cover the documented commands on Windows.
Independent reader outcomes, other hosts, comparative quality and inference
cost were unmeasured.

### Decision table and transaction recovery

The [CSV reference](../evals/authoring/csv-triage.md) helps an importer
distinguish a blank cell from a missing column or surplus data. The
[SQLite runbook](../evals/authoring/sqlite-recovery.md) gives an operator
two choices after a deferred foreign key prevents a commit. The tasks were
fixed before opening the source manuals. Codex desktop used a fresh project
installation of the skill at `16f5445`. All 17 installed files matched the
Git tree after line-ending normalization. The author and evaluator shared
the task criteria. [Trial protocol](../evals/authoring/protocol.md#advanced-structures-on-two-external-tasks)

On Windows, CPython 3.12.8 with SQLite 3.45.3 and CPython 3.14.0 with
SQLite 3.50.4 each passed the three [example tests](../tests/test_authoring_examples.py).
The replay compared all four CSV rows with their decision-table entries
and ran the printed Python example. In two disposable databases the first
commit failed and the transaction stayed open. A second connection could
see only the earlier committed item. After repair it could read both items
on reopening. After rollback it could read only the original item. A separate
check confirmed that enabling foreign keys inside an open transaction had
no effect. To repeat, run `python tests/test_authoring_examples.py -v`.

Signed-out Edge 157.0.4341.60 opened both GitHub files at 360 × 800 and
1280 × 800 CSS pixels with light and dark preferences. In the original
four-column reference, the narrow table needed 185 pixels of horizontal
scrolling to expose the final decision. The table took keyboard focus and
Right Arrow reached that column. The revised table keeps each parsed value
beside its import decision. All four rows fit at both widths with zero
horizontal scroll. [Original table](https://github.com/whale-devx/github-markdown-studio-skills/blob/3ea655d7af4e340186a284db5c4a9c981d508088/evals/authoring/csv-triage.md) · [Revised table](https://github.com/whale-devx/github-markdown-studio-skills/blob/af401f3ebb00727ce6e8b9c65c516dfc30dada6d/evals/authoring/csv-triage.md)

In all eight revised views, Tab reached the disclosure, Enter opened its
sample and Space closed it. The SQLite alert and both recovery choices
were outside the disclosure. These observations cover the GitHub repository
file view. Independent reader outcomes and screen-reader and touch interaction
remain unmeasured. [Rendered runbook](https://github.com/whale-devx/github-markdown-studio-skills/blob/af401f3ebb00727ce6e8b9c65c516dfc30dada6d/evals/authoring/sqlite-recovery.md)

### Replay the Mermaid diagrams

The [renderer check](../evals/render_mermaid.py) reads the Mermaid fences directly
from the architecture page and the English and Thai showcases. From the repository
root, install the audit dependencies described in [Contributing](../CONTRIBUTING.md),
then preload the pinned [Mermaid CLI image](https://github.com/mermaid-js/mermaid-cli).

```sh
podman pull ghcr.io/mermaid-js/mermaid-cli/mermaid-cli@sha256:18938e53497376d524e04b1fc0bf7b6d61a491ce9ff7032bb2855d57155acb10
python evals/render_mermaid.py
```

The check streams one fence into each disconnected container. It checks the exported
SVG for node labels, directed edges, and a linked accessible title and description
matching the source. It runs the default and dark themes. Docker users can pull the
same digest with Docker and pass `--engine docker` to the script.

On 2026-11-21 the original three exports had nodes and arrows but lacked both
accessible text references. After adding localized descriptions, all six exports
passed on Linux amd64 under Podman. The architecture diagram had 11 nodes and 12
arrows. Each showcase had three nodes and two arrows. The image reported Mermaid
CLI 12.0.0, Mermaid 12.2.0 and Chromium 156.0.8078.79. Screen reader behavior
still needs a separate trial.

### Live diagram viewers in the English and Thai showcase

On 2026-11-21 a signed-out Edge 157.0.4341.60 session opened the
[English](https://github.com/whale-devx/github-markdown-studio-skills/blob/f2232810ed65da3bbdc63041fa72fae5d3a4ba47/examples/advanced-formatting.en.md)
and [Thai](https://github.com/whale-devx/github-markdown-studio-skills/blob/f2232810ed65da3bbdc63041fa72fae5d3a4ba47/examples/advanced-formatting.th.md)
repository files. To repeat, open each file in a fresh context at 360 × 800
and 1280 × 800 CSS pixels, with light and dark color preferences. Scroll each
diagram into view. Inspect the viewer contents and controls inside each frame.

| Viewer | Observations in all eight contexts |
| --- | --- |
| Mermaid | The three localized labels and two connecting edges rendered. At 360 px GitHub controls partly covered the final node. The examples now include the sequence in the surrounding text. |
| GeoJSON and TopoJSON | Both showed one pin over open water. Wait for the map's accessible location to say “Atlantic Ocean” before taking screenshots. The canvas appeared earlier than the pin. |
| STL | The solid view displayed a triangular face. Focusing the Wireframe radio and pressing Space selected it. Automated pointer selection did not complete within 2.5 s. On the initial narrow trial, GitHub's overlay intercepted pointer events. |

These 32 viewer observations concern the pinned repository files. Held-out
reader tasks, other GitHub surfaces and physical touch interaction remain open.

### Issues, pull requests, comments and commit messages

On 2026-11-21 (Bangkok), Playwright opened five existing public pages or
comment anchors in signed-out Edge 157.0.4341.60. Each example was checked
at 360 × 800 and 1280 × 800 CSS pixels with both light and dark preferences.
The table records what a reader could reach from each example.

| Source | What to check when repeating the trial |
| --- | --- |
| [Issue 10](https://github.com/whale-devx/github-markdown-studio-skills/issues/10) | The description had three section headings. Focusing the roadmap link and pressing Enter opened the repository's roadmap file. |
| [PR 12 description](https://github.com/whale-devx/github-markdown-studio-skills/pull/12#issue-6518198188) | The verification list had four items. The inline code `f223281` stayed plain text. Enter on the linked issue number opened issue 10. |
| [PR 3 verification table](https://github.com/whale-devx/github-markdown-studio-skills/pull/3#issue-6513051408) | Two headers and six data rows rendered. At 360 px the table had 195 px of horizontal scroll. Starting at the heading, Tab focused the table and Right Arrow scrolled it in both themes. Scrolling to the end revealed the full tree hash. At 1280 px the table fit. |
| [PR 3 comment](https://github.com/whale-devx/github-markdown-studio-skills/pull/3#issuecomment-7041652793) | The two job names formed a list. The commit hash in inline code stayed plain text. Enter on the Quality run link opened run 44750747500 and its two-job summary. |
| [Commit f223281](https://github.com/whale-devx/github-markdown-studio-skills/commit/f2232810ed65da3bbdc63041fa72fae5d3a4ba47) | In the merge subject, Enter on the linked PR number opened the onboarding PR. |

The page width matched the viewport in all 20 cases. For a separate offline
check, save each original body as UTF-8 and run `audit.py` with the matching
`--surface`. Both PRs targeted `main`, so their checks also used
`--pr-target default`. All five inputs returned zero findings.

### Public Wiki and Discussion examples

Discussions were disabled in this repository, and its public wiki URL
redirected to the repository home. Two published upstream examples provided
the same four signed-out theme and viewport combinations.

- On the original GitHub CLI Discussion post, both command names were inline
  code inside links. Enter on `gh api` opened the CLI manual with the matching
  heading in all four cases. [Discussion 2618](https://github.com/cli/cli/discussions/2618)
- On the pinned VS Code wiki page, the source links to the **current** page's
  Node version heading. Enter opened that URL with the expected fragment in
  all four cases. The heading existed, but it stayed below the viewport for
  the five-second observation window, including after reload. Starting from
  the current page also left the heading outside the viewport in all four
  combinations. Check where the heading lands before reporting that a reader
  can jump to it.
  [Pinned wiki page](https://github.com/microsoft/vscode/wiki/How-to-Contribute/6217f0572bd6d5d101f393765f2d175a901bff16)

The strict offline checks on the original Discussion body and wiki Markdown
both returned zero findings. Together with the repository-file checks above,
these trials cover examples on all seven named surfaces. The wiki jump remains
a failed navigation check. Physical touch and actions that change issue state
remain untested.

### Explicit desktop edit

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

The Windows entries above cover installation, explicit host use and the four live diagram viewers in two themes. Project-only discovery, remote link availability, host image generation, native review of additional languages and comparative agent benchmarks remain open.

The Arabic renderer test is a structural smoke test, not native linguistic or visual approval. English and Thai examples were reviewed as authored content, not certified by an independent translation reviewer.
