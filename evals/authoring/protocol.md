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

## Advanced structures on two external tasks

Use the installed skill from commit 16f54457c0483e392cdb68dcda5b3f3f14dec6a7
in the existing Codex desktop session. Freeze the following tasks before
opening their upstream references or running their examples. Choose the
document structure for the reader's decision. Keep the runtime instructions
visible when optional details are closed. Leave the skill itself frozen.

1. A CSV importer receives rows with a complete record, an explicit empty
   final cell, a missing final cell and a surplus cell. Turn the Python
   3.12 DictReader reference into a decision table. Use the same header and
   reader settings for all rows. Show the distinction between a quoted
   comma and a surplus column. Check every table row and the runnable
   example against the standard library.
2. An operator needs to repair a deferred SQLite foreign-key violation
   after COMMIT fails, and be able to abandon the batch without losing
   earlier committed data. Turn the SQLite foreign-key documentation into
   a short operator runbook. State when to enable enforcement, how to
   confirm it, how to verify the failure and which connection to use for
   repair or rollback. Exercise both paths and verify persisted rows.
   Keep the recovery steps visible and make optional diagnostics collapsible.

Check both documents through their normal readers on GitHub at 360 and
1280 CSS pixels in light and dark themes. Exercise the decision table and
the optional disclosure with the keyboard. Report any clipping or control
failure. This is a single-author transformation trial. Reader performance,
a model comparison and aggregate host support require separate evidence.
