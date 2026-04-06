# Part Piles — Confirmed Patterns

Validated from Pockets 1–19 development sessions (2026-04-04 through 2026-04-06).
These override general `learning/patterns.md` when they conflict.

---

## 2026-04-05 — Use rotation-aware AABB for collision, not fixed radii
**Context:** Collision detection between parts with arbitrary 3D orientations
**Pattern:** Compute AABB half-extents from the rotation matrix:
  `ex = |R[0][0]|·a + |R[0][1]|·b + |R[0][2]|·c` (same for ey, ez)
**Why:** Fixed radii assume original orientation. A flat plate standing on edge has ey≈40 LDU,
not 5. Without this, tilted parts falsely pass the collision check → ~25% overlap.
Fixed in Pocket 6, reduced forced placements from 25% to 8%.
**Confirmed:** P6–P19

---

## 2026-04-05 — Full 3D rotation (Rx, Rz) required for realistic pile look
**Context:** Generating random part orientations
**Pattern:** Always apply rotation around all three axes (Ry × Rx × Rz). Use per-category
`tilt_strength` to control how aggressively parts tilt: plates 0.18–0.25, bricks 0.35–0.50,
accents/tiny 0.50–0.70.
**Why:** Y-axis-only rotation means all parts lie flat face-up — looks like a product display,
not a pile. Rx and Rz create the natural tumbled/scattered look.
**Confirmed:** P4 (failure), P5–P19 (working)

---

## 2026-04-05 — Three rotation modes for natural variance
**Context:** Generating per-part rotation
**Pattern:** Sample from three modes: 55% Gaussian tilt (natural wobble), 25% uniform moderate
tilt, 20% fully random (upside-down / on edge). Use `rng.gauss(0, 10 + 35 * tilt_strength)`
for Gaussian mode.
**Why:** Pure Gaussian produces too many "almost flat" parts. The 20% fully-random mode creates
the occasional part clearly on its side or flipped, which makes the pile look real.
**Confirmed:** P5–P19

---

## 2026-04-05 — Triangular Y distribution biased toward bottom
**Context:** Vertical (Y) position of parts in the pile
**Pattern:** Use `random.triangular(Y_MIN, Y_MAX, Y_MIN + 50)` — peak near the bottom.
**Why:** Uniform Y spreads parts evenly through the full height, looking "airy". Real parts
settle under gravity: most are near the bottom, fewer near the top.
**Confirmed:** P6–P19

---

## 2026-04-05 — Place largest footprint parts first
**Context:** Order of part placement during pile generation
**Pattern:** Sort parts by footprint area (a × c from PART_DIMS) descending before placement.
Large plates go first, tiny parts last.
**Why:** Large plates placed first find open central space. Tiny parts placed last fill the
gaps left around large parts. Reversed order: ~25% forced placements vs ~8% with correct order.
**Confirmed:** P6–P19

---

## 2026-04-05 — Multi-seed selection to minimize forced placements
**Context:** Stochastic pile generation with rejection sampling
**Pattern:** Run the full generation loop for 60–80 seeds, pick the seed with fewest forced
placements. Use unique seed ranges per pocket (P13: 200–259, P14: 300–379, P15: 400–460, etc.).
**Why:** A single seed can be unlucky. Searching 60–80 seeds reliably finds a clean configuration.
For Medium size, any seed works (0% forced every time) — N_SEEDS can be reduced to 5–10.
**Confirmed:** P7–P19

---

## 2026-04-05 — Part replacement creates a new pocket variant from existing positions
**Context:** Creating a new pocket without re-doing the layout
**Pattern:** Read model.ldr, replace part IDs using a substitution dict, write to a new .io.
Keep all positions and rotations unchanged.
**Why:** Produces a visually different pile with the same natural composition and footprint.
Quick way to generate variants without re-running the generator.
**Confirmed:** P2 (from P1)

---

## 2026-04-05 — Minimal .io package: 3 files only
**Context:** Creating a new .io file from scratch (not modifying an existing one)
**Pattern:** ZIP must contain: `model.ldr` + `.info` + `errorPartList.err`. This is the
minimum Stud.io accepts for opening and rendering. Thumbnail is optional.
**Why:** Stud.io may refuse to open a ZIP missing these files. `errorPartList.err` can be
an empty JSON array `[]`. `.info` needs at minimum a version and total_parts field.
**Confirmed:** P3–P19

