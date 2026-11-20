# Contributing

[Home](README.md)

Keep changes focused and evidence-backed. Preserve the original license. Do not add claimed benchmarks, agent compatibility, screenshots or test outcomes that have not been verified.

## Local validation

Use Python 3.10+ in an isolated environment, install the audit requirements, then run:

```bash
python -m pip install -r skills/github-markdown-studio/scripts/requirements.txt
python -m unittest discover -s tests -v
python skills/github-markdown-studio/scripts/audit.py . --translations i18n-manifest.json --strict
```

Changes to the source README require a reviewed Thai update and new source/target hashes in the translation manifest. Do not refresh hashes without reviewing the translation. Changes to the example JSON require regeneration and review of both themes in every locale.

## Change review

Explain changed behavior, tests performed, missing checks and any added dependencies. Include a regression test for helper fixes. Do not mix document redesign with unrelated application changes. The `evals/` scenarios guide agent evaluation and are not evidence that a particular model passed.

Do not include credentials, private documents or generated imagery with unverified provenance. Discuss billed provider integrations and broad permission changes separately rather than enabling them by default.
