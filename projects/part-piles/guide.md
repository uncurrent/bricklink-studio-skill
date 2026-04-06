---
project: part-piles
status: active
created: 2026-04-05
updated: 2026-04-06
algorithm-version: v3 Recipe-1 / v4 Recipe-2
---

# Part Piles — Project Guide

Generate photorealistic renders of random LEGO part piles — used as app graphics,
"bag of parts" imagery, and decorative UI assets for the Brickit app.

---

## Goal

Final deliverable: top-down rendered PNG of a natural-looking pile of LEGO parts,
suitable for Brickit Pockets feature (visual representation of parts stored in a zip-lock bag).

---

## Pockets Overview

| File | Type | Parts | Notes |
|------|------|-------|-------|
| Pocket 1 | Manual (Stud.io) | 89 | Reference model for Small Size standard |
| Pocket 2 | Manual (part-swap of P1) | 89 | Part-swapped variant of P1, same positions |
| Pocket 3 | Generated v0 | 26 | Technic-heavy, all white — too sparse, no X/Z tilt |
| Pocket 4 | Generated v1 | 71 | First colorful pile — Y-rotation only, looks fake |
| Pocket 5 | Generated v2 | 71 | Full 3D + fixed ellipsoid BV — 25% overlap |
| Pocket 6 | Generated v3 | 66 | Rotation-aware AABB — ~8% forced ✓ |
| Pocket 7 | Generated v3+ | 65 | Tight sigma + tall Y_MAX → 0% forced, too tall |
| Pocket 8 | Generated v3+ | 65 | Reduced tilt + flat Y_MAX → 6% forced ✓ best flat |
| Pocket 9 | Generated v3+ | 65 | Two-layer floor+pile → 9% forced, Z exact match |
| Pocket 10 | Generated v3+ | 65 | P8 approach, SIGMA_Z=33 → 8% forced, Z=12.3 studs |
| Pocket 11 | Generated 4-layer | 61 | 4-layer coverage Y-separation → 3.3% forced ✓ |
| Pocket 12 (base) | Generated Recipe-2 v4 | 31 | Sequential outward placement, top-layer only |
| Pocket 12-B | Recipe-2 + rotation shuffle | 31 | Varied rotations (on-side, upside-down) |
| Pocket 12-C | Recipe-2 + gap fill | 51 | Gap-fill small parts added |
| Pocket 12-D | Recipe-2 + both mods | 51 | Rotation shuffle + gap fill |
| Pocket 13 | Generated v3+ | 66 | Small, P7 params, 2% forced |
| Pocket 14 | Generated v3+ Medium | 66 | **First Medium size**, 0% forced ✓ |
| Pocket 14-B | Recipe-1 + fill_gaps | 91 | P14 + 25 fill parts |
| Pocket 14-C | Recipe-1 + settle_y | 91 | P14-B settled → 8% shorter |
| Pocket 15–19 | Recipe-1 batch Medium | 91 ea | Batch validation, 0% forced, 86–100% coverage |

---

## Size Standards

### Small Size (reference: Pocket 1 & 2)

| Parameter | Value |
|-----------|-------|
| Parts count | ~89 (generated: 65–66) |
| Footprint X | ~354 LDU ≈ 17.7 studs |
| Footprint Z | ~264 LDU ≈ 13.2 studs |
| Pile height Y | ~208 LDU ≈ 26 plates |
| Pile center | X ≈ −100, Z ≈ −130 (LDU) |

### Medium Size (reference: Pocket 14)

| Parameter | Value |
|-----------|-------|
| Parts count | ~66 hero + 25 fill = 91 total |
| Footprint X | ~440 LDU ≈ 22 studs |
| Footprint Z | ~326 LDU ≈ 16.3 studs |
| Pile height Y | ~315 LDU ≈ 39 plates |
| Pile center | X ≈ −100, Z ≈ −130 (LDU) |

