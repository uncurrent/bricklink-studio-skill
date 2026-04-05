# BrickLink Studio — Common Workflows

## Workflow 1: Start a New Model from Scratch

1. Launch Studio → File → New (or `Ctrl+N`)
2. Choose **Blank** template
3. Set baseplate if needed: search `baseplate` in Parts, place first
4. Begin adding structural parts (see model-generation skill for LDraw approach)

---

## Workflow 2: Open an Existing LDraw File

1. File → Open (`Ctrl+O`)
2. In dialog, change file type filter to **LDraw Files (*.ldr *.mpd)**
3. Navigate to file, click Open
4. Wait for parts library to resolve (first open may be slow)
5. Take screenshot to confirm model loaded correctly

---

## Workflow 3: Build a Simple Wall

1. Search parts palette for `3001` (2x4 brick)
2. Place first brick at origin
3. Hold `Ctrl` and click to place additional bricks in a row
4. For second row: select all bricks in row 1 → `Ctrl+D` to duplicate
5. Move duplicate up by 1 brick height (use Y offset = 24 LDU in Properties)
6. Offset by half-brick for staggered pattern (X offset = 20 LDU)

---

## Workflow 4: Change Colors of Multiple Parts

1. Drag-select all parts to recolor (or `Ctrl+click` individual parts)
2. Press `C` to open color panel
3. Filter by color family or search by name (e.g. "red", "dark bluish gray")
4. Click color swatch — all selected parts change instantly
5. Take screenshot to verify

---

## Workflow 5: Export to LDraw for BOM/Analysis

1. File → Export → LDraw
2. Choose destination folder
3. Set filename (`.ldr` for single model, `.mpd` for multi-step instructions)
4. Click Export
5. File is ready for `ldraw-format` or `bom-export` sub-skills

---

## Workflow 6: Create Building Instructions

1. Switch to **Instructions** mode (top toolbar toggle)
2. Each step = one group of parts
3. Select parts added in step N → click `+` in Step Panel
4. Repeat for each step
5. File → Export → PDF Instructions to generate printable PDF

---

## Workflow 7: Replace Parts (UI)

1. Open the model in Studio
2. In the **Step List** (right panel) — click a part to highlight it in the viewport
3. Click the **REPLACE** tab (top-left corner)
4. Type the desired part name or ID in the search field
5. Double-click the replacement part — applied immediately

**Multi-replace:** Cmd+click multiple parts in Step List → double-click replacement.
All selected parts of the same type will be replaced simultaneously.

**Known issues:**
- Cmd+A in the REPLACE search field types "a" instead of selecting all — use the × button to clear
- Mixed selection of different part types → REPLACE may find no candidates — replace one type at a time
- Studio **auto-saves** changes without warning — undo (Cmd+Z) works but does not always roll back everything
- If the file is corrupted after editing — restore from git

---

## Workflow 8: Create a Random Pile of Parts

Studio has no physics or scatter tools — pile appearance is achieved manually:

1. Place all parts in the viewport at approximately the desired XZ footprint
2. Set different Y values (height) for each part — parts "float" at different levels
3. Apply arbitrary rotations (use R during placement or rotate in Properties)
4. Lock camera to **top-down view** (camera lock button in viewport)
5. From above, a group of parts at varied heights and angles reads as a realistic pile
6. Export to LDraw when the top-down composition looks correct

**For physically realistic piles:** export to Blender → apply Rigid Body simulation →
parts settle under gravity. See `references/blender-pipeline.md`.

---

## Workflow 9: Export to Blender for Rendering

Best results for photorealistic LEGO visualization:

1. In Studio: **File → Export → LDraw** → save as `.ldr` or `.mpd`
2. In Blender, import via one of:
   - `ExportLDraw` — supports .ldr, .mpd, .l3b
   - `ldr_tools_blender` — optimized for large scenes (100k+ parts), uses instancing
   - `ImportLDraw` — standard importer
3. Apply Rigid Body physics for natural settling (Active on parts, Passive on ground plane)
4. Render with Cycles — LEGO materials and stud logos render correctly

**For scenes with 10k+ parts:** use Geometry Nodes instancing and set display to Normal resolution.

---

## Workflow 10: Render a Photo-Realistic Image

1. Position camera: hold `Alt` + right-click drag to orbit, zoom to compose shot
2. Render → Photo Realistic Render (`F11`)
3. In dialog:
   - Resolution: 1920×1080 for presentation, 800×600 for drafts
   - Quality: Draft (fast) or High (slow, better)
4. Click **Render** — progress bar appears
5. When complete: File → Save Render → choose PNG/JPG
