# Restore pip in a maintenance virtual environment

Use this runbook with uv 0.8.12 when `.maintenance` needs pip and
`.venv` belongs to the application. Start in their parent directory with
neither environment activated. Both must already exist. Place the single
approved pip wheel in `wheelhouse/` and note the version on its filename.

## Check the maintenance environment

```sh
uv --offline pip show --python .maintenance pip
```

If uv reports that it cannot find the package, continue to installation.
If it reports a version and location, check those first. An interpreter
error means you need to correct the environment path before installing.

## Install the approved wheel

```sh
uv --offline --no-cache pip install --python .maintenance --no-index --find-links ./wheelhouse pip
```

The command names the maintenance environment explicitly. It uses the wheel
directory with package indexes and the persistent cache disabled. If uv
cannot find a compatible wheel, stop and check the approved file.

## Verify both environments

```sh
uv --offline pip show --python .maintenance pip
uv --offline pip show --python .venv pip
```

The maintenance result should show the wheel's version and a `Location`
inside `.maintenance`. Compare the application environment with its original
state. An application environment that started without pip should still
report the package missing.

If pip was absent before this repair and you need to undo the installation,
use the same explicit target, then repeat the two verification commands.

```sh
uv --offline pip uninstall --python .maintenance pip
```

See uv's [environment selection](https://github.com/astral-sh/uv/blob/36151df0e4ac7103aa75399ea3ec6e63a697e0aa/docs/pip/environments.md) and [package operations](https://github.com/astral-sh/uv/blob/36151df0e4ac7103aa75399ea3ec6e63a697e0aa/docs/pip/packages.md).
