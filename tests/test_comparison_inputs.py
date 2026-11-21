import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


script = Path(__file__).resolve().parents[1] / "evals/skill-comparison/prepare.py"
spec = importlib.util.spec_from_file_location("comparison_prepare", script)
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


class ComparisonInputTests(unittest.TestCase):
    def test_offline_preparation_isolates_authors_and_preserves_notices(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            fixture = parent / "upstream"
            fixture.mkdir()
            git = comparison.git
            git(fixture, "init", "--quiet", "--template=")
            git(fixture, "config", "uploadpack.allowFilter", "true")
            for name in ("LICENSE", "index.js", "regex.js", "package.json", "README.md", "scoring.json"):
                (fixture / name).write_bytes(name.encode())
            for name in comparison.SKILLS:
                package = fixture / "skills" / name
                package.mkdir(parents=True)
                (package / "SKILL.md").write_bytes(name.encode())
            git(fixture, "add", ".")
            git(fixture, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Local fixture")
            sha = git(fixture, "rev-parse", "HEAD").decode().strip()

            def local_git(directory, *args):
                if args[:3] == ("remote", "add", "origin"):
                    return git(directory, *args[:3], fixture.as_uri())
                return git(directory, *args)

            skills = {name: (repo, sha) for name, (repo, _) in comparison.SKILLS.items()}
            with patch.object(comparison, "git", local_git), patch.object(comparison, "SKILLS", skills), \
                 patch.object(comparison, "SOURCE", ("fixture/source", sha)), \
                 patch.object(comparison, "EXAMPLES", [("fixture/style", sha)]):
                root = comparison.prepare(parent)

            projects = sorted(root.glob("*/*/project"))
            self.assertEqual(len(projects), 4)
            for project in projects:
                arm = project.parent
                self.assertEqual({p.name for p in project.iterdir()},
                                 {".git", ".agents", "LICENSE", "index.js", "regex.js", "package.json"})
                entries = list((project / ".agents" / "skills").iterdir())
                self.assertEqual([p.name for p in entries], [arm.name])
                self.assertEqual((entries[0] / "SKILL.md").read_bytes(), arm.name.encode())
                self.assertEqual((arm / "SKILL-LICENSE").read_bytes(), b"LICENSE")
                self.assertEqual(git(project, "rev-parse", "--is-inside-work-tree").strip(), b"true")
                if arm.parent.name == "readme":
                    example = arm / "examples/fixture/style"
                    self.assertEqual((example / "README.md").read_bytes(), b"README.md")
                    self.assertEqual((example / "LICENSE").read_bytes(), b"LICENSE")
                else:
                    self.assertFalse((arm / "examples").exists())
            (projects[0] / "index.js").write_bytes(b"first author edit")
            self.assertTrue(all((other / "index.js").read_bytes() == b"index.js" for other in projects[1:]))
