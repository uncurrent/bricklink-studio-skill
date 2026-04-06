# Pocket Notes — Collected from Pockets/ folder

---

# Pocket 1 — Notes

**Type:** Hand-made in Stud.io
**Parts:** 89
**Status:** Reference model for Small Size standard

## Part Composition

| Count | Part | ID |
|-------|------|----|
| 7× | Plate 2×2 | 3022.dat |
| 6× | Tile 2×2 | 3068b.dat |
| 5× | Plate 1×2 | 3023a.dat |
| 3× | Brick 1×1 | 3005.dat |
| 3× | Brick 2×4 | 3001.dat |
| 3× | Plate 2×4 | 3020.dat |
| + | Decorative accents | wheel, ice cream cone, Technic brick, etc. |

## Notes

- This model is the primary reference for Small Size dimensions (354×264 LDU footprint)
- Was partially modified via Stud.io UI (auto-save). If original is needed: `git show HEAD:"Pockets/Pocket 1.io" > /tmp/pocket1_original.io`
- Positions and rotations were later reused as the base for Pocket 2

---

# Pocket 2 — Notes

**Type:** Programmatic (Python part-swap of Pocket 1)
**Parts:** 89
**Status:** Done

## Method

Pocket 1's `model.ldr` was read in Python; part IDs were replaced line-by-line. Positions and rotations were kept identical — only part names changed.

## Part Replacement Mapping

| Old (Pocket 1) | → | New (Pocket 2) |
|----------------|---|----------------|
| 3022.dat — Plate 2×2 | | 3003.dat — Brick 2×2 |
| 3068b.dat — Tile 2×2 | | 3010.dat — Brick 1×4 |
| 3023a.dat — Plate 1×2 | | 3040b.dat — Slope 45° 2×1 |
| 3005.dat — Brick 1×1 | | 3062b.dat — Brick 1×1 Round |
| 3001.dat — Brick 2×4 | | 3002.dat — Brick 2×3 |
| 3020.dat — Plate 2×4 | | 3795.dat — Plate 2×6 |
| 3710.dat — Plate 1×4 | | 3009.dat — Brick 1×6 |
| 3460.dat — Plate 1×8 | | 3008.dat — Brick 1×8 |

## Notes

- Because positions are copied from Pocket 1, the top-down silhouette looks very similar
- Future pockets should use independent position generation to look distinct

---

# Pocket 3 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 26
**Status:** Done — experimental, not a production pocket

## Purpose

Experiment: maximum variety from Pockets 1/2, Technic-heavy composition, all white.

## Composition

All parts recolored to LDraw color 15 (white). Technic-heavy:
- Liftarms (1×3, 1×5, 1×7, 1×9, 1×11)
- Technic bricks (1×2, 1×4, 1×6, 1×8)
- Axle connectors, pins, axle pins
- A few regular bricks and plates

## Algorithm (v0 — no collision detection)

- Gaussian XZ placement (σ≈55, 44), center (-100, -130)
- Y-axis-only rotation — all parts face upward
- No collision detection → parts can overlap freely
- Spread layout (σ large) → parts well separated, not a heap

## Lessons Learned

- Without X/Z tilt, parts look like they're floating face-up in empty space
- Need full 3D rotation to look like a realistic pile → fixed in Pocket 5
- Technic parts look interesting but wrong as a "common parts" pocket

---

# Pocket 4 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 71
**Status:** Superseded by Pocket 6 (overlaps unresolved)

## Purpose

First "proper" colorful pile. Established the Small Size composition recipe: common bricks + plates as base, Technic as accent only.

## Composition

- Base bricks: 2×4 ×6, 2×2 ×5, 1×2 ×4, 1×4 ×3, 1×1 ×3
- Base plates: 2×8 ×2, 2×6 ×2, 2×4 ×4, 2×3 ×2, 1×4 ×3, 2×2 ×3, 1×2 ×4
- Accent: slopes, round bricks, tiles, curved slopes
- Technic: max 3 pcs (liftarm, axle pin, pin)
- Colors: random from palette [red, blue, yellow, green, orange, dark pink, light grey, tan, dark purple, medium grey]

