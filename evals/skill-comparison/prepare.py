"""Prepare four isolated author workspaces from pinned public sources."""
import argparse
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from zipfile import ZipFile


SOURCE = ("Flet/github-slugger", "3461c4350868329c8530904d170358bca1d31448")
SKILLS = {
    "github-markdown-studio": ("whale-devx/github-markdown-studio-skills", "f2232810ed65da3bbdc63041fa72fae5d3a4ba47"),
    "create-readme": ("github/awesome-copilot", "f10fdb8b2660ce85c98f220b2f1ca24653768a5c"),
    "mermaid-diagrams": ("softaworks/agent-toolkit", "3027f20f3181758385a1bb8c022d4041dfb4de84"),
}
EXAMPLES = (
    ("Azure-Samples/serverless-chat-langchainjs", "ae6df50bb0998753a3c28fdd10ea6127c217c232"),
    ("Azure-Samples/serverless-recipes-javascript", "2b05da6daca68fcb571da103c3efe5b4dc765661"),
    ("sinedied/run-on-output", "4d8dd6b7ee53fac6ed4362b0c17c4ab625c44354"),
    ("sinedied/smoke", "3d4972f7579229dd9d248a8d858d8161860a5e99"),
)


def git(directory, *args):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    return subprocess.check_output(
        ["git", "-C", str(directory), "-c", "credential.helper=", "-c", "core.hooksPath=", *args],
        env=env, timeout=180,
    )


def export(cache, source, output, *paths):
    repo, sha = source
    store = cache / "git" / repo
    store.parent.mkdir(parents=True, exist_ok=True)
    git(cache, "init", "--quiet", "--bare", "--template=", str(store))
    git(store, "remote", "add", "origin", f"https://github.com/{repo}.git")
    git(store, "config", "remote.origin.promisor", "true")
    git(store, "config", "remote.origin.partialclonefilter", "blob:none")
    git(store, "fetch", "--quiet", "--depth=1", "--no-tags", "--filter=blob:none", "origin", sha)
    if git(store, "rev-parse", "FETCH_HEAD^{commit}").decode().strip() != sha:
        raise ValueError(f"Unexpected source revision for {repo}")
    archive = git(store, "archive", "--format=zip", sha, "--", *paths)
    with ZipFile(io.BytesIO(archive)) as snapshot:
        snapshot.extractall(output)


def copy_files(source, destination):
    # Preserve empty Git directories and file bytes without requiring POSIX metadata.
    for directory, _, files in os.walk(source):
        folder = Path(directory)
        target = destination / folder.relative_to(source)
        target.mkdir(parents=True, exist_ok=True)
        for name in files:
            shutil.copyfile(folder / name, target / name)


def prepare(parent):
    with tempfile.TemporaryDirectory(prefix="comparison-inputs-") as temp:
        cache = Path(temp)
        source = cache / "source"
        export(cache, SOURCE, source, "LICENSE", "index.js", "regex.js", "package.json")
        git(source, "init", "--quiet", "--template=")
        for name, pin in SKILLS.items():
            export(cache, pin, cache / "payloads" / name, "LICENSE", f"skills/{name}")
        references = cache / "examples"
        for repo, sha in EXAMPLES:
            export(cache, (repo, sha), references / repo, "README.md", "LICENSE")

        root = Path(tempfile.mkdtemp(prefix="markdown-comparison-", dir=parent)).resolve()
        try:
            for task, specialist in (("readme", "create-readme"), ("diagram", "mermaid-diagrams")):
                for name in ("github-markdown-studio", specialist):
                    arm = root / task / name
                    project = arm / "project"
                    copy_files(source, project)
                    payload = cache / "payloads" / name
                    copy_files(payload / "skills" / name, project / ".agents" / "skills" / name)
                    shutil.copyfile(payload / "LICENSE", arm / "SKILL-LICENSE")
                    if task == "readme":
                        copy_files(references, arm / "examples")
        except Exception:
            if root.parent == parent.resolve() and root.name.startswith("markdown-comparison-"):
                shutil.rmtree(root)
            raise
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent", type=Path, help="Existing directory for a new, uniquely named comparison")
    args = parser.parse_args()
    if not args.parent.is_dir():
        parser.error("Choose an existing parent directory")
    print(prepare(args.parent))
