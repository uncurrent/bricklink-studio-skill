---
name: 4-Angle Model Preview
version: 1
project: part-piles
status: draft
created: 2026-04-06
updated: 2026-04-06
---

## Purpose

Automatically capture 4-angle preview screenshots of .io models in BrickLink Studio for batch QA review — without manually opening each file.

## Inputs

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| folder | path | required | — | Directory containing .io files |
| force | flag | false | — | Regenerate previews even if _preview/ folder exists |

## Pipeline

### Step 1: Batch capture
- **Script:** `projects/part-piles/scripts/preview/model_preview.sh`
- **Command:** `./model_preview.sh ./output` or `./model_preview.sh --force ./output`
- **Output:** For each .io file: `{filename}_preview/` folder with 4 PNG screenshots

### Screenshots captured

| Image | View | Method |
|-------|------|--------|
| `perspective_45.png` | 3/4 perspective (Studio default) | Captured first, before any view switch |
| `front_Z.png` | Front view | Keypad 1 (key code 83) |
| `right_X.png` | Right view | Keypad 4 (key code 86) |
| `top_Y.png` | Top view | Keypad 5 (key code 87) |

### Viewport preparation (3 steps)

1. `Cmd+/` — hide all panels
2. `Cmd+B` — hide ground plane
3. `Escape` — deselect all parts

After each view switch: `Cmd+0` (Zoom to Fit) + 1 second settle wait.

## Batch Usage

```bash
# After generating pockets with Recipe 1:
cd ~/Dev/BrickitStudio
./model_preview.sh ./Pockets-recipe-1/output

# Force regeneration:
./model_preview.sh --force ./Pockets-recipe-1/output
```

## Output Spec

- **Format:** PNG screenshots
- **Naming:** `{filename}_preview/{view}.png`
- **Location:** Next to the original .io file
- **Quality criteria:** Model centered and visible in each view, no panels/ground/selection artifacts

## Known Limitations

- **macOS only** — requires AppleScript + `screencapture` command
- **BrickLink Studio must be installed** at `/Applications/Studio 2.0/Studio.app`
- **Terminal must have Accessibility permission** (System Settings → Privacy & Security → Accessibility)
- Files are opened via AppleScript-driven File → Open dialog (Cmd+O → Cmd+Shift+G → path) because Studio does not support `open -a` for .io files
- `screencapture -R` with System Events bounds approach — not fully tested on Retina/multi-monitor setups
- LOAD_WAIT=8 seconds per file — may need increase for complex models
- No auto-cropping — screenshots include empty space around the model

## History

Developed as a QA tool after batch generation pipeline was established. Went through 6 versions:
- v1–v2: `open -a` approach (failed — Studio doesn't support it)
- v3: AppleScript File → Open dialog (works)
- v4: Quartz CGWindowID capture (failed — unreliable)
- v5: Backtick perspective toggle (failed — key doesn't register)
- v6: System Events bounds + capture default perspective first (current)
