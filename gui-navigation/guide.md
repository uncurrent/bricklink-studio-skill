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

**Prefer area screenshots over full screen.** Area screenshots are smaller, load faster,
and focus analysis on what matters. Full screenshots only when orientation is unknown.

### Taking an area screenshot (macOS)

Default shortcut: **Shift+Cmd+4** → drag to select area.

⚠️ Users often remap this shortcut. Before the first screenshot in a session, ask:
> "What's your screenshot shortcut, and does it save to file or clipboard?"

Common configurations:
- `Shift+Cmd+4` → saves PNG file to Desktop (macOS default)
- `Ctrl+Shift+Cmd+4` → saves to clipboard instead of file
- Custom tools (CleanShot, Shottr, etc.) — may use completely different shortcuts

**If saving to clipboard:** the image is immediately available to paste or upload.
**If saving to file:** ask for the path, or check Desktop for the latest PNG.

### After every action
1. Take a screenshot of the relevant area — not the full screen
2. Verify the expected change occurred
3. If UI is unexpected — check `references/panels.md` for orientation
4. If Studio shows an error dialog — read it, then decide: dismiss or address
5. If bricks show a **contour outline** (wire frame around the shape) — see Visual Indicators below

---

## Visual Indicators

### Contour outline on a brick (wire frame / ghost shape)

Studio renders non-active parts that overlap with the selected part as a contour/outline
rather than solid. If you see a brick rendered as just its outline shape:

- **Cause:** two or more bricks are occupying the same space (clipping through each other)
- **Meaning:** placement is wrong — this would be physically impossible with real LEGO
- **Fix:** move one of the overlapping parts to a valid snapped position
- **How to find them:** click the outlined brick → it will select; check its position in Properties

This is Studio's collision indicator. A correctly placed model should have no outlined bricks.

---

## Efficiency: Multi-Action Batching

When performing repetitive tasks (placing multiple parts, recoloring a set, adjusting positions),
try batching actions before verifying:

**Pattern:**
1. Plan a sequence of 2–4 related actions
2. Execute all of them
3. Take one area screenshot to verify the batch result
4. If correct → continue with next batch
5. If wrong → undo the batch (Cmd+Z multiple times), identify which step failed, retry one action at a time

**Learn and record:** if a multi-step sequence works reliably → note it in `learning/patterns.md`.
If it consistently fails or causes unexpected results → note in `learning/failed.md`.

This reduces screenshot overhead and speeds up long workflows significantly.

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
- `references/shortcuts.md` — Full keyboard shortcut reference (including WASD, arrows, F focus)
- `references/workflows.md` — Step-by-step common workflows
- `references/submodels.md` — Submodels: grouping, linked duplicates, Copy and Mirror, instructions
- `references/performance.md` — Performance tips for large models: snapping, collision, viewport quality

---

## Best Practices

### Camera & Navigation

