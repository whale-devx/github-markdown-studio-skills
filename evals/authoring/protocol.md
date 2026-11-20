# External-project authoring trial

Freeze the tasks before inspecting either upstream manual or running the
examples. Use the existing Codex desktop session, explicitly invoke the
Markdown Studio skill from product commit 9edf0e87f844b9cbfd35f7be695ae3a12dacb5e6,
and write two short GitHub repository documents. Use original wording.
The products were selected from locally available binaries, outside the
Studio examples and reader packets. This is a single-author trial without
an independent reader or baseline. Do not update the skill during the trial.

1. Turn ripgrep's guide (BurntSushi/ripgrep, tag 15.2.0) into a reference for a
   maintainer searching for the literal version string v2.0. Show the default
   search, an opt-in search that includes hidden files while preserving ignore
   rules, and how to interpret absence versus a faulty path. The fixture has
   notes.txt and .client.txt containing v2.0, generated.txt containing v2.0
   excluded by .ignore, and other.txt containing v2x0. Require the exact file
   sets on both success paths, exit 1 with empty output for an absent literal,
   and exit 2 with a diagnostic for an absent input path. Hash the fixture
   before and after. Check the commands written into the final Markdown.

2. Turn uv's pip-interface environment and package documentation (astral-sh/uv,
   tag 0.8.12) into a runbook for an operator who needs pip in a maintenance
   virtual environment. An adjacent project .venv must remain untouched. The
   shell has neither environment activated, both start without pip, and the
   only approved distribution is a pip wheel in wheelhouse/. Show diagnosis,
   an offline install using only that directory, and verification of both
   environments. Require a missing-package result before repair, a matching
   installed version and location under .maintenance afterward, and a
   byte-identical project environment where pip is still absent. Check the
   commands written into the final Markdown. Never perform an upstream edit.

Record tool versions, pinned input links, commands, observed failures,
retries, output boundaries and any check that remains open. Do not infer
general documentation quality, activation on another host or a human result.