## Algorithm (v1 — Y-rotation only)

- Gaussian XZ (σ≈55, 44), center (-100, -130), Y uniform [0–200]
- **Y-axis rotation only** (no X/Z tilt) → all parts face upward, looks fake
- **No collision detection** → ~25% parts semi-transparent (overlapping) in Stud.io

## Lessons Learned

- Part composition recipe works well — this is now the standard recipe
- Y-only rotation is insufficient: need full 3D Rx/Rz tilt for realistic pile look
- Collision detection is essential: ~25% overlap makes model look broken in Stud.io

---

# Pocket 5 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 71
**Status:** Superseded by Pocket 6 (overlap issue partially fixed but root cause remained)

## Algorithm (v2 — full 3D rotation + ellipsoid collision)

Two improvements over Pocket 4:

### 1. Full 3D rotation matrix

R = Ry × Rx × Rz, with per-part `tilt_strength` controlling how much X/Z tilt a part gets:
- Large plates: `tilt_strength=0.18` (mostly flat)
- Bricks: `tilt_strength=0.35–0.50`
- Accent parts: `tilt_strength=0.55–0.70` (can be sideways or upside-down)

Three rotation modes sampled randomly:
- Gaussian tilt (55% chance) — natural slight wobble
- Uniform moderate tilt (25%) — more pronounced angle
- Fully random orientation (20%) — upside-down, on edge, etc.

### 2. Ellipsoid bounding volume collision

Each part assigned fixed `(r_horizontal, r_vertical)` radii. Rejection sampling: try 400 random positions, fallback to fewest-overlap position.

## Result

71 parts, footprint 23.4 × 13.8 studs. Tilts looked much more realistic. But still ~25% forced placements.

## Root Cause of Remaining Overlaps

The bounding radii were **fixed** regardless of rotation. A flat plate (`r_v = 5 LDU`) standing on its edge actually needs `ey ≈ 40 LDU` — but the collision check still used `r_v = 5`. The axis-aligned extent of a rotated object must account for the rotation matrix. → Fixed in Pocket 6 with rotation-aware AABB.

---

# Pocket 6 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 66
**Status:** Current best — ~8% forced overlap (5/66 parts)
**Best seed:** 43 (from multi-seed search over seeds 42–61)

## Result Stats

| Metric | Value | Reference |
|--------|-------|-----------|
| Parts | 66 | ~89 |
| Forced placements | 5 (8%) | target: <10% |
| Footprint X | 18.2 studs | 17.7 studs |
| Footprint Z | 16.9 studs | 13.2 studs |
| Y range | 4–232 LDU | 0–208 |

## Algorithm (v3 — rotation-aware AABB)

See full description in `POCKETS.md`. Key fix over v2: bounding box half-extents are computed from the rotation matrix rather than using fixed radii:

```
ex = |R[0][0]|·a + |R[0][1]|·b + |R[0][2]|·c
```

This correctly handles tilted plates (standing on edge → ey ≈ 40, not 5).

Additional changes vs v2:
- GAP = 4 LDU minimum clearance
- Triangular Y distribution (biased toward bottom)
- Placement order: largest footprint first
- Multi-seed selection (20 seeds, pick best)

## Generation Script

See `gen_pocket6.py` in this folder.

## Known Issues

- Z footprint (16.9 studs) is wider than reference (13.2 studs) — SIGMA_Z could be reduced slightly
- 5 parts are still forced (semi-transparent in Stud.io) — acceptable for now
- To improve further: tighten SIGMA_Z to ~36, or implement layered Y placement by part size

---

# Pocket 7 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 65
**Status:** Done ✓ — first pocket with 0% forced overlap

## Result Stats

| Metric | Value | Reference |
|--------|-------|-----------|
| Parts | 65 | ~89 |
| Forced placements | **0 (0%)** | target <10% |
| Footprint X | 15.8 studs | 17.7 studs |
| Footprint Z | 11.8 studs | 13.2 studs |
| Y range | 2–293 LDU | ~208 |
| Best seed | 63 | — |

