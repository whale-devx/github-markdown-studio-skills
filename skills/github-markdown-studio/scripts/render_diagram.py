#!/usr/bin/env python3
"""Generate matching light/dark SVG process diagrams from localized JSON.

Deterministic illustration, not AI image generation. No network, keys or packages.
"""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import sys
import tempfile
import unicodedata

PALETTES = {
    "light": {"background": "#f6f8fa", "surface": "#ffffff", "text": "#182230", "muted": "#475569", "accent": "#0f766e", "border": "#cbd5e1"},
    "dark": {"background": "#0d1117", "surface": "#161b22", "text": "#f0f6fc", "muted": "#b7c4d5", "accent": "#5eead4", "border": "#39495c"},
}
LANGUAGE = re.compile(r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*\Z")


def display_width(text: str) -> int:
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in {"W", "F"} else 1 for c in text)


def label(value: object, maximum: int, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or display_width(value) > maximum:
        raise ValueError(f"{name} must be non-empty text within {maximum} display columns; use shorter labels")
    if any(unicodedata.category(c) in {"Cc", "Cs"} for c in value):
        raise ValueError(f"{name} contains control characters")
    return value.strip()


def build_assets(spec: dict) -> dict[str, str]:
    if not isinstance(spec, dict) or spec.get("version") != 1:
        raise ValueError("Expected a version 1 diagram specification")
    name = spec.get("name", "")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("name must be a short lowercase, hyphenated filename stem")
    locales = spec.get("locales")
    if not isinstance(locales, dict) or not 1 <= len(locales) <= 30:
        raise ValueError("Provide 1-30 locales")
    assets: dict[str, str] = {}
    step_count = None
    for language, content in locales.items():
        if not LANGUAGE.fullmatch(language) or not isinstance(content, dict):
            raise ValueError("Invalid locale tag or content")
        direction = content.get("direction", "ltr")
        if direction not in {"ltr", "rtl"}:
            raise ValueError("direction must be ltr or rtl")
        title = label(content.get("title"), 44, "title")
        summary = label(content.get("summary"), 70, "summary")
        steps = content.get("steps")
        if not isinstance(steps, list) or not 2 <= len(steps) <= 8:
            raise ValueError("Provide 2-8 steps per locale")
        if step_count is not None and len(steps) != step_count:
            raise ValueError("Keep the same number and order of steps in every locale")
        step_count = len(steps)
        normalized = []
        for step in steps:
            if not isinstance(step, dict):
                raise ValueError("Each step must be an object")
            normalized.append((label(step.get("title"), 32, "step title"), label(step.get("detail"), 58, "step detail")))
        height = 166 + 124 * len(steps)
        for theme, palette in PALETTES.items():
            x, anchor = (532, "start") if direction == "rtl" else (108, "start")
            def text(px, py, size, value, fill, weight=400, align=anchor):
                return f'<text x="{px}" y="{py}" fill="{fill}" font-size="{size}" font-weight="{weight}" text-anchor="{align}" direction="{direction}">{escape(value)}</text>'
            parts = [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="{height}" viewBox="0 0 640 {height}" role="img" aria-labelledby="title desc" xml:lang="{language}">',
                f'<title id="title">{escape(title)}</title>',
                f'<desc id="desc">{escape(summary + ": " + "; ".join(a + ". " + b for a, b in normalized))}</desc>',
                f'<rect width="640" height="{height}" rx="20" fill="{palette["background"]}"/>',
                '<g font-family="system-ui, -apple-system, Segoe UI, sans-serif">',
                text(600 if direction == "rtl" else 40, 53, 24, title, palette["text"], 700),
                text(600 if direction == "rtl" else 40, 86, 15, summary, palette["muted"]),
            ]
            for index, (heading, detail) in enumerate(normalized):
                y = 116 + index * 124
                circle_x = 570 if direction == "rtl" else 70
                parts.extend([
                    f'<rect x="32" y="{y}" width="576" height="98" rx="14" fill="{palette["surface"]}" stroke="{palette["border"]}"/>',
                    f'<circle cx="{circle_x}" cy="{y + 38}" r="18" fill="{palette["accent"]}"/>',
                    f'<text x="{circle_x}" y="{y + 44}" text-anchor="middle" fill="{palette["surface"]}" font-size="16" font-weight="700">{index + 1}</text>',
                    text(x, y + 39, 20, heading, palette["text"], 650),
                    text(x, y + 69, 14, detail, palette["muted"]),
                ])
                if index < len(normalized) - 1:
                    parts.append(f'<path d="M320 {y + 101} v16 m-5 -5 5 5 5 -5" fill="none" stroke="{palette["accent"]}" stroke-width="2"/>')
            parts.extend(['</g>', '</svg>'])
            assets[f"{name}.{language}.{theme}.svg"] = "\n".join(parts) + "\n"
    metadata = {
        "version": 1, "method": "deterministic-svg", "ai_generated": False,
        "source_spec_sha256": hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "files": {filename: hashlib.sha256(content.encode()).hexdigest() for filename, content in assets.items()},
        "review": "Inspect text shaping, legibility and meaning in each locale; generation is not visual approval.",
    }
    assets[f"{name}.manifest.json"] = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    return assets


def write_assets(output: Path, assets: dict[str, str], force: bool = False) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for filename in assets:
        destination = output / filename
        if destination.is_symlink() or (destination.exists() and not force):
            raise ValueError(f"Refusing to replace {filename}; use --force only for reviewed generated assets")
        if destination.exists() and not destination.is_file():
            raise ValueError(f"Not a regular file: {filename}")
    # Stage all content before replacing destinations. Each replacement is atomic.
    with tempfile.TemporaryDirectory(dir=output) as temporary:
        staging = Path(temporary)
        for filename, content in assets.items():
            (staging / filename).write_text(content, encoding="utf-8")
        for filename in assets:
            (staging / filename).replace(output / filename)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="Localized diagram JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output asset directory")
    parser.add_argument("--force", action="store_true", help="Replace existing generated files; symlinks are always rejected")
    args = parser.parse_args()
    try:
        if args.spec.stat().st_size > 256 * 1024:
            raise ValueError("Specification must not exceed 256 KiB")
        assets = build_assets(json.loads(args.spec.read_text(encoding="utf-8")))
        write_assets(args.output, assets, args.force)
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, f"render_diagram: {exc}\n")
    print(json.dumps({"method": "deterministic-svg", "files": sorted(assets)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
