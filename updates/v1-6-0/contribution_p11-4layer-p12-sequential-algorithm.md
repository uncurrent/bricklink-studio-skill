# Contribution: P10 Packaging, P11 4-Layer System, P12 Sequential Outward Algorithm

**Source chat:** "Pockets-Receipe-2" (2026-04-06)
**Pockets developed:** P10 (packaging), P11 (4-layer coverage), P12 and variants B/C/D
**Algorithms:** 4-layer Y-separation coverage (P11), touch-point sequential placement (P12 v1–v4), rotation shuffle modifier, Monte Carlo gap fill modifier
**Key deliverable:** Recipe 2 top-layer algorithm (sequential outward placement) + two post-processing modifiers. Full Recipe 2 pipeline in `Pockets-receipe-2/`.

---

## 1. What Was Developed in This Chat

### 1.1 Pocket 10 — Packaging and Retrospective

P10 was already generated in a prior session. This chat:
- Packaged the existing `/tmp/pocket10_model.ldr` into a `.io` ZIP
- Wrote `Pockets/Pocket 10/NOTES.md` documenting the generation parameters

**P10 stats:** seed=107, 5/65 forced (8%), footprint 12.3 studs Z, 2-layer Gaussian.

**Key insight documented in P10 NOTES:** For flat piles with rejection sampling, the practical lower bound for forced overlap is around 6–8%. Forced overlap below this requires either increasing the oval, reducing part count, or switching to a different algorithm. This motivated P11's redesign.

---

### 1.2 Pocket 11 — 4-Layer Coverage System

**Origin of the idea:** User proposed splitting generation into distinct phases — first top layer with big parts, then accents, then fill visible gaps, then tiny fill. The key user insight: "гепы это непокрытые области визуально, а не наличие центров деталей" (gaps are visually uncovered areas, not about where part centers are). This led to the coverage-based Y-separation approach.

**Algorithm overview (4 layers):**

1. **Layer 1+2 (Heroes + Accents):** Large parts + medium accents placed using Gaussian XZ at Y=[0,175]. Sorted largest-footprint-first.
2. **Layer 3 (Gap Fill Plates):** Flat plates placed at Y=[182,210] — below the hero layer in LDraw coords — specifically targeting uncovered cells within a TIGHTER oval (FILL_OVAL).
3. **Layer 4 (Tiny Fill):** Very small parts (1×1 plates, round plates) at the bottom.

**The Y-level separation insight:** By placing fill parts at a distinctly different Y range (182–210) from hero parts (0–175), the AABB collision checks almost never trigger between hero and fill parts. The algorithm can place fill parts without fighting hero parts for space. This is the key innovation — the same insight later used in Recipe 1's fill_gaps modifier.

**Coverage grid and visual correction factor:**

The coverage detection used a grid with GRID_RES=12 LDU per cell. For each placed hero part, the cells it "covers" were computed using **0.65× of the rotation-aware AABB extents**, not the full AABB. This correction accounts for the fact that a tilted part's full AABB substantially overstates its visual footprint as seen from the top. Without this correction, a single tilted 2×4 plate would report 100% coverage of a large area when it actually covers much less.

**Value 0.65 is empirical** — tested at 0.50 (detected too many false gaps), 0.75 (missed real gaps), and settled at 0.65 as the best visual match. It approximates the average ratio of the actual top-view projection area to the AABB area for a randomly tilted part.

**FILL_OVAL vs PLACEMENT_OVAL distinction:**

A critical discovery: fill plates placed at the boundary of the full placement oval had their AABBs extending *outside* the oval, causing the footprint to be much wider than intended. Fix: gap detection uses a TIGHTER oval (FILL_OVAL = 85% of placement OVAL), and an explicit overflow check rejects any fill part whose AABB extends beyond `FILL_OVAL × 1.12`.

```python
OVAL_A      = 190, OVAL_B = 140    # hero placement oval
FILL_OVAL_A = 162, FILL_OVAL_B = 125  # coverage detection oval (tighter)

# Overflow check for fill plates:
if abs(px - CX) + _ex_pre > FILL_OVAL_A * 1.12: continue
if abs(pz - CZ) + _ez_pre > FILL_OVAL_B * 1.12: continue
```

**Development history — parameter tuning:**

*Attempt 1 — Y_HERO_MAX=90:*
- Result: forced=17–31 (very high!)
- Root cause: 45 parts in Y=[0,90] is physically too compressed — fill ratio in that volume approaches 86%
- With so many large parts trying to fit in a thin Y band, overlap is unavoidable

*Fix — Y_HERO_MAX=175:*
- Result: forced=2–9 (normal)
- Doubling the Y range for heroes nearly eliminates forced overlap

