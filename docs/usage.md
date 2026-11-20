# Usage

[Home](../README.md)

## Install and invoke

The repository contains one installable skill at `skills/github-markdown-studio/`. Use the Skills CLI or copy that entire directory into a location supported by your agent. Copying only `SKILL.md` omits its references, templates and optional scripts.

From a development checkout:

```bash
npx skills add . --list
npx skills add . --skill github-markdown-studio
```

The CLI downloads its own package if needed; it needs network access and its documented Node.js version. CLI installation is separate from Python helper dependencies. The skill format is portable, but individual agent activation, image tools and browsers depend on the host and have not all been tested here.

If you already installed the skill globally from GitHub, update that copy with the following command. For a project installation, use `-p` in the project directory.

```bash
npx skills update github-markdown-studio -g -y
```

Request a scope and outcome, such as:

```text
Audit docs/architecture.md without changing files.
Check factual support, links, diagram readability and light/dark behavior.
```

```text
Create an English and Thai getting-started guide from the implementation.
Keep commands identical. Add an explanatory diagram only if it improves understanding.
```

## Provider-neutral installation and preflight

The same skill files are used for all compatible clients. Select a target with the Skills CLI's documented `-a` IDs; do not edit `SKILL.md` to change models. Examples below illustrate installation syntax, **not verified activations**:

```bash
npx skills add . --skill github-markdown-studio -a codex
npx skills add . --skill github-markdown-studio -a claude-code
npx skills add . --skill github-markdown-studio -a gemini-cli
```

For hosts without built-in skills discovery, supplying the text and relevant references is possible, but automatic activation is not established. A chat-only model cannot inspect or edit a repository without file tools. See [agent portability](../skills/github-markdown-studio/references/agent-portability.md) and the upstream [supported-agent list](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).

Optional preflight with an explicit example inventory (no provider API or automatic tool discovery):

```bash
python skills/github-markdown-studio/scripts/capability_plan.py --input examples/host-capabilities.json
```

All returned tasks have `execution: not-run`; `ready` is a declared prerequisite check only. `false` blocks a required capability and omitted/null values stay unverified. Never invent an image, browser check or execution result to satisfy a missing tool. Python is unnecessary for the skill's general writing instructions; if no Python runtime is available, skip this helper entirely.

## Advanced formatting and target surfaces

Read the [formatting guide](../skills/github-markdown-studio/references/advanced-formatting.md), [transformation patterns](../skills/github-markdown-studio/references/formatting-patterns.md) and [English](../examples/advanced-formatting.en.md)/[Thai](../examples/advanced-formatting.th.md) examples. Every topic has known automated/manual boundaries in the [coverage inventory](../skills/github-markdown-studio/assets/formatting-coverage.json).

```bash
python skills/github-markdown-studio/scripts/audit.py . examples/advanced-formatting.en.md --surface repository --strict
python skills/github-markdown-studio/scripts/audit.py . path/to/pr-body.md --surface pull-request --pr-target default --json
```

The second command illustrates a user-provided PR-body file, not one shipped here. `--pr-target default` must reflect an actual check, not an assumption. The helper never contacts GitHub, uploads attachments, creates sub-issues or closes issues. Default destination is `repository`; choices also include `issue`, `pull-request`, `discussion`, `wiki`, `comment`, and `commit-message`. Relative links outside repository documents are marked for surface review rather than incorrectly resolved against local files.

Warnings are conservative authoring diagnostics, not a full grammar verdict. Map checks inspect JSON and selected top-level members only. STL checks boundary counts only. Math checks selected delimiters, not equations or TeX macros. Footnote definitions are kept as prose rather than mistaken for link URLs; full multi-block footnote grammar is not implemented. Unsupported rendering and workflow verification always remain `not-run`. No new package or model API is required.

## Run the audit helper

From this repository's root:

```bash
python -m pip install -r skills/github-markdown-studio/scripts/requirements.txt
python skills/github-markdown-studio/scripts/audit.py . README.md docs --json
python skills/github-markdown-studio/scripts/audit.py . --translations i18n-manifest.json --strict
```

For a different target repository, use the absolute path to the installed skill's script and pass that target as `root`. Scope paths and the optional manifest are relative to the target root. Standard output may be redirected to a chosen report file. The helper does not write files, contact URLs or execute examples.

Exit codes: `0` means no fatal findings under the selected policy; `1` means errors, or warnings with `--strict`; `2` means command usage failed. A zero exit code is not proof of factual correctness, accessibility or actual GitHub rendering. JSON records those separate checks as `not-run`.

## Translation review snapshots

`i18n-manifest.json` tracks a reviewed source/target pair with SHA-256 hashes of the original bytes. After reviewing source changes and updating the translation, calculate both hashes and update the corresponding entry. Do not regenerate hashes to hide untranslated changes.

```bash
python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('README.md').read_bytes()).hexdigest())"
```

Executable code fences are compared, while plain text and Mermaid labels may be localized. This is structural review assistance, not translation-quality certification.

## Generate explanatory images offline

The supplied process-card renderer reads a localized JSON specification and produces matching light/dark SVG files plus a provenance manifest:

```bash
python skills/github-markdown-studio/scripts/render_diagram.py examples/workflow.json --output /tmp/studio-assets
```

It supports 2-8 short steps, declared language tags and `ltr`/`rtl` direction. It uses no image model and no network. Keep SVGs as image files; do not paste their markup directly into GitHub Markdown. Review labels, shaping and meaning before publishing.

For generative illustrations, the agent follows the [visual workflow](../skills/github-markdown-studio/references/visual-explanations.md) and [brief template](../skills/github-markdown-studio/assets/image-brief.template.json). This version intentionally does not ship a billed provider integration or ask for an API key.

## What the checks do not cover

Remote HTTP availability, exact GitHub slug generation, every HTML/Markdown extension, SVG security, pixel contrast in arbitrary images, Mermaid syntax/rendering, linguistic quality, application behavior, and runtime support across every platform need separate checks. See [verification guidance](../skills/github-markdown-studio/references/verification.md).