## Algorithm Parameters (vs Pocket 6)

| Parameter | Pocket 6 | Pocket 7 |
|-----------|----------|----------|
| SIGMA_X | 52 | 44 |
| SIGMA_Z | 42 | 32 |
| GAP | 4 LDU | 2 LDU |
| Y_MAX | 240 | 300 |
| Y bias peak | Y_MIN+40 | Y_MIN+50 |
| MAX_TRIES | 600 | 1200 |
| Seeds searched | 20 | 60 |
| Forced | 5/66 (8%) | **0/65 (0%)** |

## Key Insight

Increasing Y_MAX (allowing parts to stack taller) compensates for tighter XZ sigma —
instead of being forced to the sides, parts can go up. This is how density without overlap
is achieved via pure Gaussian sampling.

GAP=2 (vs 4) allows parts to sit closer together without actually overlapping AABBs.

## Visual Impression

Дenser and taller than Pocket 6. Footprint slightly smaller than reference.
Pile has a peaked mound shape (high Y_MAX with triangular distribution).

## Generation Script

See `gen_pocket7.py` in this folder (copy of gen_pocket6.py with updated parameters).

## Next (Pocket 8)

User feedback: footprint slightly too narrow, pile too tall.
Goal: slightly wider XZ + half the height → flat dense heap matching Pocket 1 reference.

---

# Pocket 8 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 65
**Status:** Done ✓ — flat dense heap, ~6% forced overlap
**Superseded by:** Pocket 9 (better oval footprint, two-layer floor coverage)

## Result Stats

| Metric | Value | Reference |
|--------|-------|-----------|
| Parts | 65 | ~89 |
| Forced placements | 4 (6%) | target <10% |
| Footprint X | 16.3 studs | 17.7 studs |
| Footprint Z | 14.7 studs | 13.2 studs |
| Y range | 5–158 LDU | ~208 (P7 was 2–293) |
| Best seed | 112 | — |

## Goal

User request: slightly wider footprint than P7, even denser packing, half the height.
Reference: Pocket 1 (hand-made) — flat, spread-out heap.

## Algorithm Parameters (vs Pocket 7)

| Parameter | Pocket 7 | Pocket 8 |
|-----------|----------|----------|
| SIGMA_X | 44 | 48 |
| SIGMA_Z | 32 | 36 |
| GAP | 2 LDU | **1 LDU** (почти впритык) |
| Y_MAX | 300 | **160** (вдвое ниже) |
| Y bias peak | Y_MIN+50 | **Y_MIN+15** (сильно к дну) |
| tilt_strength | full | **×0.55 среднее** (части лежат, не торчат) |
| MAX_TRIES | 1200 | 1500 |
| Seeds searched | 60 | 100 |
| Forced | 0/65 (0%) | 4/65 (6%) |

## Key Insight: tilt_strength для плоской кучки

Центральный вывод этой итерации: при маленьком Y_MAX нельзя использовать высокий tilt_strength.
Если деталь стоит вертикально (rx≈90°), её `ey` может достигать 40 LDU для плейта.
При Y_MAX=160 таких деталей может быть только 2 в одной точке — остальные вынуждены.

Решение: снизить tilt_strength примерно вдвое по всем категориям. Детали лежат,
их `ey` остаётся малым → они помещаются в плоский диапазон Y без конфликтов.

| Категория | P7 tilt | P8 tilt |
|-----------|---------|---------|
| Крупные плейты | 0.18 | 0.10 |
| Базовые плейты | 0.22–0.25 | 0.12–0.15 |
| Кирпичи 2×4/2×2 | 0.35 | 0.20 |
| Кирпичи 1×2/1×4 | 0.40 | 0.25 |
| Slopes/accents | 0.50–0.55 | 0.30–0.35 |
| Техник | 0.60–0.70 | 0.40–0.50 |