*Attempt 2 — First fill implementation had footprint overflow:*
- Fill plates generated at 21.8×16.4 studs (too wide — 19% larger than target)
- Root cause: fill plates placed near oval boundary have AABB extending outside
- Fix: FILL_OVAL (162×125 vs 190×140) + overflow check
- Result: footprint corrected to 18.4×13.6 studs

*Attempt 3 — Coverage=100% with tilt (false positive):*
- The coverage map was reporting 100% after only placing tilted plates
- Root cause: tilted plates' full AABB appeared to cover all cells even when visual gaps existed
- Fix: apply 0.65× scale factor to ex/ez for coverage calculation: `vis_ex = ex * 0.65`

**Final P11 result:** seed=78, 2/61 forced (3.3%), footprint=18.4×13.6 studs, visual coverage=100% (after correction). This was the best forced-overlap result ever achieved in the project at the time.

**P11 hero palette (45 parts):**

| Part | Count | Role |
|------|-------|------|
| Brick 2×4 | 8 | Hero |
| Brick 2×2 | 6 | Hero/accent |
| Plate 2×4 | 12 | Mid-layer |
| Plate 2×3 | 6 | Mid-layer |
| Plate 2×2 | 6 | Mid-layer |
| Plate 1×4 | 4 | Edge fill |
| Tile 2×2 | 3 | Accent |

---

### 1.3 Pocket 12 — Sequential Outward Placement (Recipe 2)

#### 1.3.1 Why a New Algorithm?

After P11 achieved excellent results for the layered system, the user requested a fundamentally different approach for P12: a top layer only, but placed *sequentially from center outward, not on a grid, not with rejection sampling*. The specific user request: "ставишь одну деталь под некоторым углом и идешь по кругу прикрепляя почти встык детали одну за другой" (place one part at some angle and go around in a circle attaching almost flush parts one after another).

This triggered development of the **touch-point sequential algorithm** — what became Recipe 2.

**Reference analysis of P1 (user reference pile):**

Before developing the algorithm, P1 was analyzed to understand target density:
- 89 parts total
- Median XZ nearest-neighbor distance = 16.2 LDU (0.87 studs!)
- 72% of parts within 1 stud of their nearest neighbor
- Y span = 264 LDU = 33 plates
- Composition: ~50–60% plates/tiles + 40–50% bricks
- Top view: extreme density at varied angles — parts almost touching at arbitrary rotations

This analysis confirmed the target: parts should nearly touch, at truly varied angles (not discretized), with mixed bricks and plates.

---

#### 1.3.2 Touch-Point Formula — Derivation

**Core idea:** When placing a new part at angle `(ca, sa)` relative to a reference part, what is the distance `d` such that the new part's AABB just touches (but doesn't overlap) the reference part's AABB?

For AABB `(ref_ex, ref_ez)` and new part `(ex, ez)` moved distance `d` in direction `(ca, sa)`:
- In X: the displacement is `d*ca`. For no X-overlap: `|d*ca| = ref_ex + ex + GAP`
  → `d = (ref_ex + ex + GAP) / |ca|`
- In Z: the displacement is `d*sa`. For no Z-overlap: `|d*sa| = ref_ez + ez + GAP`
  → `d = (ref_ez + ez + GAP) / |sa|`
- The actual touching distance must satisfy BOTH simultaneously.
  For AABB touch, we want the MINIMUM distance that causes the first axis to just touch:

```python
def touch_distance(ref_ex, ref_ez, new_ex, new_ez, ca, sa):
    aca, asa = abs(ca), abs(sa)
    if aca < 1e-9: return (ref_ez + new_ez + GAP) / asa   # pure Z direction
    if asa < 1e-9: return (ref_ex + new_ex + GAP) / aca   # pure X direction
    dx = (ref_ex + new_ex + GAP) / aca   # distance to touch in X
    dz = (ref_ez + new_ez + GAP) / asa   # distance to touch in Z
    return min(dx, dz)                    # the closer constraint triggers first
```

**Geometric interpretation:** A rectangular AABB's "touch boundary" in a given direction is not circular — it's a diamond/octagon shape. The `min()` gives the correct position where the moving part first hits the reference part's AABB perimeter.

**Alternatives considered and rejected:**
- Circle-based touching: use `sqrt(ref_ex² + ref_ez²)` as a radius. Rejected: too conservative, creates excessive gaps for elongated parts (a 2×4 plate in its short direction would have 2× unnecessary clearance)
- Grid-based snapping: snap the touch position to the nearest LEGO grid point. Rejected: produces clearly mechanical-looking patterns

---

