---
name: Gaussian Pile Generation
version: 3
project: part-piles
status: verified
created: 2026-04-05
updated: 2026-04-06
---

## Purpose

Generate natural-looking random LEGO part piles as .io files for the Brickit Pockets feature, using Gaussian rejection sampling with rotation-aware AABB collision detection.

## Inputs

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| name | string | required | — | Pocket display name, e.g. "Pocket 20" |
| size | enum | medium | small, medium | Pile size preset (controls sigma, GAP, Y_MAX) |
| seeds | int pair | varies | any non-overlapping range | Seed range for multi-seed search, e.g. 900 980 |
| fill_seed | int | 42 | any | Seed for fill_gaps modifier randomness |

### Size presets

| Parameter | Small | Medium |
|-----------|-------|--------|
| SIGMA_X | 44 | 58 |
| SIGMA_Z | 32 | 46 |
| GAP | 2 LDU | 4 LDU |
| Y_MAX | 300 | 340 |
| MAX_TRIES | 1200 | 1500 |
| N_SEEDS | 60 | 80 |
| Typical forced | 0–2% | 0% |

**Medium is the production standard.** 0% forced on every seed tested (480+ seeds across P14–P19).

## Pipeline

### Step 1: Generate base pile
- **Script:** `scripts/recipe-1/generator_pile.py`
- **Command:** `python3 generator_pile.py --name "Pocket N" --size medium --seeds 900 980 -o /tmp/p.ldr`
- **Output:** .ldr file with 66 parts, best seed selected automatically

### Step 2: Fill visual gaps
- **Script:** `scripts/recipe-1/modifier_fill_gaps.py`
- **Command:** `python3 modifier_fill_gaps.py /tmp/p.ldr /tmp/pf.ldr --seed 42`
- **Output:** .ldr file with 66 + ~25 fill parts (91 total), coverage 86–100%

### Step 3: Gravity settle
- **Script:** `scripts/recipe-1/modifier_settle_y.py`
- **Command:** `python3 modifier_settle_y.py /tmp/pf.ldr /tmp/ps.ldr`
- **Output:** .ldr file with same parts, Y-compacted (8–17% shorter)

### Step 4: Package as .io
- **Script:** `scripts/recipe-1/packager_io.sh`
- **Command:** `bash packager_io.sh /tmp/ps.ldr "output/Pocket N.io" 91`
- **Output:** .io file (ZIP archive) ready for Stud.io

## Batch Usage

```bash
cd scripts/recipe-1
./batch_generate.sh
# Generates multiple pockets through the full 4-step pipeline
# Edit batch_generate.sh to configure pocket names, seed ranges, and output paths
```

End-to-end with coloring:
```bash
./batch_generate.sh
cd ../coloring
python3 batch_colorize.py ../recipe-1/output/ colored_output/
```

## Output Spec

- **Format:** .io (ZIP containing model.ldr + .info + errorPartList.err)
- **Naming:** `Pocket {N}.io` — model.ldr header uses `0 Name: Pocket {N}.ldr`
- **Location:** `output/` subfolder (configurable)
- **Quality criteria:** 0% forced placements (Medium), natural pile appearance from top-down, ~91 parts total, 86–100% visual coverage

## Known Limitations

- Small size still produces 0–2% forced and visible overlaps at GAP=2 in Stud.io
- Fill palette has 25 parts — coverage caps at ~88% average (100% with lucky seed)
- settle_y only reduces height 8–17% because triangular Y already biases to bottom
- Render settings not calibrated for Medium size — camera may need zoom adjustment

## History

Evolved across P1–P19. Key milestones:
- P4–P5: Y-only rotation + fixed ellipsoid BV → 25% overlap (see `scripts/archive/`)
- P6: v3 rotation-aware AABB breakthrough → 8% forced (`scripts/archive/gen_pocket6.py`)
- P7: Tight sigma + tall Y → 0% forced (Small)
- P8–P10: Flat pile experiments (`scripts/archive/gen_pocket9.py`, `gen_pocket10.py`)
- P11: 4-layer coverage system concept (`scripts/archive/gen_pocket11.py`)
- P13: Small size final (`scripts/archive/gen_pocket13.py`)
- P14: Medium size debut + fill_gaps + settle_y (`scripts/archive/gen_pocket14.py`)
- P15–P19: Batch validation — production pipeline confirmed
