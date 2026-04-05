# Confirmed Patterns

Validated discoveries promoted from `observations.md`.
These are reliable and should be used in future sessions.

Format per entry:
```
## YYYY-MM-DD — Short title
**Context:** when this applies
**Pattern:** what to do
**Confirmed:** how many times observed
**Sub-skill:** which sub-skill this belongs to (for eventual merge)
```

---

<!-- Confirmed patterns are appended below this line -->

## 2026-04-05 — Create ZIP files in /tmp, then copy to workspace
**Context:** Any time a shell command needs to create a ZIP (e.g. packaging a .io file)
**Pattern:** Build the ZIP in `/tmp`, then `cp` the result to the workspace:
```bash
cd /tmp && zip -r /tmp/output.zip file1 file2
cp /tmp/output.zip "/path/to/workspace/output.zip"
```
**Confirmed:** 3 times (Pockets 3, 4, 5)
**Sub-skill:** ldraw-format (applies to .io packaging), general shell usage

## 2026-04-05 — In file generators: write stats to stderr, data to file
**Context:** Python scripts that generate file content (LDR, CSV, JSON, etc.)
**Pattern:** Never mix diagnostic output with file output. Use `print(..., file=sys.stderr)` for stats/debug. Write the generated file with `open(path, 'w')`, not stdout.
**Confirmed:** 1 time (Pocket 5 generator)
**Sub-skill:** model-generation, general Python scripting
