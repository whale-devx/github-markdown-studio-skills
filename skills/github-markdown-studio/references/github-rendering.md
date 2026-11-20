# GitHub rendering, themes and accessibility

## Supported destination

This skill targets repository Markdown viewed on GitHub. Native features include headings, tables, fenced code, relative links, details/summary, alerts, images and Mermaid. A local HTML preview is useful but cannot reproduce every GitHub behavior.

GitHub sanitizes rendered HTML. Do not rely on scripts, inline styles, arbitrary classes, interactive controls, or inline SVG code. Use stored image assets and supported Markdown/HTML. Do not confuse repository Markdown with a GitHub Pages website.

## Theme-aware image pattern

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/flow.en.dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/flow.en.light.svg">
  <img src="assets/flow.en.light.svg" alt="A request is checked, routed and verified." width="640">
</picture>
```

Paths are relative to the document, not to the repository root unless explicitly root-relative. Check both source files and the fallback. Localize alt text and captions. Do not remove the fallback to reduce duplication.

Keep theme pairs identical in geometry and meaning. Preserve the approved logo; recoloring is not redesign. Native Markdown text already follows GitHub's theme, so do not turn ordinary paragraphs into images.

## Review matrix

Review light and dark at desktop and a narrow viewport, such as 360 pixels. Also inspect fallback behavior, a long localized heading, diagram text size, table overflow, collapsed content, and keyboard access where applicable. Examples are test targets, not evidence that review occurred.

Use WCAG contrast targets as a design baseline: at least 4.5:1 for ordinary text and 3:1 for large text and relevant non-text elements. Do not communicate status through color alone. A contrast calculation does not certify overall accessibility. Avoid important text baked into raster images; provide a text equivalent nearby.

Mermaid should default to the host theme when possible. Do not hardcode colors or use a newer syntax merely because it works in another Mermaid renderer. Inspect GitHub's current Mermaid version when compatibility matters. The static audit helper does not parse or render Mermaid.

## Verification labels

- `static`: file existence, syntax structure and local links inspected.
- `local-visual`: inspected in a local browser; name themes and widths.
- `github-preview`: actually inspected on GitHub; record revision and paths.

Never promote one label to another without performing that check.

## Primary references

- [GitHub writing quickstart](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github)
- [GitHub basic writing and relative links](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [GitHub diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
- [GitHub markup pipeline](https://github.com/github/markup)
- [WCAG minimum contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