## Attempt History

- **First attempt** (SIGMA 38/28, GAP=0, Y_MAX=140, original tilt): 22% forced.
  Root cause: sigma too tight for large parts; Y_MAX too small for tilted parts.
- **Second attempt** (SIGMA 44/32, GAP=2, Y_MAX=300, original tilt): 0% forced = Pocket 7.
  But pile was too tall (Y up to 293).
- **Third attempt** (SIGMA 48/36, GAP=0, Y_MAX=140, original tilt): 17% forced.
  Root cause: Y_MAX too tight with high tilt.
- **Fourth attempt = final** (SIGMA 48/36, GAP=1, Y_MAX=160, reduced tilt): **6% forced** ✓

## Visual Impression

Flat, spread heap. Parts predominantly lying flat with moderate tilt.
Dense feeling — parts close to each other. Much less "tall pile", more "spread handful".

---

# Pocket 9 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 65
**Status:** Done ✓ — two-layer system, oval footprint matches reference exactly

## Result Stats

| Metric | Value | Reference |
|--------|-------|-----------|
| Parts | 65 | ~89 |
| Forced placements | 6 (9%) | target <10% |
| Footprint X | 18.4 studs | 17.7 studs |
| Footprint Z | **13.2 studs** | 13.2 studs ← exact match |
| Y range | 2–153 LDU | ~208 |
| Best seed | 109 | — |

## Key Architecture Change: Two-Layer System

User feedback on Pocket 8: overlapping parts, no clear oval shape, visible gaps in floor from top-down view.

### Floor layer (19 plates, placed first)
- Distribution: **uniform-in-ellipse** (not Gaussian)
  ```python
  def sample_floor(rng):
      while True:
          rx = rng.uniform(-1, 1)
          rz = rng.uniform(-1, 1)
          if rx*rx + rz*rz <= 1.0:
              return CX + rx*OVAL_A, CZ + rz*OVAL_B
  # OVAL_A=180, OVAL_B=135 → diameter ~18×13.5 studs
  ```
- Y: `triangular(0, 60, 8)` — strongly biased to bottom
- tilt_strength: 0.08–0.12 (near-flat, covers gaps from top view)
- Parts: 3034×1, 3795×2, 3020×4, 3710×3, 3021×2, 3022×3, 3023×4

### Pile layer (46 parts, placed second)
- Distribution: Gaussian (SIGMA_X=46, SIGMA_Z=33)
- Y: `triangular(0, 155, 18)` — flat heap profile
- tilt_strength: 0.22–0.52 (moderate, natural pile look)
- Parts: bricks, slopes, round bricks, tiles, Technic

### Why uniform-in-ellipse for floor plates

With Gaussian, large plates cluster in the center — the perimeter of the pile has visible empty baseplate. With uniform-in-ellipse, plates spread across the entire footprint including the edges, covering gaps when viewed from above.

## Algorithm Parameters

| Parameter | Value |
|-----------|-------|
| CX, CZ | -100, -130 |
| OVAL_A / OVAL_B (floor) | 180 / 135 LDU |
| SIGMA_X / SIGMA_Z (pile) | 46 / 33 |
| GAP | 1 LDU |
| Y floor | triangular(0, 60, 8) |
| Y pile | triangular(0, 155, 18) |
| MAX_TRIES | 1800 |
| Seeds searched | 100 |

## Known Issue

9% forced (6 parts semi-transparent) — all from floor layer. With 19 plates covering ~65% of ellipse area, floor-floor collisions are unavoidable with current placement strategy.

Possible fix: Poisson disk sampling for floor layer (guarantees minimum distance between plate centers).

## Generation Script

See `gen_pocket9.py` in this folder.

---

# Pocket 10 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 65
**Status:** Done ✓ — P8 approach refined, Z footprint corrected to near-reference

## Result Stats

