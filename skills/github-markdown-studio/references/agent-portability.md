# Agent and provider portability

## One skill, any compatible loader

The source of truth is a standard [Agent Skills](https://agentskills.io/specification) directory: `SKILL.md`, relative references, optional scripts and assets. There is no dependency on an OpenAI, Anthropic, Google, xAI, DeepSeek, Qwen or other model SDK, API key or service. The **model provider** produces inference, while the **agent host** controls skill discovery, file access, browser and image tools. These layers must not be conflated.

Use only portable frontmatter and instructions. Do not require vendor-only `context: fork`, hooks, implicit subagents, proprietary tool names or `allowed-tools` permissions. A skill does not grant permission to execute commands, upload data, install dependencies or buy API services.

**Design portability is not runtime certification.** A host without Agent Skills support can read the skill text if the user explicitly supplies it, but may lack automatic discovery. A chat-only model without repository access cannot claim to audit or change real files.

## Observe capabilities, not provider names

Before choosing a method, inspect the host's actually exposed tools and permissions. Represent each capability as **true, false or unknown**. Unknown is not permission. Capabilities may change by session, product plan, device or organization even under the same model.

| Capability | Required evidence | When unavailable |
| --- | --- | --- |
| `read_files` | Working repo file reads | Only review content supplied to the conversation |
| `write_files` | Authorized repo file writes | Draft a patch; don't claim it was applied |
| `run_commands` | Authorized shell/process tool | Skip command-based validation |
| `python` | Compatible runtime in the execution host | Use instructions and manual review, not Python scripts |
| `image_generate` | An actual image-generation tool | Mark AI imagery blocked; don't relabel SVG or a prompt |
| `image_edit` | Tool that edits a reference image | Don't claim independently generated variants match |
| `browser` | Actual preview or browser capability | Only static checks; no screenshots |
| `network` | Authorized access to GitHub/remote URLs | No claims of live link or GitHub rendering checks |

For a requested AI illustration, no image tool means **blocked**. Offer a clearly labeled diagram alternative only if acceptable. Dark/light pairs must preserve topology and identity; offline SVG is useful for deterministic diagrams, not a replacement for AI image editing. Drafts in additional languages require review, including terminology and RTL shaping.

## Offline capability preflight

The optional [`capability_plan.py`](../scripts/capability_plan.py) takes an inventory **supplied by the host or user** and recommends methods. It does not auto-detect agents or tools, run tasks, access the network or use model APIs:

```bash
python skills/github-markdown-studio/scripts/capability_plan.py --input examples/host-capabilities.json
```

See the [example inventory](../../../examples/host-capabilities.json). A `ready` status only means prerequisites were reported available. The tool always sets `execution: not-run`; verify permissions and actual results separately.

## Install across agent hosts

The [Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) documents a shared installer with a [supported-agent list](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) including Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode, Windsurf, Cline and Roo Code. These are **installer targets**, not verified end-to-end runs of this repository.

```bash
npx skills add whale-devx/github-markdown-studio-skills --list
npx skills add whale-devx/github-markdown-studio-skills --skill github-markdown-studio -a claude-code
npx skills add whale-devx/github-markdown-studio-skills --skill github-markdown-studio -a gemini-cli
```

Omit `-a` for interactive agent selection, or use `-g` for user-level installation. Installing from a repository targets the default branch; use a local checkout or pinned revision for unmerged work. Tool permissions and the host's activation mechanism remain host-specific.

## Verification ledger

Test each host independently: skill discovery, installation, activation, repository read/write, optional image/browser abilities and an end-to-end documentation edit. Record client versions, permissions, pass/fail/blocked/not-run and links to evidence. Never infer actual image support from the model name, or agent activation from CLI installation. Automated provider-invariance tests of the offline planner are **not** native execution tests for different providers.

See [validation](../../../docs/validation.md) and [roadmap](../../../docs/roadmap.md).
