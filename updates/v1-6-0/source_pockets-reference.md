# Brickit Pockets — Master Reference

## What This Is

Models for the **Brickit Pockets** feature in the Brickit app. Users store LEGO parts in zip-lock bags; the model is a visual representation — a top-down render that looks like a real handful of parts in a transparent bag.

All `.io` files are opened with **Stud.io** (by BrickLink).

---

## File Structure

```
Pockets/
  POCKETS.md                 ← this file — master reference
  MODELING_BESTPRACTICES.md  ← Stud.io & Blender techniques
  SESSION_NOTES.md           ← .io format, LDraw syntax, Studio UI tips
  SESSION_LOG.md             ← full history of Pockets 3–6 development
  Pocket 1.io / Pocket 2.io / ...   ← model files (open in Stud.io)
  Pocket N/
    NOTES.md                 ← per-pocket notes, composition, generation info
    gen_pocketN.py           ← generation script (for generated pockets)
  renders/                   ← top-down renders for app use
```

---

## Size Standards

### Small Size (reference: Pocket 1 & 2, hand-made in Stud.io)

| Parameter | Value |
|-----------|-------|
| Parts count | ~89 (generated pockets work well at 66–71) |
| Footprint X | ~354 LDU ≈ 17.7 studs |
| Footprint Z | ~264 LDU ≈ 13.2 studs |
| Pile height Y | ~208 LDU ≈ 26 plates |
| Pile center | X ≈ −100, Z ≈ −130 (LDU) |

### Medium Size (reference: Pocket 14)

| Parameter | Value |
|-----------|-------|
| Parts count | ~66 |
| Footprint X | ~440 LDU ≈ 22 studs |
| Footprint Z | ~326 LDU ≈ 16.3 studs |
| Pile height Y | ~315 LDU ≈ 39 plates |
| Pile center | X ≈ −100, Z ≈ −130 (LDU) |
| SIGMA_X / SIGMA_Z | 58 / 46 |
| GAP | 4 LDU |
| Y_MAX | 340 |

---

## Part Composition Recipe (Small Size)

| Category | Share | Parts |
|----------|-------|-------|
| Base bricks | ~35% | 2×4 ×6, 2×2 ×5, 1×2 ×4, 1×4 ×3, 1×1 ×3 |
| Base plates | ~30% | 2×8 ×2, 2×6 ×2, 2×4 ×4, 2×3 ×2, 1×4 ×3, 2×2 ×3, 1×2 ×4 |
| Accent parts | ~35% | slopes, curved slopes, round tiles, tiles |
| Technic | accent only | max 2–3 pcs total |

Must-haves: 2×4 bricks ×5+, 2×2 bricks ×4+, 1×2 bricks ×4+, 2×4 plates ×3+, 2×8 plate ×2.

---

## Generation Algorithm (v3 — Pocket 6+)

### Core idea

Python script generates LDraw `.ldr`, packaged as `.io` (ZIP). Stud.io renders `model.ldr`.

### Part half-dimensions (LDU)

```python
PART_DIMS = {
    "3001.dat": (40,12,20),  "3003.dat": (20,12,20),  "3004.dat": (20,12,10),
    "3010.dat": (40,12,10),  "3005.dat": (10,12,10),
    "3023.dat": (20, 4,10),  "3022.dat": (20, 4,20),  "3020.dat": (40, 4,20),
    "3710.dat": (40, 4,10),  "3034.dat": (80, 4,20),  "3795.dat": (60, 4,20),
    "3021.dat": (30, 4,20),
    "3039.dat": (20,14,20),  "3040b.dat":(20,14,10),  "3062b.dat":(10,12,10),
    "14769.dat":(20, 3,20),  "4073.dat": (10, 3,10),
    "3069b.dat":(20, 3,10),  "3068b.dat":(20, 3,20),
}
```

### Rotation-aware AABB (key fix vs v2)

