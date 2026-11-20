# Find a literal version string with ripgrep

Run these searches from the directory you want to inspect. In ripgrep 15.2.0,
`-F` treats the dot in `v2.0` literally. Use `-l` to print each matching
filename once. The final `.` makes the directory the search input, including
when you run the command from a script.

```sh
rg -l -F 'v2.0' .
```

Suppose `notes.txt`, `.client.txt` and `generated.txt` all contain `v2.0`,
`other.txt` contains `v2x0`, and `.ignore` lists `generated.txt`. The
search above prints just `notes.txt`. To include the hidden client file
and still respect the ignore rule, use the following command.

```sh
rg --hidden -l -F 'v2.0' .
```

Expect both `.client.txt` and `notes.txt` in any order. The printed paths
may begin with `./` or its Windows equivalent.

## Interpret an empty result

```sh
rg -l -F 'v9.9' .
```

With these files, exit code **1** and empty output mean the search finished
without a match. A missing input path also gives you no matching filenames,
but ripgrep writes a diagnostic to standard error and returns **2**. Try
this with a path you know is absent.

```sh
rg -l -F 'v2.0' missing-input.txt
```

For other ignore rules and search modes, see the [ripgrep guide](https://github.com/BurntSushi/ripgrep/blob/e89fff89ac9af12e8d4ce9d5fd07beb408ca730f/GUIDE.md).
