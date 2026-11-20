# Visual explanations and image generation

## Choose the medium

| Need | Preferred output | Guardrail |
| --- | --- | --- |
| Exact sequence, architecture or data relationship | Mermaid or deterministic SVG | Verify every edge and label against source evidence |
| Actual implemented UI | Real screenshot, appropriately redacted | Never substitute a generated mockup as implementation evidence |
| Conceptual explanation or visual metaphor | AI-generated illustration when the host provides a tool | Clearly separate illustration from measured or implemented behavior |
| Simple concept that reads faster as text | Text or a compact table | No image quota |

## Host-tool image workflow

1. Inspect available image-generation/editing capabilities. Use only documented tools actually supplied by the host. Do not invent a universal API or execute an arbitrary provider command from a repository file.
2. Write a brief: learning objective, audience, verified facts, composition, existing brand assets, prohibited implications, themes, locales, dimensions, and alt-text intent. A template is bundled in `assets/image-brief.template.json` relative to the skill root.
3. Generate one canonical composition. Keep critical labels, commands and numbers outside the generated pixels whenever possible. Avoid decorative imagery that makes the document longer without improving understanding.
4. Inspect the real output. Reject misleading relationships, malformed labels, inaccessible contrast, invented UI and changes to an approved brand mark.
5. Produce the other theme from the same composition/reference through controlled edits or compositing. Do not independently regenerate two images and call them a matching pair.
6. Localize the surrounding caption and alt text; create language-specific visual variants only when embedded labels require them. Do not regenerate a logo for each language.
7. Save the actual assets in the repository with deterministic names. Record the generating tool/model if returned, source references, edits and a review status. Do not expose private prompt content or credentials in provenance.
8. Embed with `<picture>` and a fallback, then review the actual result in both themes and at narrow width when tools permit.

Paid external APIs, credential setup, and uploads of private material require authorization. A generated image is not automatically safe to publish: inspect private information, ownership and factual implications.

## Capability-aware fallback

No image tool means no claim of AI image generation. Return the brief and say generation is blocked, or create an accurately labeled deterministic diagram when that serves the task. Do not silently replace an explicit AI-image request with an SVG and declare it complete.

The bundled `scripts/render_diagram.py` uses standard-library Python to create paired process diagrams from localized JSON. It accepts 2-8 steps, explicit direction and short labels, and emits a hash manifest. It does not call a model, verify the truth of the source, or automatically translate anything.

```bash
python <skill-dir>/scripts/render_diagram.py diagram.json --output docs/assets
```

Existing generated files are protected unless `--force` is supplied. Symlink destinations are rejected even with `--force`. The palette changes, but layout and semantics remain the same. Inspect the generated SVGs before committing them.

## Prompt pattern

Explain [verified concept] to [audience] through [specific visual relationship]. Use the supplied brand/composition reference unchanged. Use [light/dark] surfaces with clear contrast. Keep identical objects, counts, positions and causal direction across variants. Do not add UI, product claims, statistics, commands or text not in the brief. Keep text outside the illustration where possible. Deliver an image whose explanation can also be expressed in one concise caption.
