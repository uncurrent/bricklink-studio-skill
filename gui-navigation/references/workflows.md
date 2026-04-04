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

## Workflow 7: Render a Photo-Realistic Image

1. Position camera: hold `Alt` + right-click drag to orbit, zoom to compose shot
2. Render → Photo Realistic Render (`F11`)
3. In dialog:
   - Resolution: 1920×1080 for presentation, 800×600 for drafts
   - Quality: Draft (fast) or High (slow, better)
4. Click **Render** — progress bar appears
5. When complete: File → Save Render → choose PNG/JPG