- Press **F** to lock camera onto selected part — camera will orbit around it
- **Numpad 1–7** — switch camera views: Front / Back / Left / Right / Top / Bottom / Orthogonal
- **Tab** — toggle Building Palette visibility (more workspace)
- **Ctrl+/** — hide all panels

### Part Movement & Rotation

- **WASD** — move selected part freely (no snapping, no collision)
- **Arrow keys** — rotate 90°; **Shift + Arrow keys** — rotate 45°
- Rotation can be applied while moving a part
- **T** — open Translation ActionPalette (useful for rotated grouped objects — yellow square resets movement orientation)
- **R** — open Rotation ActionPalette
- **H** — Hinge Tool
- **C** — Clone Tool
- **L** — Hide Tool
- **V** — Default Select Mode

### Selection Tools

- **Select by Color** — select all parts of the same color (fast recoloring)
- **Select by Type** — select all parts of the same type
- **Select by Color and Type** — combination
- **Select by Connected** — select all parts connected to clicked part (essential before grouping hinged assemblies)
- **Invert Selection** — `Ctrl+Shift+V`

### Alignment

Select multiple parts → Right-click → **Align** → Top / Bottom / Left / Right / Near / Far.
Useful when parts were placed without snapping or need height alignment.

### Submodels — Key Patterns

- **Ctrl+G** — create submodel from selection (always give a meaningful name)
- **Ctrl+U** — release submodel
- **Shift+Ctrl+U** — release submodel recursively (nested)
- **Double-click** submodel — edit in place (wireframe of rest of model shown)
- Right-click → Submodel → **View** — edit in isolation (no distractions)

**Linked duplicates:** Copies of a submodel are automatically linked — editing one updates all.
To unlink: right-click → Submodel → Unlink.

**Nested submodels:** You can create submodels inside submodels for fine control.
Example: "Steam engine" → "Boiler" → "Chimney" (3–4 levels deep is common).

**Workflow for hinged assemblies:**
1. Select by Connected on the hinge part
2. Press Ctrl+G to group the result
3. Use Hinge Tool to rotate the group

### Performance on Large Models

- Dragging large objects with snapping enabled checks every stud for connectivity — very slow.
  **Fix:** Disable snapping, set Grid to Plate Height, then use **Connect Tool** for precise attachment.
- Collision Detection is resource-heavy on large models.
  **Fix:** Lower Render Quality in Edit → Preferences → Appearance → Render quality.
- ⚠️ **NO AUTOSAVE** — save manually with Ctrl+S frequently. Make periodic file backups.
  Studio can corrupt instruction layouts on large models when editing step views.

---

## Instruction Maker — Full Workflow

### Part 1: Prepare Model Before Entering Instruction Maker

Before opening Instruction Maker, structure the model into logical submodels:
- Identify sections built independently: removable roofs, wheel sets, window assemblies
- Create each as its own submodel (Ctrl+G)
- Use linked submodels for repeated elements (chairs, columns, etc.)
- Nested submodels work — divide as deep as needed

### Part 2: Dividing Into Steps

**Two approaches — use whichever fits:**

**Build Mode (Step List sidebar):**
- Step List visible in right sidebar
- Select parts → Right-click → MoveTo → New Step (or existing step)
- Drag parts between steps
- Easier to edit model simultaneously; harder to keep overview

**Instruction Maker (preferred for complex models):**
- Click "Instruction" button at top to switch modes
- Left sidebar: all steps; Bottom drawer: parts in current step; 3D view: current step + wireframe of previous
- Select parts for step 1 → click "Move to new: Step Before"
- Repeat for each step
- For complex models: rough split into 3–4 big steps first, then subdivide
- Submodels appear as single items in drawer — move them like any part
- To create steps inside a submodel: select it → "View Steps" → divide → "Return to Parent"

### Part 3: Page Design

**Setup:**
- Page Setup button → page size, margins, color mode
- Global Style panel (right sidebar) → overall look of instructions

**Step views:**
- Click page → "Change Step View" → adjust Model Orientation + Scale + Camera Setup
- When changing orientation mid-build: add a **Flip symbol** (Insert → Flip Indicator)
- Enable auto-flip: Preferences → General → "Auto flip symbol"
- Move model on page by hovering until blue rectangle appears, then drag
- Previous step shown as transparent ghost to help alignment

**Page Layout:**
- "Change Layout" → multiple steps per page (good for compact submodels)
- "Apply" affects current page; "Apply to followings" — current + all after

**Callouts (for small submodels ≤3 steps):**
- Select submodel pages → "Convert to Callout" → all steps go into a beige box
- Position callout box anywhere on page; add arrow pointing to placement location
- To undo: "Convert Back to Steps"

**Buffer Exchange (show part offset with arrow):**
- Hover over part → turquoise box appears → click part
- Sidebar: "Activate Buffer Exchange" button
- Enter X/Y/Z offset values manually (drag arrows may not work — known bug)
- Arrow appears automatically; reposition by clicking it

**Bill of Materials:**
- Add empty page at end → Insert → Bill of Materials
- Auto-generates full parts list across as many pages as needed

**Export:**
- Green "Export" button → choose pages (All or range) → format (PDF or PNG) → quality (1x / 2x / 4x)

---

## See Also

- Automation scripts like `model_preview.sh`: `projects/*/scripts/` (automated preview generation)
- GUI workflows and advanced patterns: `references/workflows.md`
- For complex interactive tasks, scripts can automate repetitive Studio actions