| Metric | Value | Reference |
|--------|-------|-----------|
| Parts | 65 | ~89 |
| Forced placements | 5 (8%) | target <10% |
| Footprint X | 18.9 studs | 17.7 studs |
| Footprint Z | **12.3 studs** | 13.2 studs |
| Y range | 2–155 LDU | ~208 |
| Best seed | 107 | — |
| Seeds searched | 200 | — |

## Goal

User feedback on Pocket 9: still overlaps, visible gaps from top view.
Return to P8 approach (Gaussian for all parts, reduced tilt) — proven best for flat piles —
but reduce SIGMA_Z from P8's 36 to 33 to bring Z footprint down toward reference (13.2 studs).

## Algorithm Parameters

| Parameter | P8 | P9 | P10 |
|-----------|----|----|-----|
| Strategy | Gaussian | Two-layer | Gaussian |
| SIGMA_X | 48 | 46 (pile) | 48 |
| SIGMA_Z | 36 | 33 (pile) | **33** |
| GAP | 1 LDU | 1 LDU | 1 LDU |
| Y_MAX | 160 | 155 | 162 |
| Y bias peak | Y_MIN+15 | Y_MIN+18 | Y_MIN+15 |
| Seeds searched | 100 | 100 | **200** |
| Forced | 4/65 (6%) | 6/65 (9%) | 5/65 (8%) |

## Attempt History

1. **80 parts, two-layer with GAP_FF=6 floor-floor**: 27–48% forced.
   Root cause: 80 parts in 18×13×7 stud volume is physically impossible with rejection sampling.

2. **10 Poisson disk floor + 55 Gaussian pile**: 15–27% forced (best 15%).
   Root cause: Poisson disk guarantees XZ separation but NOT 3D AABB separation.
   Two plates at similar XZ but different Y still conflict. Approach was abandoned.

3. **P8-style Gaussian, SIGMA_Z=33, 200 seeds**: **8% forced** ✓
   Returned to proven P8 approach; reduced SIGMA_Z; doubled seed search.

## Why Two-Layer Failed vs Gaussian

The intuition was correct (floor plates cover gaps visible from above), but in practice:
- Floor plates placed with uniform-in-ellipse created their own collision clusters
- When pile parts (Gaussian) came after, they competed for Y space with floor plates
- P8's single Gaussian with reduced tilt lets everything find Y positions more freely
- Result: P8 (6% forced) is better than P9 (9% forced) despite the two-layer logic

## Why Poisson Disk Didn't Help

Poisson disk sampling for floor plates ensures no two plates are closer than `min_dist`
in the XZ plane. But collision detection is 3D:
- Two plates at (x,z) and (x+30, z) can both have y≈0 → fine
- Two plates at (x,z) and (x+15, z) with y=0 and y=10 → 3D AABB collision despite XZ gap
The only reliable fix is reducing the number of floor plates or using Blender physics.

## Fundamental Limit (Documented)

For flat piles (Y_MAX ≈ 150–160 LDU) with 65 parts using rejection sampling:
- **Best achievable: ~6–8% forced** (P8 holds the record at 6%)
- Truly dense flat pile with 0% overlap requires **Blender rigid body physics**
- Blender physics pipeline is documented in `MODELING_BESTPRACTICES.md`

## Key Tilt Strength Parameters (Flat Pile)

Same as P8 — reduced ~0.55× vs original P6 values:

| Category | P6 tilt | P10 tilt |
|----------|---------|----------|
| Large plates (2×8, 2×6) | 0.18 | 0.10 |
| Base plates | 0.22–0.25 | 0.12–0.15 |
| Bricks 2×4/2×2 | 0.35 | 0.20 |
| Bricks 1×2/1×4 | 0.40 | 0.25 |
| Slopes/accents | 0.50–0.55 | 0.30–0.35 |
| Technic | 0.60–0.70 | 0.40–0.50 |

## Generation Script

See `gen_pocket10.py` in this folder.

---

# Pocket 11 — Notes

**Type:** Generated — 4-layer coverage system (new algorithm)
**Parts:** 61
**Status:** Done ✓ — first test of layer-based approach

## Result Stats

