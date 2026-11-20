# Use this skill with your agent

Run this in the project where you want the skill. Replace TARGET with one value from the table.

```sh
npx skills add whale-devx/github-markdown-studio-skills --skill github-markdown-studio --agent TARGET
```

| Host | TARGET | Project directory observed with Skills CLI 1.9.0 |
|---|---|---|
| Codex | codex | .agents/skills |
| Claude Code | claude-code | .claude/skills |
| Cursor | cursor | .agents/skills |
| Gemini CLI | gemini-cli | .agents/skills |
| Kiro CLI | kiro-cli | .kiro/skills |

Validation on Windows used a temporary project and the repository checkout as the source, with all five targets selected and copy mode enabled. The installer produced the skill in the three directories above. This checks installation only. Live activation and task completion require separate tests in each host. Kiro IDE was not tested.

## Upgrade or restore a project-local copy

These steps apply to a Codex project installed with Skills CLI 1.9.0 and
`--copy`. From the project root, read the entry for this skill.

```sh
python -c "import json; from pathlib import Path; entry=json.loads(Path('skills-lock.json').read_bytes())['skills']['github-markdown-studio']; print(entry['source'], entry.get('commit'))"
```

Confirm the source is `whale-devx/github-markdown-studio-skills` and save its
full working commit. Back up the lockfile and the entire installed folder
outside the agent's skill directories. Reinstalling replaces files in that
folder, including local edits and untracked notes. Keep authored documents
and custom assets in the consuming project. If the entry lacks a commit,
use the complete backup for recovery until you can identify the source.

Replace `FULL_COMMIT` with the reviewed 40-character SHA. Run the installer
from the same project root. In your audit environment, replace `GUIDE.md`
with a project document whose audit result you know.

```sh
npx --yes skills@1.9.0 add "https://github.com/whale-devx/github-markdown-studio-skills/tree/FULL_COMMIT" --skill github-markdown-studio --agent codex --copy --yes
python -B .agents/skills/github-markdown-studio/scripts/audit.py . GUIDE.md --strict
```

Check the new lock entry and the audit result. On a revision that includes the
package notice, compare `.agents/skills/github-markdown-studio/LICENSE` with
the upstream root `LICENSE` at that same SHA. Earlier packages can lack this
file. Keep the matching upstream notice when sharing a copy.

To roll back, repeat the install using the saved working SHA and repeat the
checks. Inspect other skills' lock entries before accepting the change.
Restoring a shared lockfile wholesale can undo a sibling's later upgrade.
Restore intentional customizations from the backup separately. Start a new
host session to load the restored instructions.

To uninstall the project copy, run `npx --yes skills@1.9.0 remove github-markdown-studio --agent codex --yes`.
Verify the directory and its lock entry are gone. Other agents configured to
read that same project directory will also lose access to the removed copy.

## Other agents and API-key clients

For a host with native Agent Skills support, configure its documented discovery directory and install the entire [skill directory](../skills/github-markdown-studio/). For a text-only host, explicitly supply SKILL.md as task guidance, then supply referenced files as needed. A host that cannot accept instructions or access the required inputs cannot run this workflow.

For API use, your application reads SKILL.md and includes its text in the provider's instruction field, then supplies the user's task and relevant inputs in a separate message. Keep the API key in the application's secret store and use it only for provider authentication. Resolve relative references within the installed skill directory. File edits, helper scripts and external tools require host implementations and permissions. Without tools, return a proposed edit or recommendation for the user to apply.

## First task

Audit examples/advanced-formatting.en.md. Identify one readability issue and propose a minimal edit that preserves the facts.

Record the host and version, whether the host loaded the skill automatically or explicitly, and the actual output. Use public or synthetic inputs when sharing a report.
