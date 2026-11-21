"""Replay the reviewed ripgrep and uv examples against disposable local fixtures."""
import hashlib
from importlib.resources import files
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import venv

HERE = Path(__file__).resolve().parent
SEARCH = (
    "rg -l -F 'v2.0' .",
    "rg --hidden -l -F 'v2.0' .",
    "rg -l -F 'v9.9' .",
    "rg -l -F 'v2.0' missing-input.txt",
)
SHOW_TARGET = "uv --offline pip show --python .maintenance pip"
INSTALL = "uv --offline --no-cache pip install --python .maintenance --no-index --find-links ./wheelhouse pip"
SHOW_PROJECT = "uv --offline pip show --python .venv pip"
ROLLBACK = "uv --offline pip uninstall --python .maintenance pip"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_document(filename, expected):
    text = (HERE / filename).read_text(encoding="utf-8")
    blocks = re.findall(r"^```sh\n(.*?)^```$", text, re.MULTILINE | re.DOTALL)
    lines = [line for block in blocks for line in block.splitlines() if line.strip()]
    require(lines == list(expected), f"{filename}: command blocks differ from the reviewed replay")


def manifest(directory):
    return {p.relative_to(directory): hashlib.sha256(p.read_bytes()).digest()
            for p in directory.rglob("*") if p.is_file()}


def run(command, cwd, env, expected_code=0):
    result = subprocess.run(shlex.split(command), cwd=cwd, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=60)
    require(result.returncode == expected_code,
            f"{command}: expected exit {expected_code}, got {result.returncode}\n{result.stderr}")
    return result


def replay_search(directory, env):
    for name, value in {".ignore": "generated.txt", "generated.txt": "v2.0",
                        ".client.txt": "v2.0", "notes.txt": "v2.0", "other.txt": "v2x0"}.items():
        (directory / name).write_text(value + "\n", encoding="utf-8")
    before = manifest(directory)
    for command, expected in zip(SEARCH, ({"notes.txt"}, {".client.txt", "notes.txt"})):
        result = run(command, directory, env)
        matches = sorted(Path(line).as_posix() for line in result.stdout.splitlines())
        require(matches == sorted(expected) and not result.stderr, f"{command}: unexpected match set")
    missing = run(SEARCH[2], directory, env, 1)
    require(not missing.stdout and not missing.stderr, "absent literal produced output")
    invalid = run(SEARCH[3], directory, env, 2)
    require(not invalid.stdout and "missing-input.txt" in invalid.stderr, "missing path diagnostic")
    require(manifest(directory) == before, "search changed its input files")


def replay_environment(directory, env):
    target, project = directory / ".maintenance", directory / ".venv"
    for path in (target, project):
        venv.EnvBuilder(with_pip=False).create(path)
    wheelhouse = directory / "wheelhouse"
    wheelhouse.mkdir()
    wheels = [p for p in files("ensurepip").joinpath("_bundled").iterdir()
              if p.name.startswith("pip-") and p.name.endswith(".whl")]
    require(len(wheels) == 1, "replay requires one pip wheel bundled with this Python installation")
    wheel = wheels[0]
    before = manifest(project)

    def check_absent(command):
        result = run(command, directory, env, 1)
        require(not result.stdout and "not found" in result.stderr.lower() and "pip" in result.stderr.lower(),
                f"{command}: expected a missing-package diagnostic")

    check_absent(SHOW_PROJECT)
    check_absent(SHOW_TARGET)
    run(INSTALL, directory, env, 1)
    check_absent(SHOW_TARGET)
    (wheelhouse / wheel.name).write_bytes(wheel.read_bytes())
    run(INSTALL, directory, env)
    info = run(SHOW_TARGET, directory, env).stdout
    fields = dict(line.split(": ", 1) for line in info.splitlines() if ": " in line)
    require(fields.get("Name") == "pip" and fields.get("Version") == wheel.name.split("-")[1],
            "maintenance environment has the wrong package or version")
    require(Path(fields["Location"]).resolve().is_relative_to(target.resolve()), "wrong install location")
    check_absent(SHOW_PROJECT)
    require(before == manifest(project), "installation changed the project environment")
    run(ROLLBACK, directory, env)
    check_absent(SHOW_TARGET)
    check_absent(SHOW_PROJECT)
    require(before == manifest(project), "rollback changed the project environment")
    print(f"Verified {wheel.name} installation and rollback. Project files matched both times.")


def main():
    check_document("ripgrep-reference.md", SEARCH)
    check_document("uv-runbook.md", (SHOW_TARGET, INSTALL, SHOW_TARGET, SHOW_PROJECT, ROLLBACK))
    with tempfile.TemporaryDirectory(prefix="markdown-authoring-") as tmp:
        root = Path(tmp)
        home, search, maintenance = (root / name for name in ("home", "search", "uv"))
        for path in (home, search, maintenance):
            path.mkdir()
        allowed = {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "SYSTEMDRIVE", "PATHEXT"}
        env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
        env.update({key: str(home) for key in ("HOME", "USERPROFILE", "TMP", "TEMP", "TMPDIR",
                                               "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME")})
        env.update(UV_OFFLINE="1", UV_NO_PYTHON_DOWNLOADS="1", UV_NO_CONFIG="1",
                   UV_CACHE_DIR=str(home / "uv-cache"), PYTHONDONTWRITEBYTECODE="1", NO_COLOR="1")
        for command in ("rg --version", "uv --version"):
            print(run(command, root, env).stdout.splitlines()[0])
        print(f"Python {sys.version.split()[0]}")
        replay_search(search, env)
        print("Verified four search examples and the original file contents.")
        replay_environment(maintenance, env)


if __name__ == "__main__":
    main()