Fixed bounding radii are wrong for tilted parts — a plate standing on its edge is tall, not flat. The AABB formula accounts for any orientation:

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
    if r < 0.55:
        s = 10 + 35 * tilt_strength
        rx = math.radians(rng.gauss(0, s))
        rz = math.radians(rng.gauss(0, s))
    elif r < 0.80:
        lim = 35 + 70 * tilt_strength
        rx = math.radians(rng.uniform(-lim, lim))
        rz = math.radians(rng.uniform(-lim, lim))
    else:
        rx = math.radians(rng.uniform(-180, 180))
        rz = math.radians(rng.uniform(-180, 180))
    cy,sy = math.cos(ry),math.sin(ry); cx,sx = math.cos(rx),math.sin(rx); cz,sz = math.cos(rz),math.sin(rz)
    def mm(A,B): return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(mm([[cy,0,sy],[0,1,0],[-sy,0,cy]], [[1,0,0],[0,cx,-sx],[0,sx,cx]]), [[cz,-sz,0],[sz,cz,0],[0,0,1]])
```

Tilt strength by category: large plates `0.18`, base plates `0.22–0.25`, bricks `0.35–0.50`, slopes/accent `0.50–0.65`, Technic/tiny `0.65–0.70`.

### Placement parameters (Pocket 6 baseline)

| Parameter | Value |
|-----------|-------|
| `CX, CZ` | `-100, -130` |
| `SIGMA_X` | `52` |
| `SIGMA_Z` | `42` |
| `Y_MIN / Y_MAX` | `0 / 240` |
| `GAP` | `4 LDU` (minimum clearance between AABBs) |
| `MAX_TRIES` | `600` per part |
| Y distribution | `triangular(Y_MIN, Y_MAX, Y_MIN+40)` — biased toward bottom |
| Placement order | Largest footprint first |
| Seeds tried | 20 (pick best = fewest forced placements) |

### Collision check

```python
GAP = 4
def overlaps(p1, p2):
    x1,y1,z1,ex1,ey1,ez1 = p1
    x2,y2,z2,ex2,ey2,ez2 = p2
    return (abs(x1-x2) < ex1+ex2+GAP and abs(y1-y2) < ey1+ey2+GAP and abs(z1-z2) < ez1+ez2+GAP)
```

### Multi-seed selection

```python
for seed in range(42, 62):
    parts_out, n_clean, n_forced = generate(seed)
    if n_forced < best_forced:
        best_result = (seed, parts_out, n_clean, n_forced)
```

Typical best result: **~8% forced** (5/66 parts).

---

## .io Packaging

```bash
mkdir /tmp/pocket_io
cp /tmp/model.ldr /tmp/pocket_io/model.ldr
echo '{"version":"2.26.3_1","total_parts":66,"parts_db_version":215}' > /tmp/pocket_io/.info
echo '[]' > /tmp/pocket_io/errorPartList.err
cd /tmp/pocket_io && zip -r /tmp/PocketN.io model.ldr .info errorPartList.err
cp /tmp/PocketN.io "Pockets/Pocket N.io"
# Note: create zip in /tmp first — mounted workspace dirs may be read-only for zip
```

Required `model.ldr` header:
```
0 <Model Name>
0 Name: model.ldr
0 Author: <author>
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickLockedControlPoint
0
```

---

## LDraw Quick Reference

| Concept | Value |
|---------|-------|
| 1 stud | 20 LDU |
| 1 plate height | 8 LDU |
| 1 brick height | 24 LDU |
| Y axis direction | downward (negative Y = up) |
| White color | 15 |

Part line: `1 <color> <x> <y> <z> <R00..R22> <part.dat>`

---

## Pockets Overview

| File | Type | Parts | Notes |
|------|------|-------|-------|
| `Pocket 1.io` | Manual | 89 | Reference model, hand-made in Stud.io |
| `Pocket 2.io` | Manual | 89 | Part-swapped variant of Pocket 1 |
| `Pocket 3.io` | Generated | 26 | Technic-heavy, all white, spread layout |
| `Pocket 4.io` | Generated | 71 | First colorful pile, Y-rotation only |
| `Pocket 5.io` | Generated | 71 | Full 3D rotations, ellipsoid BV (~25% overlap) |
| `Pocket 6.io` | Generated | 66 | Rotation-aware AABB, ~8% forced overlap ✓ |
| `Pocket 13.io` | Generated | 66 | Small, v3+P7 params, 2% forced |
| `Pocket 14.io` | Generated | 66 | **Medium** (first), v3 algorithm, 0% forced ✓ |
