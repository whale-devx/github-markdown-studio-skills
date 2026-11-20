#!/usr/bin/env python3
"""Offline capability preflight for any Agent Skills-compatible host.

This helper NEVER detects host tools, invokes a model, contacts a provider,
installs dependencies, or runs requested tasks. The host/user supplies the
observed capabilities; a reported 'ready' only means prerequisites were declared.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

CAPABILITIES = frozenset({
    "read_files", "write_files", "run_commands", "python",
    "image_generate", "image_edit", "browser", "network",
})
TASKS = frozenset({
    "static_audit", "edit_markdown", "mermaid_diagram", "svg_diagram",
    "ai_illustration", "paired_ai_illustration", "dark_light_assets",
    "multilingual_draft", "local_preview", "github_preview",
})
MAX_INPUT_BYTES = 65536


def validate(payload: Any) -> tuple[dict[str, bool | None], list[str], str | None]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object")
    unknown = set(payload) - {"agent", "capabilities", "tasks"}
    if unknown:
        raise ValueError(f"Unknown top-level keys: {', '.join(sorted(unknown))}")
    agent = payload.get("agent")
    if agent is not None and (not isinstance(agent, str) or not agent.strip() or len(agent) > 128):
        raise ValueError("agent must be a nonempty string (<=128 characters) when provided")
    provided = payload.get("capabilities")
    if not isinstance(provided, dict):
        raise ValueError("capabilities must be an object with boolean or null values")
    unknown = set(provided) - CAPABILITIES
    if unknown:
        raise ValueError(f"Unknown capabilities: {', '.join(sorted(unknown))}")
    if any(v is not None and type(v) is not bool for v in provided.values()):
        raise ValueError("Capabilities must be true, false or null; omission means unknown")
    capabilities = {key: provided.get(key) for key in CAPABILITIES}
    tasks = payload.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a nonempty array")
    if any(not isinstance(t, str) or t not in TASKS for t in tasks):
        raise ValueError("Unknown task; consult documented TASKS")
    if len(tasks) != len(set(tasks)):
        raise ValueError("Duplicate tasks are not allowed")
    return capabilities, tasks, agent


def availability(caps: dict[str, bool | None], *keys: str) -> str:
    """Three-valued prerequisite check: unavailable > unknown > available."""
    if any(caps[key] is False for key in keys):
        return "blocked"
    if any(caps[key] is None for key in keys):
        return "unverified"
    return "ready"


def item(task: str, status: str, method: str, detail: str) -> dict[str, str]:
    return {
        "task": task,
        "status": status,
        "method": method,
        "detail": detail,
        "execution": "not-run",
    }


def select(task: str, c: dict[str, bool | None]) -> dict[str, str]:
    if task == "static_audit":
        access = availability(c, "read_files")
        if access != "ready":
            return item(task, access, "inspect-files", "Repository reading must be available and confirmed.")
        if availability(c, "run_commands", "python") == "ready":
            return item(task, "ready", "offline-audit-helper", "Inspect script and install dependencies only with permission.")
        return item(task, "fallback", "manual-readonly-review", "Offline helper not confirmed; inspect files manually and report checks not run.")

    if task == "edit_markdown":
        status = availability(c, "read_files", "write_files")
        return item(task, status, "native-markdown-edit", "Write only within authorized scope; unavailable or unknown access cannot be assumed.")

    if task == "mermaid_diagram":
        status = availability(c, "write_files")
        return item(task, status, "github-mermaid-code-block", "Can author Markdown without a Mermaid tool; rendering and meaning need separate review.")

    if task == "svg_diagram":
        if availability(c, "write_files", "run_commands", "python") == "ready":
            return item(task, "ready", "offline-deterministic-svg", "The bundled generator is not AI image generation; inspect output.")
        if availability(c, "write_files") == "ready":
            return item(task, "fallback", "github-mermaid-code-block", "SVG generator unavailable; use Mermaid only if an equivalent diagram is acceptable.")
        return item(task, availability(c, "write_files"), "not-available", "Writing access is required to save an asset.")

    if task == "ai_illustration":
        status = availability(c, "write_files", "image_generate")
        return item(task, status, "host-image-generation", "Requires an actual image tool; SVG or a prompt is NOT equivalent to AI-generated imagery.")

    if task == "paired_ai_illustration":
        status = availability(c, "write_files", "image_generate", "image_edit")
        return item(task, status, "single-reference-generation-and-edit", "Do not regenerate dark and light variants independently or claim consistent composition without review.")

    if task == "dark_light_assets":
        edit = availability(c, "write_files", "image_edit")
        svg = availability(c, "write_files", "run_commands", "python")
        if edit == "ready":
            return item(task, "ready", "controlled-image-edit", "Create and inspect matched dark/light files, keep the same layout.")
        if svg == "ready":
            return item(task, "ready", "offline-deterministic-svg", "Suitable for exact process diagrams; not for altering an existing photograph.")
        if availability(c, "write_files") == "ready":
            return item(task, "fallback", "manually-authored-svg", "Paired SVG can be authored manually but theme and geometry review is not automatic.")
        return item(task, availability(c, "write_files"), "not-available", "Cannot save theme variants without writing access.")

    if task == "multilingual_draft":
        status = availability(c, "read_files", "write_files")
        if status == "ready":
            return item(task, "review-required", "host-language-model-draft", "Native speaker, technical terminology and RTL shaping are not certified by this preflight.")
        return item(task, status, "not-available", "Read/write capability is required to create linked translations.")

    if task == "local_preview":
        status = availability(c, "browser")
        return item(task, status, "host-browser-local-preview", "Local browser checks do not prove actual GitHub rendering.")

    if task == "github_preview":
        status = availability(c, "browser", "network")
        return item(task, status, "host-browser-github-preview", "Requires accessible GitHub URLs and permission; screenshot is not proof until performed.")

    raise ValueError(f"Unhandled task: {task}")


def plan(payload: Any) -> dict[str, Any]:
    caps, tasks, agent = validate(payload)
    report = {
        "schema_version": 1,
        "agent": agent,
        "model_provider": "not-used-for-routing",
        "capabilities": {key: caps[key] for key in sorted(CAPABILITIES)},
        "tasks": [select(task, caps) for task in tasks],
        "disclaimer": "Preflight based only on supplied observations; no tool, agent, model or provider was invoked or verified.",
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="Path to a JSON capability inventory, or '-' for stdin")
    args = parser.parse_args(argv)
    try:
        if args.input == "-":
            raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        else:
            path = Path(args.input)
            if path.stat().st_size > MAX_INPUT_BYTES:
                raise ValueError("Input exceeds 64 KiB")
            raw = path.read_bytes()
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("Input exceeds 64 KiB")
        report = plan(json.loads(raw))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Capability preflight: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
