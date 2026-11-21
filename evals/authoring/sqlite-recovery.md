# Recover a SQLite batch after a deferred foreign-key error

Use this procedure when an item belongs to a batch and SQLite reports
`FOREIGN KEY constraint failed` at `COMMIT`. The example imports item 20
for batch 2 into a practice database that already contains item 10 in batch 1.

> [!IMPORTANT]
> Keep the connection that received the error open. With a deferred constraint,
> the failed commit leaves the transaction open. Use that connection to check,
> repair or roll back the import.

## Start with enforcement on

On a fresh connection, before starting a transaction, run these statements.
Continue only if the query returns `1`. Changing the setting inside an
open transaction has no effect.

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

<details>
<summary>Create the practice tables in an empty database</summary>

Run these statements once, before the import transaction. The first two
records are already committed when the import begins.

```sql
CREATE TABLE batch (id INTEGER PRIMARY KEY);
CREATE TABLE item (
    id INTEGER PRIMARY KEY,
    batch_id INTEGER REFERENCES batch(id) DEFERRABLE INITIALLY DEFERRED
);
INSERT INTO batch VALUES (1);
INSERT INTO item VALUES (10, 1);
```

</details>

## Identify the missing parent

Send each statement on the same connection. The insert succeeds. The
commit raises the error because batch 2 does not exist yet.

```sql
BEGIN;
INSERT INTO item VALUES (20, 2);
COMMIT;
```

After the error, run the check. The practice database returns one row,
`item | 20 | batch | 0`. It identifies the child table, child row ID,
parent table and foreign-key index. The `2` to look up comes from the
imported item's `batch_id`.

```sql
PRAGMA foreign_key_check(item);
```

## Choose one recovery path

**Repair** if the source records confirm batch 2 belongs in this database.
Insert the parent, run the check again and commit once the check returns
zero rows.

```sql
INSERT INTO batch VALUES (2);
PRAGMA foreign_key_check(item);
COMMIT;
```

**Abandon the import** if the parent cannot be confirmed. Roll back the
open transaction.

```sql
ROLLBACK;
```

Reopen the database and verify the result. Repair leaves items 10 and 20
in batches 1 and 2. Rollback leaves only the original item 10 in batch 1.

```sql
SELECT id, batch_id FROM item ORDER BY id;
```

[SQLite deferred foreign keys](https://www.sqlite.org/foreignkeys.html#fk_deferred) · [Reading the check result](https://www.sqlite.org/pragma.html#pragma_foreign_key_check) · [SQLite 3.45.3 foreign-key tests](https://github.com/sqlite/sqlite/blob/b74eb00e2cb05d9749859e6fbe77d229ad1dc1e1/test/e_fkey.test)
