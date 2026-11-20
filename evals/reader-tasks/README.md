# Reader tasks for guides, references and runbooks

A facilitator can use these tasks to see whether a reader can make a
correct decision from the assigned document. They use sources from projects
outside Markdown Studio. Independent reader trials are pending.

| Task | Document to give the reader in a baseline trial | Participant packet |
| --- | --- | --- |
| Commit one revision and keep a later edit for tomorrow | [Git tutorial at `c44beea`](https://github.com/git/git/blob/c44beea485f0f2feaf460e2ac87fdd5608d63cf0/Documentation/gittutorial.adoc) | [Two edits before a commit](guide.md) |
| Interpret a saved model inventory | [Model Router discovery reference at `0ba1e90`](https://github.com/whale-devx/intelligent-model-router-skills/blob/0ba1e9045642b1ad8d65f6f5bdd91f8d40118b77/skills/intelligent-model-router/references/live-discovery.md) | [A saved inventory](reference.md) |
| Recover from a release setup conflict | [Git FlowKit release guide at `a15e6e0`](https://github.com/whale-devx/git-flowkit-skills/blob/a15e6e024d39c93592f655d5a903c15342d5c45f/skills/git-flowkit/references/releases.md) | [Release setup during a handover](runbook.md) |

## Run a comparison

1. Freeze the baseline and candidate documents before assigning readers.
   Give each author the same source revision, editing request and budget.
   Keep the participant questions and [grading key](scoring.json) with the
   facilitator during authoring. For a held-out trial, use contributors who
   have not seen those materials. Record any prior exposure.
2. Save each rendered document under a neutral identifier. Preserve headings,
   links, code and tables. Keep the identity mapping private until scoring is
   complete. Assign readers at random to a version per task. Each reader
   sees each task only once. Give them only the assigned rendering and its
   participant packet. Use the same time allowance and lookup rules for
   every version.
3. Record the anonymous reader and document IDs, source and candidate
   revision, elapsed time, cited passage, and answer to each question. An
   unanswered or timed-out decision receives zero points. Record timeouts.
4. Have a reviewer score each decision against the key before revealing
   document identities. Award one point when all required facts for that
   decision are present and consistent. Accept ordinary paraphrases.
   Record fatal errors separately and mark the task failed if one occurs.
   A task passes with three points and zero fatal errors.
5. Report counts of participants, completed tasks, passes and fatal errors
   by task and document, together with missing observations and elapsed
   times. For authoring comparisons, report the measured authoring time
   and token usage when available. Keep raw reader responses private unless
   readers consent to sharing them.

These public packets can also be used for practice. A person who has seen
the questions or key needs a fresh task for a held-out comparison.
