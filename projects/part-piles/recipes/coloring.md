---
name: Palette Coloring
version: 1
project: part-piles
status: verified
created: 2026-04-06
updated: 2026-04-06
---

## Purpose

Apply color palettes to generated .io pocket files — recoloring all parts using weighted random selection from a named palette. This is a **post-processing recipe** that chains after Recipe 1 or Recipe 2.

## Inputs

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| input | path | required | — | Single .io file or directory of .io files |
| palette | string | "all" | see palette list | Palette name, or "all" to apply every palette |
| output | path | required | — | Output .io file or directory |

### Available palettes (11)

| Palette | Theme |
|---------|-------|
| multicolor-1 through multicolor-6 | Rainbow variations with different weight distributions |
| sunset-warm-1 | Warm: reds, oranges, yellows |
| ocean-cool-1 | Cool: blues, teals, greens |
| primary-bold-1 | Classic LEGO: red, blue, yellow, green |
| pastel-party-1 | Light pastel tones |
| neon-punch-1 | Vivid saturated colors |

Palettes are defined in `scripts/coloring/color_palettes.py` as dictionaries mapping LDraw color IDs to weights.

## Pipeline

### Single file, single palette
- **Script:** `scripts/coloring/modifier_colorize.py`
- **Command:** `python3 modifier_colorize.py input.io --palette neon-punch-1 -o output.io`
- **Output:** Recolored .io file

### Batch: all files × all palettes
- **Script:** `scripts/coloring/batch_colorize.py`
- **Command:** `python3 batch_colorize.py input_folder/ output_folder/`
- **Output:** For each input .io × each palette → `output_folder/{name} ({palette}).io`

## Batch Usage

Full end-to-end with Recipe 1:
```bash
# Step 1: Generate pockets
cd scripts/recipe-1 && ./batch_generate.sh

# Step 2: Colorize all pockets with all palettes
cd ../coloring
python3 batch_colorize.py ../recipe-1/output/ colored/
# → colored/Pocket 15 (multicolor-1).io
# → colored/Pocket 15 (sunset-warm-1).io
# → ... (11 palettes × N pockets)
```

## Output Spec

- **Format:** .io (same structure as input, only color values in model.ldr changed)
- **Naming:** `{original_name} ({palette-name}).io`
- **Location:** Output directory
- **Quality criteria:** All parts recolored, no structural changes, palette visually distinguishable

## Known Limitations

- MONO_ palettes (MONO_BLUE, MONO_RED, etc.) are defined as placeholders but not yet implemented
- Color assignments are fully random within the palette — no spatial coherence (e.g., no gradient from center to edge)
- Palette weights are fixed — no per-part-type color weighting (a plate gets same color distribution as a brick)
- Does not preserve original colors — every part is recolored

## History

Developed as a standalone post-processing step in the Pockets-coloring session. The coloring system was designed to be recipe-agnostic: it takes any .io file and recolors it, regardless of which generation recipe produced it.