**Medium is the production standard** — 0% forced across all seeds, no visible overlaps in Stud.io.
Small is viable but has higher collision rates and visible overlap artifacts at GAP=2.

---

## Part Composition Recipe

### Shared part list (Recipe 1 & 2)

| Part | ID | Category | Dims (half LDU) |
|------|----|----------|-----------------|
| Brick 2×4 | 3001.dat | brick | (40,12,20) |
| Brick 2×2 | 3003.dat | brick | (20,12,20) |
| Brick 1×2 | 3004.dat | brick | (20,12,10) |
| Brick 1×4 | 3010.dat | brick | (40,12,10) |
| Brick 1×1 | 3005.dat | brick | (10,12,10) |
| Plate 1×2 | 3023.dat | plate | (20, 4,10) |
| Plate 2×2 | 3022.dat | plate | (20, 4,20) |
| Plate 2×4 | 3020.dat | plate | (40, 4,20) |
| Plate 1×4 | 3710.dat | plate | (40, 4,10) |
| Plate 2×8 | 3034.dat | plate | (80, 4,20) |
| Plate 2×6 | 3795.dat | plate | (60, 4,20) |
| Plate 2×3 | 3021.dat | plate | (30, 4,20) |
| Slope 45° 2×2 | 3039.dat | accent | (20,14,20) |
| Slope 45° 2×1 | 3040b.dat | accent | (20,14,10) |
| Brick 1×1 Round | 3062b.dat | accent | (10,12,10) |
| Tile 2×2 Round | 14769.dat | accent | (20, 3,20) |
| Plate 1×1 Round | 4073.dat | accent | (10, 3,10) |
| Tile 1×2 | 3069b.dat | accent | (20, 3,10) |
| Tile 2×2 | 3068b.dat | accent | (20, 3,20) |

**Composition guidelines:**

| Category | Share | Notes |
|----------|-------|-------|
| Base bricks | ~35% | 2×4 ×6, 2×2 ×5, 1×2 ×4, 1×4 ×3, 1×1 ×3 |
| Base plates | ~30% | 2×8 ×2, 2×6 ×2, 2×4 ×4, 2×3 ×2, 1×4 ×3, 2×2 ×3, 1×2 ×4 |
| Accent parts | ~35% | slopes, curved slopes, round tiles, tiles |
| Technic | accent only | max 2–3 pcs total |

Must-haves: 2×4 bricks ×5+, 2×2 bricks ×4+, 1×2 bricks ×4+, 2×4 plates ×3+, 2×8 plate ×2.

---

## Core Algorithms

### Rotation-aware AABB (shared by both recipes)

Fixed bounding volumes ignore orientation — a plate standing on its edge needs ey≈40 LDU, not 5.
Always compute AABB from the rotation matrix:

```python
def compute_half_extents(dims, R):
    a, b, c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ey = abs(R[1][0])*a + abs(R[1][1])*b + abs(R[1][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ey, ez
```

### Rotation matrix R = Ry × Rx × Rz

```python
def make_R(tilt_strength, rng):
    ry = math.radians(rng.uniform(-180, 180))
    r = rng.random()
    if r < 0.55:       # Gaussian tilt — natural slight wobble
        s = 10 + 35 * tilt_strength
        rx = math.radians(rng.gauss(0, s))
        rz = math.radians(rng.gauss(0, s))
    elif r < 0.80:     # Uniform moderate tilt
        lim = 35 + 70 * tilt_strength
        rx = math.radians(rng.uniform(-lim, lim))
        rz = math.radians(rng.uniform(-lim, lim))
    else:              # Fully random — upside-down, on edge, etc.
        rx = math.radians(rng.uniform(-180, 180))
        rz = math.radians(rng.uniform(-180, 180))
    cy,sy = math.cos(ry),math.sin(ry)
    cx,sx = math.cos(rx),math.sin(rx)
    cz,sz = math.cos(rz),math.sin(rz)
    def mm(A,B): return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(mm([[cy,0,sy],[0,1,0],[-sy,0,cy]], [[1,0,0],[0,cx,-sx],[0,sx,cx]]), [[cz,-sz,0],[sz,cz,0],[0,0,1]])
```

