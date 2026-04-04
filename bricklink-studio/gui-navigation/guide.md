---
name: bricklink-studio/gui-navigation
description: >
  Navigate BrickLink Studio GUI via Computer Use. Use for: placing parts, changing colors,
  moving/rotating elements, rendering images, saving files, building instructions.
  REQUIRES computer_use tool with display. Not available in claude.ai chat or API without display.
compatibility:
  required_tools: [computer_use, display]
---

# GUI Navigation — BrickLink Studio

> **Language policy:** All entries written to skill files during this session must be in English.
> The user interface may be in any language.


> ⚠️ This sub-skill requires **Computer Use with display access** (Cowork).
> If not available, use `model-generation` + `ldraw-format` instead.

---

## Startup Checklist

Before doing anything in Studio:
1. Take a screenshot to see current state
2. Check if Studio is open — if not, launch it
3. Identify which panel is active (see `references/panels.md`)
4. Confirm the correct model file is loaded

---

## Core Interaction Patterns

### Placing a Part
1. Open Parts palette (left panel or `B` key)
2. Search by Part ID or name in the search bar
3. Click part → it attaches to cursor
4. Click in viewport to place
5. Use arrow keys or handles to adjust position
6. Press `Escape` to deselect

### Changing Color
1. Select part(s) in viewport (click or drag-select)
2. Open Color panel (right panel or `C` key)
3. Click desired color swatch
4. Verify change in viewport

### Moving / Rotating
1. Select part(s)
2. Use transform handles in viewport, or
3. Use `W` (move), `E` (rotate), `R` (scale) hotkeys
4. For precise placement: right-click → Properties → enter coordinates

### Saving
- `Ctrl+S` — save as `.io`
- File → Export → LDraw → saves as `.ldr`/`.mpd`

---

## Screenshot Analysis Protocol

After every action:
1. Take screenshot
2. Verify the expected change occurred
3. If UI is unexpected — check `references/panels.md` for orientation
4. If Studio shows an error dialog — read it, then decide: dismiss or address

---

## Rendering

1. Go to **Render** menu → **Photo Realistic Render** (or press `F11`)
2. Set resolution and quality in dialog
3. Click **Render**
4. Wait for completion (can take 30s–5min depending on complexity)
5. Save output via **File → Save Render**

---

## Reference Files

- `references/panels.md` — UI layout, panel locations, what each area does
- `references/shortcuts.md` — Full keyboard shortcut reference
- `references/workflows.md` — Step-by-step common workflows