---

## 2026-04-05 — Reducing tilt_strength ~0.55× enables flat piles
**Context:** When Y_MAX ≤ 165 LDU (flat pile aesthetic)
**Pattern:** Reduce all tilt_strength values by ~0.55× vs the P6 baseline. This keeps parts
near-flat (ey stays small), allowing them to fit in compressed Y range without AABB conflicts.
Example values: large plates 0.18→0.10, bricks 2×4/2×2 0.35→0.20, slopes 0.50–0.55→0.30–0.35.
**Why:** A plate standing vertically (rx≈90°) has ey≈40 LDU. With Y_MAX=160, only ~2 such
parts fit vertically — the rest are forced. Reducing tilt keeps ey small.
**Confirmed:** P8 (6% forced), P9 floor layer, P10 (8% forced)

---

## 2026-04-05 — ~6–8% forced is the practical floor for flat piles with rejection sampling
**Context:** Generating flat dense piles (Y_MAX ≈ 150–165 LDU) with 65 parts
**Pattern:** Expect ~6–8% forced placements as the practical minimum with rejection sampling.
Do not spend iterations pushing below this — it won't happen. If 0% forced is required for
flat piles, use Blender rigid body physics instead. Taller piles (Y_MAX ≥ 240) can achieve 0%.
**Confirmed:** P8=6%, P9=9%, P10=8%

---

## 2026-04-06 — Medium size is the sweet spot for 66 parts (Recipe 1)
**Context:** Choosing pile size for production pockets
**Pattern:** SIGMA_X=58, SIGMA_Z=46, GAP=4 with 66 parts produces 0% forced on every seed.
Small (SIGMA 44×32, GAP=2) produces visible overlaps in Stud.io even at 0% algorithmic forced
because GAP=2 (0.1 studs) is below the visual threshold for "not overlapping".
**Confirmed:** P13 (Small, visual overlaps), P14–P19 (Medium, 0% forced all seeds)

---

## 2026-04-06 — Y-level separation eliminates fill-vs-hero AABB conflicts
**Context:** Adding fill parts to a completed pile (Recipe 1 fill_gaps, Recipe 2 fill_small_parts)
**Pattern:** Place fill parts at a distinctly different Y range from hero parts (e.g., Y=220–310
while heroes are at Y=0–200). Because Y ranges don't overlap, AABB collision checks between hero
and fill parts almost never trigger. Fill can be placed based purely on XZ coverage without
fighting for Y space.
**Why:** This insight was first applied in P11's 4-layer system and confirmed in Recipe 1
fill_gaps modifier. Origin: user insight that "gaps are visually uncovered areas, not about
where part centers are."
**Confirmed:** P11 (layer 3 at Y=182–210), Recipe 1 fill_gaps (Y=220–310)

---

## 2026-04-06 — VIS_FACTOR=0.60–0.65 for coverage detection
**Context:** Estimating visual coverage (top-down visible area) from AABB
**Pattern:** Use 60–65% of the rotation-aware AABB extents for XZ coverage estimation.
VIS_FACTOR=1.0 reports near-100% coverage even when visible gaps exist (AABB overstates footprint).
VIS_FACTOR=0.50 reports too many false gaps. 0.60–0.65 matches perceived gaps well.
**Implementation:** `vis_ex = ex * VIS_FACTOR` before marking cells as covered on the coverage grid.
**Confirmed:** P11 (0.65), Recipe 1 fill_gaps (0.60), Recipe 2 fill_small_parts (EXISTING_SCALE=0.65)

---

## 2026-04-06 — EXISTING_SCALE=0.65 on nominal dims for Recipe 2 gap detection
**Context:** Gap detection in modifier_fill_small_parts.py (Recipe 2)
**Pattern:** For gap detection in Recipe 2, use 0.65× NOMINAL dims (not rotation-aware AABB).
For a 2×4 brick (dims[0]=40): effective ex = 26 instead of rotation-aware ≈44.
**Why:** Recipe 2 bricks have TILT_STR=0.40 — rotation-aware AABB can be 2× nominal size.
Using full rotation-aware AABB for gap detection reports zero gaps even when visual holes exist.
**Confirmed:** P12-C, P12-D