**Tilt strength by category:**

| Category | R1 (tall pile) | R1 (flat pile) | R2 |
|----------|----------------|----------------|----|
| Large plates (2×8, 2×6) | 0.18 | 0.10 | — |
| Base plates | 0.22–0.25 | 0.12–0.15 | 0.07 |
| Standard bricks 2×4/2×2 | 0.35–0.40 | 0.20 | 0.40 |
| Bricks 1×2/1×4 | 0.40–0.50 | 0.25 | 0.40 |
| Slopes / accent | 0.50–0.65 | 0.30–0.35 | — |
| Tiles | 0.60–0.70 | — | 0.04 |
| Technic / tiny 1×1 | 0.65–0.70 | 0.40–0.50 | — |

---

## Recipe 1 — Gaussian Rejection Sampling

### Pipeline

```
generator_pile.py  →  modifier_fill_gaps.py  →  modifier_settle_y.py  →  packager_io.sh
   (base pile)          (visual gap fill)          (gravity compact)         (.io archive)
```

Scripts location: `BrickitStudio/Pockets-recipe-1/`

### Running

```bash
cd BrickitStudio/Pockets-recipe-1

python3 generator_pile.py --name "Pocket 15" --size medium --seeds 400 460 -o /tmp/p.ldr
python3 modifier_fill_gaps.py /tmp/p.ldr /tmp/pf.ldr --seed 42
python3 modifier_settle_y.py /tmp/pf.ldr /tmp/ps.ldr
bash packager_io.sh /tmp/ps.ldr "output/Pocket 15.io" 91
```

### Generator algorithm

1. Sort parts by footprint area (largest first)
2. For each part: sample Gaussian XZ position + triangular Y position
3. Try up to MAX_TRIES random positions; accept first non-overlapping; otherwise use least-overlapping (forced)
4. Run over N_SEEDS seed values; return seed with fewest forced placements

```python
GAP = 4  # or 2 for Small
def overlaps(p1, p2):
    x1,y1,z1,ex1,ey1,ez1 = p1
    x2,y2,z2,ex2,ey2,ez2 = p2
    return (abs(x1-x2) < ex1+ex2+GAP and
            abs(y1-y2) < ey1+ey2+GAP and
            abs(z1-z2) < ez1+ez2+GAP)
```

### Parameters — two presets

| Parameter | Small (P7/P13) | Medium (P14–P19) |
|-----------|----------------|------------------|
| SIGMA_X | 44 | 58 |
| SIGMA_Z | 32 | 46 |
| GAP | 2 LDU | 4 LDU |
| Y_MAX | 300 | 340 |
| Y bias peak | Y_MIN+50 | Y_MIN+50 |
| MAX_TRIES | 1200 | 1500 |
| N_SEEDS | 60 | 80 |
| Forced overlap | ~0–2% | 0% |
| CX, CZ | -100, -130 | -100, -130 |

**Medium is production standard.** 0% forced on every seed tested (480+ seeds across P14–P19).

### modifier_fill_gaps.py

Fills top-down visual gaps with small parts after the base pile is generated.

