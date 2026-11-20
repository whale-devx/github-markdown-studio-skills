"""Render the three documented flowcharts with a preloaded Mermaid CLI image."""
import argparse
from pathlib import Path
import subprocess
import sys
from xml.etree import ElementTree

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ("ghcr.io/mermaid-js/mermaid-cli/mermaid-cli@"
         "sha256:18938e53497376d524e04b1fc0bf7b6d61a491ce9ff7032bb2855d57155acb10")
SVG = "{http://www.w3.org/2000/svg}"
SHOWCASE_EDGES = ("A_B", "B_C")
CASES = (
    ("docs/architecture.md", 11, ("A_B", "B_K", "K_C", "C_D", "C_E", "E_F", "E_G",
                                  "D_H", "F_H", "G_H", "H_I", "I_J"),
     ("Requested document scope", "Patch and honest verification report")),
    ("examples/advanced-formatting.en.md", 3, SHOWCASE_EDGES,
     ("Read evidence", "Choose format", "Check and report")),
    ("examples/advanced-formatting.th.md", 3, SHOWCASE_EDGES,
     ("อ่านหลักฐาน", "เลือกรูปแบบ", "ตรวจและรายงาน")),
)


def check_svg(output, definition, count, edges, labels):
    root = ElementTree.fromstring(output)
    if root.tag != SVG + "svg":
        raise ValueError("Expected an SVG document")
    for field, attr, tag in (("accTitle", "aria-labelledby", "title"),
                             ("accDescr", "aria-describedby", "desc")):
        prefix = field + ":"
        declared = [line.strip()[len(prefix):].strip() for line in definition.splitlines()
                    if line.strip().startswith(prefix)]
        element = root.find(SVG + tag)
        if (len(declared) != 1 or not declared[0] or element is None or
                element.text != declared[0] or not element.get("id") or
                element.get("id") not in root.get(attr, "").split()):
            raise ValueError(f"SVG {attr} must refer to the diagram's {field}")
    nodes = [" ".join("".join(g.itertext()).split()) for g in root.iter(SVG + "g")
             if "node" in g.get("class", "").split()]
    if len(nodes) != count or not all(nodes) or not set(labels).issubset(nodes):
        raise ValueError("Diagram nodes or labels differ from the documented workflow")
    arrows = [p.get("data-id", "") for p in root.iter(SVG + "path") if p.get("data-edge") == "true"
              and p.get("d") and p.get("marker-end")]
    if sorted(arrows) != sorted(f"L_{edge}_0" for edge in edges):
        raise ValueError("Directed connections differ from the documented workflow")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("podman", "docker"), default="podman")
    engine = parser.parse_args().engine
    command = [engine, "run", "--rm", "-i", "--pull=never", "--network=none",
               "--cap-drop=ALL", "--security-opt=no-new-privileges", IMAGE]
    for path, count, edges, labels in CASES:
        tokens = MarkdownIt("commonmark").parse((ROOT / path).read_text(encoding="utf-8"))
        diagrams = [token.content for token in tokens if token.type == "fence"
                    and token.info.strip() == "mermaid"]
        if len(diagrams) != 1:
            raise ValueError(f"{path}: expected one Mermaid fence")
        for theme in ("default", "dark"):
            try:
                result = subprocess.run([*command, "-q", "-i", "-", "-o", "-", "-e", "svg", "-t", theme],
                                        input=diagrams[0].encode("utf-8"), stdout=subprocess.PIPE,
                                        check=True, timeout=90)
                check_svg(result.stdout, diagrams[0], count, edges, labels)
            except (ValueError, ElementTree.ParseError, OSError, subprocess.SubprocessError) as error:
                sys.exit(f"{path} ({theme}): {error}")
            print(f"PASS {path} ({theme}): {count} nodes, {len(edges)} arrows, title and description")


if __name__ == "__main__":
    main()