#### 1.3.3 P12 v1 — Initial Grid-Based Implementation

**Algorithm:** `N_ANGLES=8` discrete angles (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°). Touch-point formula applied. Always pick closest-to-center candidate.

**Part palette:** All plates and tiles, no bricks.

**Result (seed=69):** 32 parts placed, footprint 17.4×13.7 studs.

**User feedback:** "они все расположились очень примитивно" (they are all arranged very primitively). The parts look like they're placed on a sparse grid rather than scattered naturally.

**Root causes identified:**
1. **Discrete angles:** Only 8 angle choices → parts align along 0/45/90/135° which creates a very regular looking arrangement
2. **Always-closest-to-center creates concentric rings:** The greedy "pick closest to center" always picks positions that form a regular ring around the previous ring
3. **No bricks:** All plates look flat and similar from the top
4. **GAP was positive:** Parts visually further apart than reference pile

---

#### 1.3.4 P12 v2 — Continuous Angles + Negative GAP

**Key changes from v1:**
- `ry = rng.uniform(0, 2*math.pi)` — fully continuous random Y-rotation (no discrete snapping)
- `GAP = -4` — negative gap allows parts to slightly overlap at AABB level ("nearly touching" effect)
- `N_ANGLES = 72` (up from 8) — more candidate positions to evaluate
- `TOP_K = 6` — pick randomly from top-6 closest-to-center positions (break concentric-ring pattern)

**Screenshot result:** Massive transparent overlaps from top view. Side view: everything in one flat plane. All parts were plates.

**User feedback:** (1) too many overlaps, (2) all in one plane, (3) too similar parts — need bricks.

**Root cause of overlaps:** GAP=-4 with continuous rotation means parts can overlap by 4 LDU in *each* AABB dimension. For plates at various orientations, this caused many parts to pile directly on top of each other (the 3D overlap check was too permissive for thin flat parts).

**Root cause of "one flat plane":** Y_JITTER=4 LDU (1 plate height) is imperceptible. No bricks means no visual height variation.

**Root cause of all-plates look:** Palette contained only plates and tiles.

---

#### 1.3.5 P12 v3 — XZ-Only Collision + Bricks

**Key changes from v2:**
- **XZ-only collision detection** — Y position is assigned decoratively after placement, not used for collision
- Different Y assignment per part type:
  - Bricks: `y = rng.uniform(-22, -8)` → bricks stick up visually
  - Plates: `y = rng.uniform(-8, 8)` → plates lie nearly flat
  - Tiles: `y = rng.uniform(-4, 6)` → between plates and bricks
- **Mixed palette:** 13 bricks (40% of total) + 36 plates/tiles
- **GAP = -6** (tried to keep tight packing)
- `TILT_STR = {"brick": 0.25, "plate": 0.06, "tile": 0.04}`

**Why XZ-only collision:**
The fundamental problem with 3D AABB collision for a pile simulation is that bricks (ey=12) and plates (ey=2) at the same Y position will always "collide" in the Y dimension even when they're physically beside each other in XZ. Separating the concerns — XZ determines placement, Y is assigned per-type — is cleaner for a pile where parts at different heights coexist.

**Result (seed=62):** 36 parts placed, footprint 18.7×14.4 studs. Bricks visible and colorful!

