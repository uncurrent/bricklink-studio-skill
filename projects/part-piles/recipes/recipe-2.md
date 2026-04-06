---
name: Sequential Crystal-Growth Top Layer
version: 4
project: part-piles
status: verified
created: 2026-04-06
updated: 2026-04-06
---

## Purpose

Generate a flat spread of LEGO parts viewed from above using sequential outward placement from center — each part touches an existing part without XZ overlap. Produces a different visual style than Recipe 1: a single layer of tightly packed parts with varied orientations.

## Inputs

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| name | string | "Pocket 12" | — | Pocket display name |
| n_seeds | int | 60 | 1–200 | Number of seeds to search for best result |
| oval_a | int | 185 | 150–250 | Placement oval X half-size (LDU) |
| oval_b | int | 145 | 120–200 | Placement oval Z half-size (LDU) |
| n_parts_max | int | 50 | 20–80 | Max parts in palette (not all will be placed) |
| apply_rotation_shuffle | bool | true | — | Apply rotation variety modifier |
| apply_fill | bool | true | — | Apply small parts gap fill modifier |

### Key algorithm parameters (v4)

```python
GAP       = 0       # no XZ overlap
N_ANGLES  = 96      # touch-point direction candidates per existing part
TOP_K     = 10      # pick randomly from top-K closest-to-center positions
TILT      = {"brick": 0.40, "plate": 0.07, "tile": 0.04}
```

## Pipeline

### Step 1: Generate base top layer
- **Script:** `scripts/recipe-2/generator_toplayer_v4.py`
- **Command:** Used as module (imported by driver script)
- **Output:** .ldr with ~31 parts placed sequentially outward from center

### Step 2 (optional): Rotation shuffle
- **Script:** `scripts/recipe-2/modifier_rotation_shuffle.py`
- **Command:** Used as module
- **Output:** Same positions, varied orientations (50% upright, 20% leaning, 17% on-side, 5% upside-down, 8% extreme)

### Step 3 (optional): Fill small parts
- **Script:** `scripts/recipe-2/modifier_fill_small_parts.py`
- **Command:** Used as module
- **Output:** +20 small fill parts added via Monte Carlo placement (EXISTING_SCALE=0.65)

### Driver (runs all steps)
- **Script:** `scripts/recipe-2/generator_toplayer_with_modifiers.py`
- **Command:** `python3 generator_toplayer_with_modifiers.py`
- **Output:** Three variants: B (rotation shuffle), C (gap fill), D (both modifiers)

## Batch Usage

```bash
cd scripts/recipe-2
python3 batch_generate.py
# Generates multiple pockets with all modifier variants
```

End-to-end with coloring:
```bash
python3 batch_generate.py
cd ../coloring
python3 batch_colorize.py ../recipe-2/output/ colored_output/
```

## Output Spec

- **Format:** .io (or .ldr intermediates)
- **Naming:** `Pocket {N} (base-v4).io`, `Pocket {N}-B (rotation-shuffle).io`, `Pocket {N}-C (small-fillers).io`, `Pocket {N}-D (both-mods).io`
- **Location:** `output/` subfolder
- **Quality criteria:** 0 XZ overlaps, ~31 base + 20 fill = ~51 parts total, varied part orientations, tight packing

## Known Limitations

- Only generates a top layer — no multi-layer full pile yet
- Only ~31 of 50 parts fit in the oval (remaining 19 can't find valid XZ positions — expected)
- AABB-based collision at 45° rotation inflates extents — slight axis-alignment bias remains
- modifier_fill_small_parts uses EXISTING_SCALE=0.65 approximation — some fill parts may visually overlap heavily tilted bricks
- No packager step yet — .io packaging is done inline in the batch script

## History

Evolved across P12 v1–v4:
- v1: N_ANGLES=8, all plates, always-closest → mechanical concentric rings (`scripts/archive/gen_pocket12_toplayer_v1.py`)
- v2: Continuous rotation, GAP=-4 → massive overlaps (`scripts/archive/gen_pocket12_toplayer_v2.py`)
- v3: XZ-only collision, bricks added, GAP=-6 → still overlaps (`scripts/archive/gen_pocket12_toplayer_v3.py`)
- v4: GAP=0, oval 185×145, N_ANGLES=96, TOP_K=10 → production quality (`scripts/archive/gen_pocket12_toplayer_v4.py`)
- Modifiers: rotation_shuffle + fill_small_parts (`scripts/archive/gen_pocket12_BCD.py`)
