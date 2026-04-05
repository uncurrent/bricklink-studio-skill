---
project: part-piles
status: active
created: 2026-04-05
algorithm-version: v3 (Pocket 6)
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

| File | Type | Parts | Status |
|------|------|-------|--------|
| Pocket 1 | Manual (Stud.io) | 89 | Reference model |
| Pocket 2 | Manual (part-swap of P1) | 89 | Variant of P1 |
| Pocket 3 | Generated v0 | 26 | Technic, all white — too sparse |
| Pocket 4 | Generated v1 | 71 | Y-rotation only — looks fake |
| Pocket 5 | Generated v2 | 71 | Full 3D + ellipsoid — 25% overlap |
| Pocket 6 | Generated v3 | 66 | Rotation-aware AABB — **~8% overlap ✓** |

---

## Size Standards (Small Size)

Measured from Pocket 1 & 2 (hand-made reference):

| Parameter | Value |
|-----------|-------|
| Parts count | ~89 (generated pockets work well at 66–71) |
| Footprint X | ~354 LDU ≈ 17.7 studs |
| Footprint Z | ~264 LDU ≈ 13.2 studs |
| Pile height Y | ~208 LDU ≈ 26 plates |
| Pile center | X ≈ −100, Z ≈ −130 (LDU) |

---

## Part Composition Recipe (Small Size)

| Category | Share | Example parts |
|----------|-------|---------------|
| Base bricks | ~35% | 2×4 ×6, 2×2 ×5, 1×2 ×4, 1×4 ×3, 1×1 ×3 |
| Base plates | ~30% | 2×8 ×2, 2×6 ×2, 2×4 ×4, 2×3 ×2, 1×4 ×3, 2×2 ×3, 1×2 ×4 |
| Accent parts | ~35% | slopes, curved slopes, round tiles, tiles |
| Technic | accent only | max 2–3 pcs total |

**Must-haves:** 2×4 bricks ×5+, 2×2 bricks ×4+, 1×2 bricks ×4+, 2×4 plates ×3+, 2×8 plate ×2.

---

## Generation Pipeline (v3 — current best)

### 1. Define part half-dimensions

```python
PART_DIMS = {
    "3001.dat": (40,12,20),  # Brick 2×4
    "3003.dat": (20,12,20),  # Brick 2×2
    "3004.dat": (20,12,10),  # Brick 1×2
    "3010.dat": (40,12,10),  # Brick 1×4
    "3005.dat": (10,12,10),  # Brick 1×1
    "3023.dat": (20, 4,10),  # Plate 1×2
    "3022.dat": (20, 4,20),  # Plate 2×2
    "3020.dat": (40, 4,20),  # Plate 2×4
    "3710.dat": (40, 4,10),  # Plate 1×4
    "3034.dat": (80, 4,20),  # Plate 2×8
    "3795.dat": (60, 4,20),  # Plate 2×6
    "3021.dat": (30, 4,20),  # Plate 2×3
    "3039.dat": (20,14,20),  # Slope 45° 2×2
    "3040b.dat":(20,14,10),  # Slope 45° 2×1
    "3062b.dat":(10,12,10),  # Brick 1×1 Round
    "14769.dat":(20, 3,20),  # Tile 2×2 Round
    "4073.dat": (10, 3,10),  # Plate 1×1 Round
    "3069b.dat":(20, 3,10),  # Tile 1×2
    "3068b.dat":(20, 3,20),  # Tile 2×2
}
```

Units: LDU half-extents (a=X/2, b=Y/2, c=Z/2).

### 2. Generate rotation matrix

```python
import math, random

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
    def mm(A,B):
        return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)
```

**Tilt strength by category:**

| Category | tilt_strength |
|----------|---------------|
| Large plates (2×8, 2×6) | 0.18 |
| Base plates | 0.22–0.25 |
| Standard bricks | 0.35–0.50 |
| Slopes / accent | 0.50–0.65 |
| Technic / tiny (1×1) | 0.65–0.70 |

### 3. Rotation-aware AABB (key fix vs v2)

```python
def compute_half_extents(dims, R):
    a, b, c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ey = abs(R[1][0])*a + abs(R[1][1])*b + abs(R[1][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ey, ez
```

