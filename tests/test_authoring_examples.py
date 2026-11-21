"""Replay the reviewed CSV and SQLite examples using only the standard library."""
import csv
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / "evals/authoring"
CSV_EXAMPLE = '''import csv

with open("records.csv", encoding="utf-8", newline="") as stream:
    rows = csv.DictReader(stream, restkey="_extra", restval=None)
    for row in rows:
        print(row["id"], repr(row["place"]), row.get("_extra", []))'''

# The executable statements are fixture inputs. Never execute arbitrary Markdown.
SQL = (
    ("PRAGMA foreign_keys = ON;", "PRAGMA foreign_keys;"),
    ("CREATE TABLE batch (id INTEGER PRIMARY KEY);",
     "CREATE TABLE item ( id INTEGER PRIMARY KEY, batch_id INTEGER REFERENCES batch(id) DEFERRABLE INITIALLY DEFERRED );",
     "INSERT INTO batch VALUES (1);", "INSERT INTO item VALUES (10, 1);"),
    ("BEGIN;", "INSERT INTO item VALUES (20, 2);", "COMMIT;"),
    ("PRAGMA foreign_key_check(item);",),
    ("INSERT INTO batch VALUES (2);", "PRAGMA foreign_key_check(item);", "COMMIT;"),
    ("ROLLBACK;",),
    ("SELECT id, batch_id FROM item ORDER BY id;",),
)


def fences(text, language):
    return re.findall(r"^```" + language + r"\n(.*?)\n```$", text, re.MULTILINE | re.DOTALL)


class TransformationExamples(unittest.TestCase):
    def test_csv_table_and_printed_example(self):
        text = (EXAMPLES / "csv-triage.md").read_text(encoding="utf-8")
        self.assertEqual(fences(text, "python"), [CSV_EXAMPLE])
        sample, = fences(text, "csv")
        lines = sample.splitlines()
        self.assertEqual(lines[0], "id,place")
        reader = csv.DictReader(lines, restkey="_extra", restval=None)
        entries = [line.strip("|").split("|") for line in text.splitlines() if line.startswith("| `")]
        outputs = []
        for line, row, (source, decision) in zip(lines[1:], reader, entries, strict=True):
            place, extra = repr(row["place"]), row.get("_extra", [])
            self.assertEqual(source.strip(), f"`{line}`")
            self.assertIn(f"`{place}`", decision)
            for value in extra:
                self.assertIn(f"`{value!r}`", decision)
            outputs.append(f"{row['id']} {place} {extra}")
        self.assertEqual(outputs, ["A1 'North, Bay' []", "B2 '' []", "C3 None []", "D4 'West' ['annex', 'upper']"])
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "records.csv").write_text(sample + "\n", encoding="utf-8")
            output = subprocess.check_output([sys.executable, "-I", "-B", "-c", CSV_EXAMPLE],
                                             cwd=directory, text=True, timeout=10)
        self.assertEqual(output.splitlines(), outputs)

    def test_sqlite_repair_and_rollback(self):
        text = (EXAMPLES / "sqlite-recovery.md").read_text(encoding="utf-8")
        normalized = [" ".join(block.split()) for block in fences(text, "sql")]
        self.assertEqual(normalized, [" ".join(group) for group in SQL])
        (enable, status), schema, (begin, insert, commit), (check,), repair, (rollback,), (verify,) = SQL
        for keep in (True, False):
            with self.subTest(repair=keep), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "practice.db"
                with closing(sqlite3.connect(path, isolation_level=None)) as db:
                    db.execute(enable)
                    self.assertEqual(db.execute(status).fetchone(), (1,))
                    for statement in schema:
                        db.execute(statement)
                    db.execute(begin)
                    db.execute(insert)
                    with self.assertRaisesRegex(sqlite3.IntegrityError, "FOREIGN KEY constraint failed"):
                        db.execute(commit)
                    self.assertTrue(db.in_transaction)
                    self.assertEqual(db.execute(check).fetchall(), [("item", 20, "batch", 0)])
                    with closing(sqlite3.connect(path)) as observer:
                        self.assertEqual(observer.execute(verify).fetchall(), [(10, 1)])
                    if keep:
                        parent, recheck, retry = repair
                        db.execute(parent)
                        self.assertEqual(db.execute(recheck).fetchall(), [])
                        db.execute(retry)
                    else:
                        db.execute(rollback)
                    self.assertFalse(db.in_transaction)
                with closing(sqlite3.connect(path)) as observer:
                    expected = [(10, 1), (20, 2)] if keep else [(10, 1)]
                    self.assertEqual(observer.execute(verify).fetchall(), expected)
                    self.assertEqual(observer.execute(check).fetchall(), [])

    def test_turning_on_foreign_keys_inside_an_open_transaction(self):
        with closing(sqlite3.connect(":memory:", isolation_level=None)) as db:
            db.execute("PRAGMA foreign_keys = OFF")
            db.execute("BEGIN")
            enable, status = SQL[0]
            db.execute(enable)
            self.assertEqual(db.execute(status).fetchone(), (0,))
            db.execute("ROLLBACK")
            db.execute(enable)
            self.assertEqual(db.execute(status).fetchone(), (1,))


if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]}, SQLite {sqlite3.sqlite_version}", flush=True)
    unittest.main()