**Algorithm:**
1. Parse LDR → compute rotation-aware AABBs for all parts
2. Build XZ coverage grid (GRID_RES=14 LDU per cell)
3. Apply VIS_FACTOR=0.60 to each AABB — accounts for visual footprint being smaller than AABB
4. Compute fill oval = 85% of actual model footprint (don't fill extreme edges)
5. Find uncovered cells within fill oval, sorted center-first
6. For each gap cell, try fill parts largest-first at 8 rotation angles
7. Fill parts placed at Y=220–310 (below main pile — Y-separation prevents collisions)
8. GAP=3 for fill placement

**Fill palette (25 parts):**

| Parts | Count |
|-------|-------|
| 1×2, 1×1, Round 1×1 Plates | 10 |
| 1×2, 1×1 Tiles | 6 |
| 1×1, 1×2, Round 1×1 Bricks | 6 |
| Gear 24T, Gear 8T, Technic Pin | 3 |

**Tilt strategy:** Plates/tiles near-flat (ts=0.12), bricks moderate (ts=0.35), Technic (ts=0.45).

**Coverage results on Medium pockets:** 72% → 86–100% (P19 hit 100%).

### modifier_settle_y.py

Simulates gravity: drops each part downward until it rests on another part or the floor.

**Algorithm:**
1. Parse all parts with rotation-aware AABBs
2. Auto-detect floor Y (max Y of all parts + largest ey + 20 LDU margin)
3. Sort parts by Y descending (bottom parts settle first — highest Y = closest to floor in LDraw coords)
4. For each part: find minimum Y satisfying all constraints from already-settled parts below
5. Only move parts downward (new Y ≥ original Y)
6. GAP=1 after settling (parts rest close together)

**Result:** ~8–17% height reduction. Fill parts at Y=220–310 drop down into the pile.

### Batch generation

```bash
# Pockets-recipe-1/batch_generate.sh — generates N pockets through full pipeline
./batch_generate.sh  # generates P15–P19 (or as configured)
```

Each pocket gets unique seed range; naming set via `--name "Pocket N"`.

---

## Recipe 2 — Sequential Outward Placement

### Pipeline

```
generator_toplayer_v4.py  →  [modifier_rotation_shuffle.py]  →  [modifier_fill_small_parts.py]
      (base top layer)              (orientation variety)              (gap fill)
```

Scripts location: `BrickitStudio/Pockets-recipe-2/`

### Running

```bash
cd BrickitStudio/Pockets-recipe-2

python3 generator_toplayer_with_modifiers.py
# → writes /tmp/pocket12B.ldr  /tmp/pocket12C.ldr  /tmp/pocket12D.ldr
```

Variant naming: Base = v4 only, B = rotation shuffle, C = small fillers, D = both mods.

### Generator algorithm (v4)

Parts placed one-by-one from center outward. Each new part is placed at the position that
touches an existing part (AABB just touching) closest to the oval center.

**Touch-point formula:**

```python
def touch_distance(ref_ex, ref_ez, new_ex, new_ez, ca, sa):
    """Distance to place new part touching reference part AABB in direction (ca, sa)."""
    aca, asa = abs(ca), abs(sa)
    if aca < 1e-9: return (ref_ez + new_ez + GAP) / asa
    if asa < 1e-9: return (ref_ex + new_ex + GAP) / aca
    dx = (ref_ex + new_ex + GAP) / aca  # distance to touch in X
    dz = (ref_ez + new_ez + GAP) / asa  # distance to touch in Z
    return min(dx, dz)                   # first axis to trigger
```

**Geometric interpretation:** For rectangular AABB, touching boundary in direction (ca,sa) is a
diamond shape. `min(dx, dz)` gives the correct position where the moving part first hits the
reference AABB perimeter.

**Key parameters (v4 base):**

```python
OVAL_A, OVAL_B = 185, 145   # placement oval (LDU)
GAP            = 0           # no XZ overlap
N_ANGLES       = 96          # touch-point direction candidates per existing part
TOP_K          = 10          # pick randomly from top-K closest-to-center positions
N_PARTS_MAX    = 50          # parts in palette (31 typically placed — oval fills up)
N_SEEDS        = 60          # best seed selection
TILT           = {"brick": 0.40, "plate": 0.07, "tile": 0.04}
```

**Why XZ-only collision:** A brick (ey=12) and plate (ey=2) beside each other in XZ would
always "collide" in Y. Y is assigned per-type as decoration after XZ placement:

| Part type | Y range |
|-----------|---------|
| Bricks (upright) | uniform(-30, -4) |
| Plates | uniform(-8, 8) |
| Tiles | uniform(-4, 6) |

**Why larger oval (185×145)?** A 2×4 plate at 45° has AABB (42.4, 42.4) — much larger than
axis-aligned (40, 20). Smaller oval would bias toward axis-aligned placements (0°/90°) because
only those consistently fit within a tight oval. GAP=0 + larger oval achieves the "nearly
touching" look intended.

### modifier_rotation_shuffle.py

Replaces rotations to create visual orientation variety (studs-up is too uniform).

| Mode | Probability | Description |
|------|-------------|-------------|
| Upright | 50% | Normal, small tilt `rx = gauss(0, 8°)` |
| Leaning | 20% | Medium tilt 15–35° |
| On-side | 17% | ≈90° shows side face from top |
| Upside-down | 5% | ≈180° shows anti-stud underside |
| Extreme | 8% | 45–70° dramatic diagonal |

Y positions adjusted per mode (on-side bricks use lower Y range).

### modifier_fill_small_parts.py

Fills gaps using **Monte Carlo placement** (not grid-based) because AABB of tilted bricks is
up to 2× the nominal size — grid detection would report zero gaps even when visual holes exist.

**EXISTING_SCALE=0.65** applied to nominal dims (not rotation-aware AABB) for collision:
`ex = dims[0] * 0.65` — same empirical value as P11 coverage correction.

```python
EXISTING_SCALE = 0.65   # 0.65 × nominal dims for gap detection
FILLER_GAP     = 4      # clearance for filler placement
```

**Filler palette:** 1×1/1×2 plates, tiles, bricks (various), Gear 24T (max 1), Gear 8T (max 1),
Technic Pin (max 1). Up to 20 fillers added.

---

## Coloring System

Location: `BrickitStudio/Pockets-coloring/`

### Scripts

| Script | What it does |
|--------|-------------|
| `modifier_colorize.py` | Reads LDR, reassigns all colors using weighted random from a named palette |
| `batch_colorize.py` | Takes a folder of .io files, applies all palettes, outputs to a target folder |

### 11 defined palettes

| Palette | Theme |
|---------|-------|
| multicolor-1 through multicolor-6 | Rainbow variations |
| sunset-warm-1 | Warm temperature: reds, oranges, yellows |
| ocean-cool-1 | Cool temperature: blues, teals, greens |
| primary-bold-1 | Classic LEGO: red, blue, yellow, green |
| pastel-party-1 | Light pastel tones |
| neon-punch-1 | Vivid saturated colors |

MONO_BLUE, MONO_RED etc. are defined as placeholders but not yet implemented.

### Usage

```bash
cd BrickitStudio/Pockets-coloring

# Colorize one pocket with one palette
python3 modifier_colorize.py ../Pockets-recipe-1/output/Pocket15.io --palette neon-punch-1 -o output/Pocket15_neon.io

# Batch colorize — apply all palettes to all pockets in a folder
python3 batch_colorize.py ../Pockets-recipe-1/output output/
```

---

## .io Packaging

### Required model.ldr header

```
0 {PocketName}
0 Name: {pocket_name}.ldr
0 Author: Brickit
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickControlPointUnitLength -1
0
```

**Important:** Line 2 must be `0 Name: {pocket_name}.ldr` (NOT `model.ldr`).
Stud.io uses this string as the model name shown in the tab title.

### .info file content

```json
{"version":"2.26.3_1","total_parts":91,"parts_db_version":215}
```

Update `total_parts` to match actual part count.

### Packaging script

```bash
# CRITICAL: always build ZIP in /tmp — workspace dirs can be EROFS for shell commands
mkdir -p /tmp/pocket_io
cp /tmp/model.ldr /tmp/pocket_io/model.ldr
echo '{"version":"2.26.3_1","total_parts":91,"parts_db_version":215}' > /tmp/pocket_io/.info
echo '[]' > /tmp/pocket_io/errorPartList.err
cd /tmp/pocket_io && zip -r /tmp/PocketN.io model.ldr .info errorPartList.err
cp /tmp/PocketN.io "/path/to/Pockets/Pocket N.io"
```

The `packager_io.sh` script (Recipe 1 pipeline) handles this automatically.

---

## Production Pipeline

### Recipe 1 full run (recommended)

```bash
cd BrickitStudio/Pockets-recipe-1

# Single pocket
python3 generator_pile.py --name "Pocket 20" --size medium --seeds 900 980 -o /tmp/p.ldr
python3 modifier_fill_gaps.py /tmp/p.ldr /tmp/pf.ldr --seed 42
python3 modifier_settle_y.py /tmp/pf.ldr /tmp/ps.ldr
bash packager_io.sh /tmp/ps.ldr "output/Pocket 20.io" 91

# Batch (multiple pockets)
./batch_generate.sh
```

### Recipe 2 full run

```bash
cd BrickitStudio/Pockets-recipe-2
python3 generator_toplayer_with_modifiers.py
# Produces 12-B, 12-C, 12-D variants
```

### Batch colorize

```bash
cd BrickitStudio/Pockets-coloring
python3 batch_colorize.py <input_folder> <output_folder>
# Applies all 11 palettes to every .io in input folder
```

### Preview generation (QA)

```bash
cd BrickitStudio
./model_preview.sh ./Pockets-recipe-1/output
# Opens each .io in Studio via AppleScript, captures 4-angle screenshots
# Writes {filename}_preview/ folder next to each .io file
```

Dependencies: macOS + BrickLink Studio + Accessibility permissions for terminal app.

---

## Render Settings (Top-Down for App)

| Setting | Value |
|---------|-------|
| Camera | Directly above (slight 10–20° angle for depth) |
| Resolution | 1200×1600 (portrait) |
| Background | Transparent or white |
| Lighting | HDR or three-point; intensity 0.7–0.8 |
| Stud logo | ON |
| FOV | 30–45° |

Reference renders in `BrickitStudio/Pockets/renders/`.

---

## macOS Studio File Association Patch

BrickLink Studio 2.0 does not register as a macOS file handler for `.io` files (Unity build omits
CFBundleDocumentTypes). Double-clicking `.io` files does not open Studio, and `open -a` fails.

**Fix:** Patch `Info.plist` inside Studio.app:
- Add `CFBundleDocumentTypes` for `.io` extension
- Add `UTImportedTypeDeclarations` declaring `com.bricklink.studio.io` UTI (conforms to `public.data + public.archive`)
- After patching: remove `_CodeSignature/` and run `lsregister -f` on the app

Patch script: `~/Dev/Studio 2.0/patch-studio-file-association.sh`

**Note:** Patch is reset on every Studio auto-update (Unity regenerates Info.plist).

**Workaround (no patch):** Always open files from within Studio via File → Open dialog, never by double-click.

---

## Alternative: Blender Physics Pipeline

For overlap-free flat piles (below the 6–8% practical floor for rejection sampling):

1. Studio → Export LDraw (.ldr)
2. Import in Blender via `ExportLDraw` or `ldr_tools_blender`
3. Assign Rigid Body (Active) to all parts; ground plane (Passive)
4. Run physics simulation → parts settle naturally
5. Render top-down with Cycles

See `MODELING_BESTPRACTICES.md` in BrickitStudio for Blender details.

---

## Scripts Reference

All production scripts are included in the skill at `projects/part-piles/scripts/`.

### Recipe 1 — `scripts/recipe-1/`

| Script | Purpose | CLI |
|--------|---------|-----|
| `generator_pile.py` | Generate base pile (rotation-aware AABB, multi-seed) | `python3 generator_pile.py --name "Pocket N" --size medium --seeds 400 460 -o /tmp/p.ldr` |
| `modifier_fill_gaps.py` | Fill top-down visual gaps with small parts | `python3 modifier_fill_gaps.py input.ldr output.ldr --seed 42` |
| `modifier_settle_y.py` | Compact pile vertically (gravity simulate) | `python3 modifier_settle_y.py input.ldr output.ldr` |
| `packager_io.sh` | Package .ldr as .io ZIP for Stud.io | `bash packager_io.sh input.ldr "output/Pocket N.io" 91` |
| `batch_generate.sh` | Full pipeline for multiple pockets | `./batch_generate.sh` |

**Full Recipe 1 pipeline:**
```bash
python3 generator_pile.py --name "Pocket 20" --size medium --seeds 900 980 -o /tmp/p.ldr
python3 modifier_fill_gaps.py /tmp/p.ldr /tmp/pf.ldr --seed 42
python3 modifier_settle_y.py /tmp/pf.ldr /tmp/ps.ldr
bash packager_io.sh /tmp/ps.ldr "Pocket 20.io" 91
```

### Recipe 2 — `scripts/recipe-2/`

| Script | Purpose | CLI |
|--------|---------|-----|
| `generator_toplayer_v4.py` | Sequential outward placement, best of 60 seeds | Used as module |
| `generator_toplayer_with_modifiers.py` | Driver: runs v4 + both modifiers, writes B/C/D variants | `python3 generator_toplayer_with_modifiers.py` |
| `modifier_rotation_shuffle.py` | Shuffle rotations (upright/leaning/on-side/upside-down) | Used as module |
| `modifier_fill_small_parts.py` | Monte Carlo gap fill with small parts | Used as module |
| `batch_generate.py` | Batch run Recipe 2 for multiple pockets | `python3 batch_generate.py` |

**Full Recipe 2 pipeline:**
```bash
cd scripts/recipe-2
python3 generator_toplayer_with_modifiers.py
# Produces /tmp/pocket12B.ldr (rotation shuffle)
#          /tmp/pocket12C.ldr (gap fill)
#          /tmp/pocket12D.ldr (both modifiers)
```

### Coloring — `scripts/coloring/`

| Script | Purpose | CLI |
|--------|---------|-----|
| `color_palettes.py` | Palette definitions (11 palettes) | Import only |
| `modifier_colorize.py` | Apply one palette to one .io file | `python3 modifier_colorize.py input.io --palette neon-punch-1 -o output.io` |
| `batch_colorize.py` | Apply all palettes to all .io files in folder | `python3 batch_colorize.py input_folder/ output_folder/` |

**End-to-end: generate + colorize:**
```bash
./batch_generate.sh                              # → output/*.io (base pockets)
python3 ../coloring/batch_colorize.py output/ colored/   # → colored/*.io (all 11 palettes)
```

### Preview — `scripts/preview/`

| Script | Purpose | CLI |
|--------|---------|-----|
| `model_preview.sh` | Batch 4-angle screenshot for all .io in a folder | `./model_preview.sh ./output` |

Requires macOS + BrickLink Studio + Accessibility permissions for terminal app.

### Archive — `scripts/archive/`

Historical per-pocket generator scripts showing the evolution of Recipe 1 (P6→P14) and
Recipe 2 (v1→v4). Not meant for direct use — reference only.
See `scripts/archive/README.md` for the full evolution timeline.

---

## Open Issues / Next Steps

- Recipe 2 has only top-layer pockets (P12 variants). Full pile with hero/accent lower layers not yet developed.
- Medium Size render settings not calibrated: existing camera position targets Small (17×13 studs); Medium (22×16) may need zoom-out.
- Fill palette expansion: currently 25 parts; pushing coverage from 88% to 95%+ requires ~35–40 parts.
- Uniform Y + settle_y: using uniform Y in generator and relying on settle for all compaction — might produce more natural layering than triangular + partial settle.
- Recipe 1 vs Recipe 2 visual comparison: not yet done side-by-side.
- MONO palettes in coloring system: defined as placeholders, not yet implemented.