**User feedback:** "уже лучше" (already better). Remaining issues: (1) still too many overlaps (GAP=-6 too aggressive for visible parts), (2) all bricks face same direction (continuous random ry doesn't guarantee angle variety in placement), (3) oval still slightly too small.

**Root cause of residual overlaps:** GAP=-6 allows 6 LDU overlap in each XZ direction. For a 1×2 plate (ez=10), that's 60% of the half-extent — very visible. For bricks it was also noticeable.

---

#### 1.3.6 P12 v4 — Final Top-Layer Algorithm (GAP=0, Larger Oval, More Tilt)

**Key changes from v3:**
- `GAP = 0` — no XZ overlaps at all
- `OVAL_A = 185, OVAL_B = 145` (previously 170×132) — larger oval needed to accommodate parts at non-axis-aligned angles (a 2×4 plate at 45° has AABB 42×42, not 40×20)
- `TILT_STR = {"brick": 0.40, "plate": 0.07, "tile": 0.04}` — bricks tilt significantly (occasionally 20-30°, looks "thrown")
- Brick Y: `rng.uniform(-30, -4)` — wider range, bricks stick up more
- `N_ANGLES = 96` — finer angle sampling reduces axis-alignment bias
- `TOP_K = 10` — larger pool for random selection

**Why larger oval?**
A part at exactly 45° Y-rotation has XZ AABB at its maximum: for a 2×4 plate (40×20), the 45° AABB is ≈(42.4, 42.4) — almost square and much larger than the axis-aligned (40, 20). If the oval is too small, only axis-aligned placements (0°/90°) consistently fit within it, creating an implicit bias toward axis-aligned orientations. Enlarging the oval removes this bias.

**Final result (seed=100):** 31/50 parts placed, footprint 21.1×15.7 studs. 14 bricks (visible at various angles and heights) + 17 plates/tiles.

**Why only 31 of 50 parts?** The remaining 19 failed to find valid XZ positions. With GAP=0, a 2×4 plate (nominal footprint 80×40 LDU) requires 80×40 of clear XZ space. With 31 parts already placed, and the oval ≈77,000 LDU², there simply isn't room. This is expected and acceptable — 31 parts for a top layer is a reasonable density.

**Axis-aligned bias analysis:**
N_ANGLES=96 means angle step = 360°/96 = 3.75°. At 0° and 90°, a 2×4 plate has AABB (40, 20). At 45°, AABB is (42.4, 42.4). The larger AABB at 45° makes it harder to fit within the oval, subtly biasing placements. This is a known limitation of AABB-based sequential placement — fully correctable only with OBB collision or SAT, which weren't implemented.

---

#### 1.3.7 P12 Modifier: rotation_shuffle

**Developed because:** Even with random Y-rotation, all bricks in the v4 base have studs facing up. The user wanted visible diversity in orientation — some parts showing their side face, some upside-down.

**Rotation mode distribution (final):**

| Mode | Probability | Description |
|------|-------------|-------------|
| Upright | 50% | Normal, small tilt. `rx = gauss(0, 8°)` |
| Leaning | 20% | Medium tilt 15–35°. `rx = gauss(0, 22°)` |
| On-side | 17% | ≈90° rotation shows side face from top |
| Upside-down | 5% | ≈180° rotation shows anti-stud underside |
| Extreme | 8% | 45°–70° dramatic diagonal tilt |

**How ratios were determined:** Ratios were set by intuition (50/70/87/92/100 probability thresholds), not empirically tested across multiple seeds. They weren't iterated — user did not request refinement of the specific ratios. The main goal was to have all modes present and on-side/upside-down being minority.

**Y position by mode:** When a brick is on-side (90° X rotation), its effective height changes — it now extends sideways, not up. Y is adjusted per-mode:
- Upright bricks: y = uniform(-28, -6) — normal height
- On-side bricks: y = uniform(-16, 0) — lower, as the part is wider now
- Upside-down bricks: y = uniform(-28, -8) — similar to upright

**Implementation note:** XZ positions are preserved from the v4 placement. Rotation is fully replaced (new ry = random, new rx/rz per mode). Some slight XZ overlap may occur for parts with very large new rotations, but this is accepted as "pile-like" contact.

---

#### 1.3.8 P12 Modifier: fill_small_parts

**Filler palette (25 parts, plus 3 special-limit-1):**

| Parts | Count | Limit |
|-------|-------|-------|
| 1×1 Plate | 8 | unlimited |
| 1×1 Tile | 6 | unlimited |
| 1×1 Round Plate | 4 | unlimited |
| 1×1 Brick | 4 | unlimited |
| 1×1 Round Brick | 3 | unlimited |
| 1×2 Plate | 6 | unlimited |
| 1×2 Tile | 4 | unlimited |
| 1×2 Brick | 3 | unlimited |
| Gear 24T (3648b) | — | max 1 |
| Gear 8T (3647) | — | max 1 |
| Technic Pin (2780) | — | max 1 |

**Algorithm — why Monte Carlo instead of grid:**

*Initial approach (grid-based):* Build coverage grid, find uncovered cells, try to place fillers at gap cells. FAILED because:
- `placed_xz` was populated with rotation-aware AABB extents
- A 2×4 brick at 45° tilt has AABB ex=ez≈44 LDU (vs nominal 40×20)
- With 31 such parts, the entire oval is "covered" by their AABBs
- Only 98 gap cells found out of 1423 total oval cells
- Zero valid filler positions found (every gap cell within 58 LDU of an AABB center)

*Root cause:* AABB of a brick with `TILT_STR=0.40` can be up to **2× the nominal part size** in each XZ direction. This is because the Y half-extent (12 LDU) contributes to the XZ extents when the rotation matrix has non-zero off-diagonal terms:
```
ex = |R[0][0]|*40 + |R[0][1]|*12 + |R[0][2]|*20
```
At ry=45°, rx=15°: ex ≈ 44 LDU (vs nominal 40). This affects every tilted brick.

*Fix — `EXISTING_SCALE = 0.65`* on NOMINAL dims:
Instead of using the rotation-aware AABB for existing parts' collision radius in gap detection, use:
```python
ex = dims[0] * EXISTING_SCALE   # 0.65 × nominal half-x
ez = dims[2] * EXISTING_SCALE   # 0.65 × nominal half-z
```
For a 2×4 plate (dims[0]=40): effective ex = 26 instead of 44. This gives realistic gap detection.

**Why 0.65?** Same empirical value from P11's visual coverage correction. It approximates the average ratio of visual footprint to AABB for randomly oriented parts. Coincidentally the same value used for P11 coverage detection and Recipe 1's fill_gaps (which uses 0.60–0.65).

**Monte Carlo placement:** For each filler part in the pool, try up to 300 random positions within the oval:
1. Sample `nx = cx + uniform(-oval_a, oval_a)`, `nz = cz + uniform(-oval_b, oval_b)`
2. Reject if outside oval (rejection sampling)
3. Assign random Y-rotation + small tilt
4. Check XZ overlap with `placed_now` using `FILLER_GAP=4`
5. Place if clear, otherwise try next random position

**Result:** 20 filler parts placed in both 12-C and 12-D.

---

## 2. Evolution Summary

| Version | Key Change | Problem Solved | New Problem Introduced |
|---------|-----------|----------------|----------------------|
| P12 v1 | Sequential outward, N_ANGLES=8, all plates | Baseline working algorithm | Too primitive/regular, concentric rings |
| P12 v2 | Continuous rotation, GAP=-4, N_ANGLES=72, TOP_K=6 | Angle variety | Massive overlaps, all in one plane, only plates |
| P12 v3 | XZ-only collision, Y by type, bricks added, GAP=-6 | Height variation, bricks visible | Still some overlaps, axis-bias from small oval |
| P12 v4 | GAP=0, oval 185×145, TILT=0.40 for bricks, N_ANGLES=96, TOP_K=10 | Overlaps eliminated, better angle variety | Only 31/50 parts fit (acceptable) |
| P12-B | rotation_shuffle modifier (50/20/17/5/8) | Visual orientation diversity | — |
| P12-C | fill_small_parts Monte Carlo modifier | Gap fill with small parts + special parts | — |
| P12-D | Both modifiers combined | Full visual variety + density | — |

---

## 3. What Failed

### 3.1 Discrete Angles in v1

**Tried:** N_ANGLES=8 (0°, 45°, 90°, 135° etc.) for touch-point candidates.
**Failed because:** Parts invariably align to the 8 "allowed" angles, creating visually mechanical arrangement.
**Fix:** Fully continuous ry = uniform(0, 2π). The N_ANGLES parameter now refers only to the number of placement-direction candidates around each existing part — not the part's own rotation.

### 3.2 Always-Closest-to-Center Selection

**Tried:** Always pick the closest-to-center candidate from all available positions.
**Failed because:** This produces a clear "crystal growth" pattern — each new ring of parts is exactly one AABB-width away from the previous ring. From the top, this looks like concentric shapes rather than a scattered pile.
**Fix:** TOP_K=10 random selection weighted by 1/rank — parts are usually near center but with enough randomness to break the ring pattern.

### 3.3 GAP = -4 and -6

**Tried:** Negative GAP values to force visual "nearly touching" like the reference pile.
**Failed because:** With XZ-only collision and continuous rotation, GAP=-6 allows the algorithm to place a 1×2 plate's center within 4 LDU of an existing part's AABB boundary — which is 60% of the plate's half-extent. This causes clearly visible visual collision in Stud.io, not the subtle "touching" effect intended.
**Fix:** GAP=0 + larger oval. The "nearly touching" look comes from varied angles and part density, not from actual AABB overlap.

### 3.4 3D AABB Collision for Mixed-Height Pile

**Tried:** 3D AABB overlap check: `abs(y1-y2) < ey1+ey2+GAP` in addition to XZ check.
**Failed because:** A brick (ey=12) and a plate (ey=2) that are BESIDE each other in XZ will have Y overlap: `abs(0-0) = 0 < 12+2 = 14`. The algorithm would report them as colliding even when they're physically separated in XZ. This prevented any mixed-height pile from being generated.
**Fix:** XZ-only collision. Assign Y per-type as a decoration step after XZ placement is determined.

### 3.5 Grid-Based Gap Detection for fill_small_parts

**Tried:** Build GRID_RES=8 LDU coverage grid, find uncovered cells, try to place filler at each gap cell.
**Failed because (two failure modes):**
1. Using rotation-aware AABB extents for coverage: tilted bricks at 45° have ex≈44, marking 1423 cells covered out of 1500 total oval cells → only 98 gap cells found, zero valid placements.
2. Even with correct gap detection, placing a 1×1 filler (ex=10) at a gap cell blocks all adjacent cells (within 10+10+4=24 LDU), so after placing the FIRST filler, subsequent gap cells are all blocked.
**Fix:** Monte Carlo placement: random position sampling with EXISTING_SCALE=0.65 correction.

### 3.6 Small Oval (170×132) with GAP=0

**Tried:** Reducing oval size after v2's large oval was causing spread-out look.
**Failed because:** At GAP=0, a 2×4 plate at 45° needs AABB room of ~42×42 LDU. In a 170×132 oval, this leaves much less room than expected, causing many placements to fail. This ALSO creates an implicit axis-alignment bias: parts at 0°/90° fit more easily (smaller AABB) than parts at 45° (larger AABB).
**Fix:** OVAL_A=185, OVAL_B=145 — enough room that 45° parts fit without significantly more difficulty than 0° parts.

### 3.7 Sorting Big→Small Then Shuffling with Small Jitter

**Tried:** Sort palette by footprint descending, then `shuffle within ±4 positions` to vary order slightly.
**Outcome:** With big bricks first and GAP=0, only 18–26 parts placed (big bricks fill the oval quickly). Changed sorting to `shuffle with ±4 positions` only (no rigid big-first sorting) — but this also wasn't much better.
**Fix:** The real issue was oval size, not sorting strategy. With oval 185×145 and shuffled palette, 31/50 parts is achievable.

---

## 4. Confirmed Patterns

### Pattern: XZ-Only Collision for Multi-Height Piles

When a pile has mixed part types (bricks + plates) at different Y levels, XZ-only collision detection with Y assigned per-type produces better results than 3D AABB. The separation of concerns — "where does it go (XZ)" vs "how high is it (Y)" — is cleaner and more controllable.

### Pattern: Y-Level Separation for Layer Systems

Both P11 and Recipe 1's fill_gaps use the same core insight: give different part categories distinct Y ranges. Hero parts at Y=[0,175], fill plates at Y=[182,210] in P11; hero parts at Y=0–200, fill parts at Y=220–310 in Recipe 1. With separated Y ranges, AABB collisions between categories become extremely rare.

### Pattern: AABB of Tilted Parts Can Be 2× Nominal Size

For a part with TILT_STR=0.40 (gauss 0, 12°), a single extreme tilt (e.g., 30°) combined with 45° Y-rotation can cause AABB to be ~2× the nominal part dimensions. This affects coverage detection, gap filling, and any other algorithm that uses AABB for area estimation. **Always use a scale factor (0.60–0.65× nominal dims) when using AABB for coverage/visual estimation.**

### Pattern: Touch-Point Formula for Sequential Placement

```python
def touch_distance(ref_ex, ref_ez, new_ex, new_ez, ca, sa):
    aca, asa = abs(ca), abs(sa)
    if aca < 1e-9: return (ref_ez + new_ez + GAP) / asa
    if asa < 1e-9: return (ref_ex + new_ex + GAP) / aca
    return min((ref_ex + new_ex + GAP) / aca,
               (ref_ez + new_ez + GAP) / asa)
```

This reliably places parts at exact AABB-touch distance in any direction. Works for any convex axis-aligned bounding box. The `min()` gives the first AABB face to be touched along the direction.

### Pattern: Monte Carlo > Grid for Gap Fill After Heavy Tilting

When existing parts have significant tilt, their AABB drastically overstates their visual footprint. Grid-based gap detection using AABB extents reports the entire oval as covered. Monte Carlo placement with `EXISTING_SCALE=0.65 × nominal dims` for collision checking is more reliable and simpler to implement.

### Pattern: N_ANGLES=96 Reduces Axis-Alignment Bias

With N_ANGLES=48 or fewer, the 0°, 90°, 45° directions are over-represented (each gets one candidate while intermediate angles share fewer). With N_ANGLES=96 (3.75° step), the distribution is fine enough that no particular direction dominates. Going to N_ANGLES=192 showed no visible improvement in practice.

### Pattern: Random FROM Top-K Candidates, Not Always The Best

Always picking the closest-to-center candidate produces concentric ring patterns. Picking randomly from the top-K=10 candidates (weighted by 1/rank) with `w_i = 1/(i+1)` introduces enough variability to break regularity while still biasing toward the center. This is the key to the "organic scatter" look.

---

## 5. Parameters Tuned

### P11 4-Layer System

| Parameter | Initial | Final | How determined |
|-----------|---------|-------|----------------|
| Y_HERO_MAX | 90 | 175 | Initial caused forced=17–31. Doubling the Y range nearly eliminates forced |
| OVAL_A / OVAL_B | 190 / 140 | 190 / 140 (unchanged) | Original value was good; modified FILL_OVAL instead |
| FILL_OVAL_A / B | — | 162 / 125 | 85% of OVAL to prevent boundary overflow |
| Overflow check factor | — | 1.12 | `abs(px-CX) + ex_pre > FILL_OVAL_A * 1.12` — empirical |
| Coverage vis_ex scale | 1.0 (false positive) | 0.65 | Tested 0.50, 0.75, settled at 0.65 visually |
| GAP | 2 | 2 | Not changed — standard for Recipe 1-inherited approach |
| Y_FILL_MIN / MAX | first try | 182 / 210 | 7 LDU gap above Y_HERO_MAX=175 to clearly separate layers |

### P12 v1→v2→v3→v4

| Parameter | v1 | v2 | v3 | v4 | Why changed |
|-----------|----|----|----|----|-------------|
| GAP | 4 | -4 | -6 | 0 | v2: too few parts fit. v3: still overlaps. v4: zero overlap, larger oval instead |
| OVAL_A / OVAL_B | 162/125 | 162/125 | 170/132 | 185/145 | Gradually increased to accommodate 45° parts |
| N_ANGLES | 8 | 72 | 72 | 96 | More candidates = less axis-alignment bias |
| TOP_K | 1 | 6 | 8 | 10 | Wider pool = more organic scatter |
| Collision | 3D AABB | 3D AABB | XZ-only | XZ-only | Mixed heights need XZ-only |
| ry | discrete (8 choices) | continuous | continuous | continuous | Discrete = mechanical look |
| TILT_STR bricks | 0.10 | 0.05 | 0.25 | 0.40 | v4: user wanted visibly thrown bricks |
| Y for bricks | Y_BASE±4 | Y_BASE±4 | uniform(-22,-8) | uniform(-30,-4) | Bricks need to visibly stick up |
| Part mix | plates only | plates only | 30% bricks | 30% bricks | User request: mix plates and bricks |
| N_PARTS_MAX | 36 | 36 | 50 | 50 | Increased to fill larger oval |
| N_SEEDS | 40 | 40 | 50 | 60 | More seeds for better result |

### Modifier Parameters

| Modifier | Parameter | Value | How determined |
|----------|-----------|-------|----------------|
| rotation_shuffle | Upright probability | 50% | Intuitive split — majority still upright |
| rotation_shuffle | On-side probability | 17% | Enough for visual variety without looking chaotic |
| rotation_shuffle | On-side rx | `90° + gauss(0, 10°)` | Small jitter around 90° for naturalness |
| rotation_shuffle | Leaning rx | `gauss(0, 22°)` | 22° std dev gives occasional 40-50° tilts |
| fill_small_parts | EXISTING_SCALE | 0.65 | Same value as P11 visual coverage correction |
| fill_small_parts | FILLER_GAP | 4 | Match standard GAP, prevent visual proximity |
| fill_small_parts | MAX_FILL_PARTS | 20 | Prevents over-filling the gaps |
| fill_small_parts | MAX_TRIES_PER_PART | 300 | Enough for Monte Carlo success in sparse oval |

---

## 6. Scripts Created

All scripts stored in `BrickitStudio/Pockets-receipe-2/`:

### generator_toplayer_v4.py

**Purpose:** Generate Recipe 2 top layer — sequential outward placement of mixed bricks/plates/tiles.
**Algorithm:** XZ-only collision, touch-point formula, N_ANGLES=96 candidates, TOP_K=10 random selection from closest, Y assigned per-type, best-of-60-seeds.
**Key variables:** CX, CZ (center), OVAL_A, OVAL_B (placement oval), GAP=0, TILT by part type.
**Output:** `/tmp/pocket12_toplayer_v4.ldr`

### modifier_rotation_shuffle.py

**Purpose:** Post-process a top-layer LDR to diversify rotations.
**Input:** List of LDR lines.
**Output:** New lines with same XZ positions but randomized rotations (per-mode distribution).
**Modes:** upright / leaning / on-side / upside-down / extreme-diagonal.
**Key function:** `apply_rotation_shuffle(lines, seed)`

### modifier_fill_small_parts.py

**Purpose:** Post-process a LDR to add small filler parts in gaps.
**Input:** Base LDR lines (parsed to get XZ positions for collision).
**Algorithm:** Monte Carlo — random position sampling with EXISTING_SCALE=0.65 collision checking.
**Output:** List of new filler part lines to append.
**Key function:** `apply_fill_small(base_lines, _ignored_placed_xz, seed, cx, cz, oval_a, oval_b)`
**Special parts:** Gear 24T, Gear 8T, Technic Pin (each max 1 per pocket).

### generator_toplayer_with_modifiers.py

**Purpose:** Driver script — runs v4 base (seed=100) then applies modifiers to produce 12-B, 12-C, 12-D.
**Output:** Three LDR files in `/tmp/`: pocket12B.ldr, pocket12C.ldr, pocket12D.ldr.

### output/ folder

| File | Parts | Description |
|------|-------|-------------|
| `Pocket 12 (base-v4).io` | 31 | Base v4 output |
| `Pocket 12-B (rotation-shuffle).io` | 31 | Rotation shuffle applied |
| `Pocket 12-C (small-fillers).io` | 51 | Small fillers added (20 parts) |
| `Pocket 12-D (both-mods).io` | 51 | Both modifiers applied |

### Also in Pockets/Pocket 12/

- `gen_pocket12_toplayer.py` — v1 script
- `gen_pocket12_toplayer_v2.py` — v2 script
- `gen_pocket12_toplayer_v3.py` — v3 script
- `gen_pocket12_toplayer_v4.py` — v4 script (same as in Pockets-receipe-2/)
- `gen_pocket12_BCD.py` — driver (same as generator_toplayer_with_modifiers.py)
- `mod_rotate.py`, `mod_fill.py` — original modifier scripts

---

## 7. Open Questions and Next Steps

### Not Implemented — Discussed or Observed

1. **Hero/accent lower layers for Recipe 2:** The current pipeline only generates the top layer. The next step is adding hero bricks with significant tilt at lower Y levels (like P11's Layer 1+2), then accents, then the top layer on top. The top-layer algorithm is intentionally a separate step to allow iterative refinement.

2. **OBB or SAT collision instead of AABB:** The axis-alignment bias in placement (easier to fit 0°/90° parts than 45° parts) could be eliminated with oriented bounding box collision. This would also reduce the apparent AABB bloat for tilted bricks. Not implemented due to complexity.

3. **Tighter TOP_K probability curve:** Currently `w_i = 1/(i+1)` weighting. A steeper curve (e.g., exponential) would make placement more center-biased. Worth experimenting if the pile looks too spread-out.

4. **Settle_Y for Recipe 2:** Recipe 1's settle_y modifier compacts parts vertically by gravity simulation. Recipe 2 currently assigns Y decoratively per-type — a settle pass would make the pile physically more plausible (bricks actually resting on plates below them).

5. **Coverage check for Recipe 2 top layer:** Currently no visual coverage check — gap-filling is done by the fill_small modifier. Could add a coverage computation after v4 placement to report what % of the oval is visually covered before fill.

6. **Axis-alignment bias quantification:** No measurement was done of how often parts end up at 0°/90° vs 45°/135° orientations. If the bias is significant, a solution could be to preferentially accept new rotations that are "far" from existing part orientations (e.g., reject if new ry is within 10° of any existing placed part's ry).

7. **Coloring integration:** Recipe 2 pockets have not been tested with the colorize modifier. The current outputs use the default 20-color palette from COLORS list. Applying the palette system from Pockets-coloring/ would be the next step for production.

8. **Validation: P12-D vs P1 reference:** The original target was to match P1's density (median NN=16.2 LDU). P12-D with 51 parts in ~21×16 studs = ~336 LDU² per part. P1 had 89 parts in roughly similar area, so P1 is ~2× denser. Increasing N_PARTS_MAX and accepting more forced might be needed for production quality.

---

## 8. Gaps from SKILL_UPDATE_BRIEF Addressed by This Chat

From Section 2 of the brief:

- ✅ **P11 full development history** — fully documented: Y-level separation idea, parameter tuning (Y_HERO_MAX 90→175, FILL_OVAL), 0.65× correction origin, FILL_OVAL vs OVAL distinction.
- ✅ **P12 evolution v1→v2→v3→v4** — fully documented: each version's key change, problem solved, new problem introduced.
- ✅ **Touch-point formula derivation** — geometrically explained, `min(dx, dz)` rationale.
- ✅ **Modifier development** — rotation mode ratios and fill algorithm explained.
- ✅ **EXISTING_SCALE=0.65 workaround** — origin documented (empirical, same value as P11 0.65 coverage correction).
- ✅ **What failed in Recipe 2** — 7 specific failed approaches documented with root causes.
- ❌ **P9 two-layer system details** — P9 is NOT from this chat. P9 was developed in the Recipe 2 earlier session (not this one). This chat starts at P10.
- ❌ **Coloring palettes** — not developed in this chat.
- ❌ **Render settings** — not relevant to this chat.