This correctly handles any orientation. A plate standing on edge → ey ≈ 40 LDU (not 5).

### 4. Collision check

```python
GAP = 4  # LDU minimum clearance between AABBs

def overlaps(p1, p2):
    x1,y1,z1,ex1,ey1,ez1 = p1
    x2,y2,z2,ex2,ey2,ez2 = p2
    return (abs(x1-x2) < ex1+ex2+GAP and
            abs(y1-y2) < ey1+ey2+GAP and
            abs(z1-z2) < ez1+ez2+GAP)
```

### 5. Placement parameters (Pocket 6 baseline)

| Parameter | Value | Notes |
|-----------|-------|-------|
| CX, CZ | -100, -130 | Pile center in LDU |
| SIGMA_X | 52 | Gaussian spread X |
| SIGMA_Z | 42 | Gaussian spread Z (tighten to ~36 to reduce footprint) |
| Y_MIN / Y_MAX | 0 / 240 | Vertical range |
| Y distribution | `triangular(Y_MIN, Y_MAX, Y_MIN+40)` | Biased toward bottom (gravity) |
| GAP | 4 LDU | Min clearance between AABBs |
| MAX_TRIES | 600 | Per-part placement attempts |
| Placement order | Largest footprint first | Big plates placed first → small fill gaps |

### 6. Multi-seed selection

```python
best_forced = float('inf')
for seed in range(42, 62):  # 20 seeds
    parts_out, n_clean, n_forced = generate(seed)
    if n_forced < best_forced:
        best_forced = n_forced
        best_result = (seed, parts_out, n_clean, n_forced)
```

**Typical best result:** ~8% forced (5/66 parts). Seed 43 was best for Pocket 6.

---

## .io Packaging

### Required model.ldr header

```
0 Model Name
0 Name: model.ldr
0 Author: Brickit
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickControlPointUnitLength -1
0
```

### .info file content

```json
{"version":"2.26.3_1","total_parts":66,"parts_db_version":215}
```

### Packaging script

```bash
# IMPORTANT: always build ZIP in /tmp — workspace dirs can be EROFS for shell commands
mkdir -p /tmp/pocket_io
cp /tmp/model.ldr /tmp/pocket_io/model.ldr
echo '{"version":"2.26.3_1","total_parts":66,"parts_db_version":215}' > /tmp/pocket_io/.info
echo '[]' > /tmp/pocket_io/errorPartList.err
cd /tmp/pocket_io && zip -r /tmp/PocketN.io model.ldr .info errorPartList.err
cp /tmp/PocketN.io "/path/to/Pockets/Pocket N.io"
```

---

## Render Settings (Top-Down for App)

| Setting | Value |
|---------|-------|
| Camera | Directly above (top-down, slight 10–20° angle for depth) |
| Resolution | 1200×1600 (portrait) |
| Background | Transparent or white |
| Lighting | HDR or three-point; intensity 0.7–0.8 |
| Stud logo | ON |
| FOV | 30–45° |

Reference renders in `BrickitStudio/Pockets/renders/` — filenames encode settings used
(e.g. `Pocket1_hdr-1200x1600_intens-0-7.png`).

---

## Alternative: Blender Physics Pipeline (higher quality)

1. Studio → Export LDraw (.ldr)
2. Import in Blender via `ExportLDraw` or `ldr_tools_blender` add-on
3. Assign Rigid Body (Active) to all parts; add ground plane (Passive)
4. Run physics simulation → parts settle naturally under gravity
5. Render top-down with Cycles
6. Result: physically correct pile, zero overlaps

See `MODELING_BESTPRACTICES.md` in BrickitStudio for Blender-specific details.

---

## Open Issues / Next Improvements

- Z footprint (16.9 studs) wider than reference (13.2) — reduce SIGMA_Z to ~36
- 5 forced parts still semi-transparent in Stud.io — target <5%
- Layered Y placement by part size would be more realistic than Gaussian
- Poisson disk sampling would give more even distribution than Gaussian XZ
- Blender physics simulation eliminates overlaps entirely
