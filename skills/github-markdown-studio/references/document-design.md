# Document design

## Select structure by purpose

| Type | Reader's task | Suggested sequence |
| --- | --- | --- |
| README | Decide whether to try the project | Purpose, concrete example, setup, next steps, limitations |
| Tutorial | Reach a first successful outcome | Prerequisites, steps, expected result, recovery, next exercise |
| How-to | Complete a specific task | Goal, assumptions, commands, verification, troubleshooting |
| API/config reference | Find an exact contract | Identifier, type, default, constraints, example, version notes |
| Architecture | Understand boundaries and tradeoffs | Context, components, flow, evidence, decisions, limitations |
| ADR | Understand a decision | Status, context, decision, alternatives, consequences |
| Runbook | Recover safely | Symptoms, checks, actions, rollback, escalation, verification |
| Roadmap/changelog | Understand status or change | Explicit version/status, delivered versus planned, migration impact |
| Agent instructions | Preserve an execution contract | Required metadata, scope, rules, workflow, verification |

These are design prompts, not mandatory boilerplate. Keep concise documents concise. Do not impose an H1 on a deliberate fragment or expand a small changelog into a landing page.

## Reading design

Put the most useful concrete example near the concept it illustrates. Link to long reference material instead of copying it into several files. Use headings that answer a reader's question. Describe prerequisites and expected results explicitly. A command is not verified solely because its package name looks plausible.

Use a table when readers compare the same attributes across options. Do not use a table to imitate a responsive grid. Keep essential warnings outside collapsed sections. Use GitHub alerts selectively and avoid nesting them in other presentation containers.

A visual must explain a relationship, decision, state, or workflow more clearly than its replacement text. Avoid adding stock imagery to API references or emergency runbooks merely to satisfy a visual quota.

## Preserve the document set

Respect canonical pages, existing document IDs and stable links. When splitting a long file, update inbound and outbound paths within the authorized scope. Report references outside the scope rather than silently rewriting unrelated files. A source path is evidence only after reading its relevant content.

Do not measure writing quality with word count or an English readability formula alone. Thai, CJK and right-to-left scripts require language-aware review. Ask whether a reader can find the answer, perform the task, and distinguish fact from proposal.
