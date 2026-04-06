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

## 2026-04-06 — Studio.app lives inside a "Studio 2.0" folder on macOS
**Context:** Launching or scripting BrickLink Studio on macOS
**Pattern:** The app is at `/Applications/Studio 2.0/Studio.app` (folder is "Studio 2.0", binary is Studio.app).
For `open -a` (app launch only): use full path `/Applications/Studio 2.0/Studio.app`.
For AppleScript `tell process`: use `"Studio"` (not "Studio 2.0").
**Confirmed:** 1 time (model_preview.sh automation)
**Sub-skill:** gui-navigation

## 2026-04-06 — Studio's default view is a good 45° perspective — capture first
**Context:** Automated screencapture of Studio models for QA/preview
**Pattern:** When Studio opens a file, it shows a 3/4 perspective view. Capture this FIRST,
before sending any numpad view-switch keys. After switching to orthographic views (Keypad 1/4/5),
the perspective is lost. Key codes for AppleScript: Keypad 1=83, 2=84, 3=85, 4=86, 5=87, 6=88.
**Confirmed:** 1 time (model_preview.sh v5+)
**Sub-skill:** gui-navigation

## 2026-04-06 — Clean Studio viewport for screenshots: three steps
**Context:** Preparing Studio for screencapture (panels and ground obscure the model)
**Pattern:** Send three keystrokes in sequence: Cmd+/ (hide all panels), Cmd+B (hide ground plane),
Escape (deselect all parts, removes selection highlights). Restore with Cmd+/ and Cmd+B again.
**Confirmed:** 1 time (model_preview.sh)
**Sub-skill:** gui-navigation

## 2026-04-06 — Scripts should be saved to project scripts/ and linked to recipes
**Context:** Creating scripts during working sessions
**Pattern:** When a task produces a working script (generator, modifier, packager, batch runner):
  1. Save to `projects/<name>/scripts/` with a clear filename and docstring
  2. If it's part of a pipeline, reference it in the corresponding recipe file in `recipes/`
  3. Update the project's `guide.md` scripts reference section
  4. List the script in the session summary
**Why:** Scripts are the primary reusable artifacts. Unsaved scripts are lost between sessions.
Binding them to recipes ensures they can be found and used consistently.
**Confirmed:** Recipe 1 pipeline (5 scripts), Recipe 2 pipeline (5 scripts), Coloring (3 scripts)
**Sub-skill:** general — applies to all project work