---

## 2026-04-06 — Touch-point formula for sequential outward placement (Recipe 2)
**Context:** Placing parts sequentially, each touching an existing part without overlapping
**Pattern:** For AABB touch in direction (ca, sa): `d = min((ref_ex+new_ex+GAP)/|ca|, (ref_ez+new_ez+GAP)/|sa|)`.
The min() gives the correct position where the moving part first hits the reference AABB perimeter.
**Why:** A rectangular AABB's touch boundary in a given direction is a diamond/octagon shape.
Circle-based touch is too conservative (2× unnecessary clearance for elongated parts).
**Confirmed:** P12 v2–v4

---

## 2026-04-06 — XZ-only collision for mixed-height top-layer piles (Recipe 2)
**Context:** Sequential outward placement with bricks and plates at different heights
**Pattern:** Use XZ-only collision detection. Assign Y per-type after XZ placement is determined.
Do NOT use 3D AABB collision for top-layer piles — a brick (ey=12) and plate (ey=2) beside
each other in XZ would always trigger the Y collision check even when they're physically separate.
**Confirmed:** P12 v3–v4

---

## 2026-04-06 — Process bottom-to-top for gravity settle
**Context:** modifier_settle_y.py — dropping parts down to simulate gravity
**Pattern:** Sort parts by Y descending (highest Y first = closest to floor in LDraw coords).
Bottom parts get placed first; upper parts "fall" onto the settled bottom parts.
**Why:** Mimics real gravity. A part falling onto a pile rests on whatever is below it.
Processing top-to-bottom would cause parts to "float" above already-settled parts.
**Confirmed:** Recipe 1 modifier_settle_y.py

---

## 2026-04-06 — GAP decreases through Recipe 1 pipeline stages
**Context:** Multiple processing stages each with their own collision GAP parameter
**Pattern:**
  - Generator: GAP=4 LDU (comfortable spacing, no visual overlap artifacts)
  - fill_gaps modifier: GAP=3 LDU (fill parts sit close but not touching)
  - settle_y modifier: GAP=1 LDU (after settling, parts rest in contact)
**Why:** Different stages have different goals. Generator needs room for clean placement.
Fill parts should be close. After settling, physical contact is expected and natural.
**Confirmed:** P14, P14-B, P14-C, P15–P19

---

## 2026-04-06 — N_ANGLES=96 for angle variety in Recipe 2
**Context:** Touch-point candidate generation in sequential placement
**Pattern:** Use N_ANGLES=96 (3.75° step) for placement direction candidates around each
existing part. N_ANGLES=8 produces mechanically regular arrangements (concentric rings).
**Why:** Fewer angles create implicit axis-alignment bias — parts cluster at 0°/45°/90° orientations.
96 angles reduces bias sufficiently (not eliminated due to AABB geometry, but much better than 8).
**Confirmed:** P12 v1 (N=8, too regular), P12 v4 (N=96, natural-looking)

---

## 2026-04-06 — TOP_K=10 random selection breaks concentric ring pattern
**Context:** Selecting placement position from touch-point candidates
**Pattern:** Pick randomly from top-10 center-closest positions (not always the closest).
Always-closest produces a clear "crystal growth" / concentric ring pattern from the top view.
**Why:** Random selection from TOP_K candidates introduces enough variation to break the rings
while still biasing parts toward the center of the pile.
**Confirmed:** P12 v1 (always-closest, rings), P12 v4 (TOP_K=10, natural)

---

## 2026-04-06 — Pocket naming in model.ldr header
**Context:** Naming .io models so they display correctly in Stud.io tab title
**Pattern:** Use `0 Name: {pocket_name}.ldr` (NOT `model.ldr`) on line 2 of the LDR header.
Example: `0 Name: Pocket 15.ldr`
**Why:** Stud.io uses this string as the model name shown in the tab title. Using `model.ldr`
means all pockets show the same tab label, making it impossible to distinguish multiple open files.
**Confirmed:** P14+
