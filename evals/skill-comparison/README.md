# Compare README and diagram authoring

This exercise compares two skills on the same README request and two skills
on the same Mermaid request. The common source is the ISC-licensed
[`github-slugger` 2.0.0 module](https://github.com/Flet/github-slugger/tree/3461c4350868329c8530904d170358bca1d31448).
The [guide, reference and runbook packets](../reader-tasks/README.md) cover
separate reading tasks with original documentation as the baseline.

| Task | Markdown Studio | Specialist |
| --- | --- | --- |
| Package README | [GitHub Markdown Studio](https://github.com/whale-devx/github-markdown-studio-skills/tree/f2232810ed65da3bbdc63041fa72fae5d3a4ba47/skills/github-markdown-studio) | [GitHub Awesome Copilot's `create-readme`](https://github.com/github/awesome-copilot/tree/f10fdb8b2660ce85c98f220b2f1ca24653768a5c/skills/create-readme) |
| Algorithm flowchart | Same Markdown Studio revision | [Softaworks' `mermaid-diagrams`](https://github.com/softaworks/agent-toolkit/tree/3027f20f3181758385a1bb8c022d4041dfb4de84/skills/mermaid-diagrams) |

## Prepare the inputs

From the repository root, run the following with Python 3.10+, Git and an
existing parent directory. Preparation fetches the pinned public Git objects
and four README examples from GitHub. It prints the newly created directory.

```sh
python evals/skill-comparison/prepare.py <parent-directory>
```

Each `<task>/<skill>/project` is a fresh Git repository with the same four
source files (`index.js`, `regex.js`, `package.json` and `LICENSE`) and one
project-local skill under `.agents/skills/`. The skill's upstream license is
beside the project. Both README workspaces include the four examples referenced
by the specialist and their licenses, at fixed revisions in the adjacent
`examples/` directory. The source project's original README, participant
packets and grading materials stay outside every author workspace.

## Give both authors the same request

**README**

> Write README.md for a JavaScript developer integrating this package into a
> table of contents for several documents. Show a runnable import and usage
> example. Help the reader choose an API for repeat headings and explain
> what to do when starting another document. Use the package source for
> claims. You may consult the four style examples in ../examples/.

**Diagram**

> Write flow.md containing one Mermaid flowchart and a short text equivalent
> for a maintainer tracing the instance method that creates a heading slug.
> Show how the method reaches a return value when generated names collide,
> including a collision with an already suffixed heading. Derive the diagram
> from the supplied implementation.

## Run and score

1. Use a fresh session and private workspace for each arm. Expose only that
   arm's project and its supplied examples. Explicitly select its assigned
   skill. Fix the model revision, reasoning setting, tools and renderer for
   both authors within each task. Allow one author turn, up to ten minutes
   and 2,000 output tokens per arm. Give both the same local Node runtime.
   Start timing at prompt submission. Record tool use, elapsed time, actual
   token usage, cost if available, and any timeout or unavailable limit.
2. Freeze the four outputs before scoring. The facilitator can test the
   README examples against the pinned module in a disposable ES module
   project and render both diagrams with the same Mermaid version. Compare
   the account of collisions against actual calls to the source, including
   a literal suffixed heading followed by repeated unsuffixed headings.
   Record the observed output and rendering errors.
3. Remove author and skill labels from the rendered materials. Assign each
   independent reader one version per task under a neutral ID. For a README,
   ask the reader to choose between the stateless and instance APIs and to
   handle a second document. For a diagram, ask the reader to trace a
   collision and identify when state changes. Set the precise inputs,
   expected answers and time allowance before assignment. Keep the mapping
   and grading key with the facilitator until scoring is complete.
4. Report correct decisions, failures, missing observations and elapsed
   times separately by task and arm. Record prior exposure to these public
   materials. Use fresh cases for previously exposed participants. An unknown
   cost or token count stays unknown.

## Input verification on 2026-11-21

Windows and Linux produced byte-identical content for all 80 files across
the four arms, excluding Git internals. The four source files and each copy
of the three skills matched their upstream Git blobs. In disconnected Linux
containers, Codex CLI 0.164.0 discovered exactly the assigned repo-scoped
skill in each project. Empty controls contained none of those skills.

Node 24.19.0 loaded the supplied source through its package name. For the
successive inputs `API`, `API-1`, `API`, `API`, one instance returned
`api`, `api-1`, `api-2`, `api-3`. After reset it returned `api` again.
Two calls to the stateless function both returned `api`. No author turn or
independent reader session ran during input verification. Comparative
quality, time and cost remain unmeasured.
