# Triage a CSV row before importing it

For a file with the header `id,place`, check the number of fields before
deciding whether a place is blank. A quoted comma belongs to the place name.
A trailing comma supplies an empty string. A row that ends after the ID
has no place field.

| CSV row | Parsed `place` | Extra fields | Import decision |
| --- | --- | --- | --- |
| `A1,"North, Bay"` | `'North, Bay'` | `[]` | Keep the full name |
| `B2,` | `''` | `[]` | Apply the importer's blank-value policy |
| `C3` | `None` | `[]` | Request the missing field |
| `D4,West,annex,upper` | `'West'` | `['annex', 'upper']` | Hold the row for column mapping |

The decisions in the last column are this importer's policy. Python exposes
the field values and leaves those decisions to the caller.

<details>
<summary>Copy the four rows into records.csv</summary>

```csv
id,place
A1,"North, Bay"
B2,
C3
D4,West,annex,upper
```

</details>

## Inspect the values

Run this Python 3 example from the directory containing `records.csv`.
`DictReader` takes column names from the header. This file reserves
`_extra` for overflow and uses `None` for a missing value. The example
prints an empty list when a row has no overflow.

```python
import csv

with open("records.csv", encoding="utf-8", newline="") as stream:
    rows = csv.DictReader(stream, restkey="_extra", restval=None)
    for row in rows:
        print(row["id"], repr(row["place"]), row.get("_extra", []))
```

Check the second and third lines first. They should read `B2 '' []` and
`C3 None []`. Converting both values to an empty string would lose the
distinction before the row reaches triage. [Python 3.12 CSV reference](https://docs.python.org/3.12/library/csv.html#csv.DictReader) · [Manual at the tested CPython revision](https://github.com/python/cpython/blob/2dc476bcb9142cd25d7e1d52392b73a3dcdf1756/Doc/library/csv.rst)