| Metric | Value | Reference |
|--------|-------|-----------|
| Parts | 61 | ~89 |
| Forced placements | **2 (3.3%)** | target <10% |
| Footprint X | **18.4 studs** | 17.7 studs |
| Footprint Z | **13.6 studs** | 13.2 studs |
| Height | ~30 plates | ~26 plates |
| Best seed | 78 | — |
| Seeds searched | 80 | — |

## Algorithm — 4-Layer Coverage System

### Layer 1+2: Heroes + Accents
Placed with Gaussian XZ distribution, Y=[0,175], moderate tilt (ts=0.40–0.55).
Sorted largest-footprint-first. 45 parts total.

| Category | Count | tilt_strength |
|----------|-------|---------------|
| Brick 2×4 | 8 | 0.40 |
| Brick 2×3 | 3 | 0.40 |
| Brick 2×2 | 6 | 0.40 |
| Brick 1×4 | 3 | 0.40 |
| Brick 1×2 | 5 | 0.40 |
| Brick 1×1 | 3 | 0.55 |
| Slope 45° 2×2 | 4 | 0.50 |
| Slope 45° 2×1 | 5 | 0.50 |
| Round brick 1×1 | 3 | 0.55 |
| Round tile 2×2 | 2 | 0.45 |
| Tile 1×2 | 3 | 0.45 |

### Layer 3: Gap-fill plates (coverage-based)
After layers 1+2, build XZ coverage grid (GRID_RES=12 LDU, 0.65× visual correction).
Find uncovered cells within FILL_OVAL (162×125 LDU).
Sort gaps by distance from center (fill center first).
For each gap cell: try 2×8→2×6→2×4→2×3→2×2→1×4→1×2, at 8 rotations.
Placed at Y=[182,210], near-flat (tiny tilt ≈3°).
Overflow check: skip if plate AABB exceeds FILL_OVAL × 1.12.

### Layer 4: Tiny fill
1×1 plates, 1×1 round plates for remaining gaps. Max 12 parts.

## Key Parameters

```
CX, CZ      = -100, -130
OVAL_A      = 190, OVAL_B = 140   # Hero placement oval
FILL_OVAL_A = 162, FILL_OVAL_B = 125   # Coverage/gap-fill oval
SIGMA_X     = 48, SIGMA_Z = 33
Y_HERO_MAX  = 175
Y_FILL_MIN  = 182, Y_FILL_MAX = 210
GAP         = 2 LDU
MAX_FILL    = 22, MAX_TINY = 12
```

## Why This Is Better Than Previous Approach

| | P8/P10 (Gaussian-only) | P11 (4-layer) |
|--|--|--|
| Hero tilt | Reduced 0.55× (flat) | Moderate (natural) |
| Gap coverage | 6–8% forced | 3.3% forced (2/61) |
| Visual coverage | 92–94% | 100% |
| Visual volume | Low (too flat) | Higher (heroes at ts=0.40) |
| Fill plates | N/A | Dedicated layer at floor Y |

## Key Insights

**Separation by Y level is the breakthrough**: heroes at Y=[0,175], fill plates at Y=[182,210].
Because the Y ranges don't overlap, the 3D AABB collision check naturally passes for fill plates vs heroes. Fill plates can be placed purely based on XZ coverage without fighting for Y space.

**FILL_OVAL vs OVAL separation**: Hero placement uses wide OVAL_A=190 (natural Gaussian scatter),
but gap-fill coverage uses tighter FILL_OVAL_A=162. This prevents fill plates from extending
outside the visual pile boundary.

**0.65× visual coverage correction**: tilted parts cover less visual area than their AABB.
Using 0.65×(rotation-aware AABB) as the "visual footprint" for coverage detection produces
more realistic gap estimates. Without this correction, 0% gaps are reported even when visual
holes exist (was seen in P9 attempts).

## Open Questions (for P12)

- Are the 2 forced placements visible? If so, which parts?
- Does the gap-fill layer look natural or mechanical?
- Does the oval look clean from top-down?
- Is 61 parts enough density or do we need more heroes?

---

# Pocket 13 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 66
**Status:** Done ✓ — v3 algorithm (P6 base) with P7-tuned parameters
**Best seed:** 209 (from multi-seed search over seeds 200–259)

## Result Stats

| Metric | Value | Reference |
|--------|-------|-----------|
| Parts | 66 | ~89 |
| Forced placements | **1 (2%)** | target <10% |
| Footprint X | 17.4 studs | 17.7 studs |
| Footprint Z | 10.9 studs | 13.2 studs |
| Y range | 7–289 LDU (35 plates) | ~208 |
| Best seed | 209 | — |
| Seeds searched | 60 | — |

## Algorithm

v3 rotation-aware AABB rejection sampling (same as P6/P7).
No multi-layer or coverage-based gap-fill — pure Gaussian placement.

## Parameters (P7-tuned)

| Parameter | P6 | P7 | P13 |
|-----------|----|----|-----|
| SIGMA_X | 52 | 44 | 44 |
| SIGMA_Z | 42 | 32 | 32 |
| GAP | 4 LDU | 2 LDU | 2 LDU |
| Y_MAX | 240 | 300 | 300 |
| Y bias peak | Y_MIN+40 | Y_MIN+50 | Y_MIN+50 |
| MAX_TRIES | 600 | 1200 | 1200 |
| Seeds searched | 20 | 60 | 60 |
| Seed range | 42–61 | 42–101 | 200–259 |
| Forced | 5/66 (8%) | 0/65 (0%) | **1/66 (2%)** |

## Observations

- Z footprint (10.9 studs) slightly narrower than reference (13.2) — consistent with P7 behavior
- Pile height (35 plates) taller than reference (26) — tradeoff for near-zero forced placements
- 17.4 stud X footprint very close to reference (17.7)

## Generation Script

See `gen_pocket13.py` in this folder.

---

# Pocket 14 — Notes

**Type:** Generated (Python → LDraw → .io)
**Parts:** 66
**Size:** Medium (first pocket of this size class)
**Status:** Done ✓ — 0% forced overlap
**Best seed:** 300 (from multi-seed search over seeds 300–379)

## Result Stats

| Metric | Value | Small ref | Delta |
|--------|-------|-----------|-------|
| Parts | 66 | ~66–89 | same |
| Forced placements | **0 (0%)** | 0–8% | ✓ |
| Footprint X | **22.0 studs** | 17.7 studs | +24% |
| Footprint Z | **16.3 studs** | 13.2 studs | +23% |
| Y range | 6–321 LDU (39 plates) | ~26 plates | taller |
| Best seed | 300 | — | — |
| Seeds searched | 80 | 20–60 | — |

## Algorithm

v3 rotation-aware AABB rejection sampling (same as P6/P7).
No multi-layer or coverage-based gap-fill — pure Gaussian placement.

## Medium vs Small Parameters

| Parameter | Small (P7) | Medium (P14) |
|-----------|-----------|-------------|
| SIGMA_X | 44 | **58** |
| SIGMA_Z | 32 | **46** |
| GAP | 2 LDU | **4 LDU** |
| Y_MAX | 300 | **340** |
| Y bias peak | Y_MIN+50 | Y_MIN+50 |
| MAX_TRIES | 1200 | **1500** |
| Seeds searched | 60 | **80** |

## Why Medium

User feedback on P13 (Small, P7 params): visible overlapping parts when viewed top-down.
Root cause: Small footprint (~17×13 studs) forces 66 parts into tight space.
Medium expands SIGMA_X/Z ~30% and increases GAP from 2→4 LDU.

Result: 0% forced on ALL 80 seeds tested — Medium has ample room for 66 parts.

## Visual Notes

- Top-down footprint is ~22×16 studs — roughly 24% larger area than Small
- Pile is taller (39 plates vs ~26) due to Y_MAX=340
- GAP=4 ensures no visual overlap artifacts in Stud.io

## Generation Script

See `gen_pocket14.py` in this folder.

