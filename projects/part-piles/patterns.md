# Part Piles — Confirmed Patterns

Validated from Pockets 3–6 development sessions (2026-04-04 and 2026-04-05).
These override general `learning/patterns.md` when they conflict.

---

## 2026-04-05 — Use rotation-aware AABB for collision, not fixed radii
**Context:** Collision detection between parts with arbitrary 3D orientations
**Pattern:** Compute AABB half-extents from the rotation matrix:
  `ex = |R[0][0]|·a + |R[0][1]|·b + |R[0][2]|·c` (same for ey, ez)
**Why:** Fixed radii assume original orientation. A flat plate standing on edge has ey≈40 LDU,
not 5. Without this, tilted parts falsely pass the collision check → ~25% overlap.
Fixed in Pocket 6, reduced forced placements from 25% to 8%.

---

## 2026-04-05 — Full 3D rotation (Rx, Rz) required for realistic pile look
**Context:** Generating random part orientations
**Pattern:** Always apply rotation around all three axes (Ry × Rx × Rz). Use per-category
`tilt_strength` to control how aggressively parts tilt: plates 0.18–0.25, bricks 0.35–0.50,
accents/tiny 0.50–0.70.
**Why:** Y-axis-only rotation means all parts lie flat face-up — looks like a product display,
not a pile. Rx and Rz create the natural tumbled/scattered look.

---

## 2026-04-05 — Three rotation modes for natural variance
**Context:** Generating per-part rotation
**Pattern:** Sample from three modes: 55% Gaussian tilt (natural wobble), 25% uniform moderate
tilt, 20% fully random (upside-down / on edge). Use `rng.gauss(0, 10 + 35 * tilt_strength)`
for Gaussian mode.
**Why:** Pure Gaussian produces too many "almost flat" parts. The 20% fully-random mode creates
the occasional part clearly on its side or flipped, which makes the pile look real.

---

## 2026-04-05 — Triangular Y distribution biased toward bottom
**Context:** Vertical (Y) position of parts in the pile
**Pattern:** Use `random.triangular(Y_MIN, Y_MAX, Y_MIN + 40)` — peak near the bottom.
**Why:** Uniform Y spreads parts evenly through the full height, looking "airy". Real parts
settle under gravity: most are near the bottom, fewer near the top. Triangular distribution
matches this without needing physics simulation.

---

## 2026-04-05 — Place largest footprint parts first
**Context:** Order of part placement during pile generation
**Pattern:** Sort parts by footprint area (a × c from PART_DIMS) descending before placement.
Large plates go first, tiny parts last.
**Why:** Large plates placed first find open central space. Tiny parts placed last fill the
gaps left around large parts. Reversed order causes large plates to fail in a cluttered
center → ~25% forced placements vs ~8% with correct order.

---

## 2026-04-05 — Multi-seed selection to minimize forced placements
**Context:** Stochastic pile generation with rejection sampling
**Pattern:** Run the full generation loop for 20 different seeds, pick the seed with the
fewest forced placements. Seeds 42–61 work well as the search range.
**Why:** A single seed can be unlucky — one large part may land in a position that blocks
many others. Trying 20 seeds adds ~1s to generation time but reliably finds a near-optimal
arrangement. Typical best: 5/66 forced (~8%).

---

## 2026-04-05 — Part replacement creates a new pocket variant from existing positions
**Context:** Creating Pocket 2 from Pocket 1 without re-doing the layout
**Pattern:** Read model.ldr, replace part IDs using a substitution dict, write to a new .io.
Keep all positions and rotations unchanged.
**Why:** Produces a visually different pile (different part shapes) with the same natural
composition and footprint. Quick way to generate variants without re-running the generator.

---

## 2026-04-05 — Minimal .io package: 3 files only
**Context:** Creating a new .io file from scratch (not modifying an existing one)
**Pattern:** ZIP must contain: `model.ldr` + `.info` + `errorPartList.err`. This is the
minimum Stud.io accepts for opening and rendering. Thumbnail is optional.
**Why:** Stud.io may refuse to open a ZIP missing these files. `errorPartList.err` can be
an empty JSON array `[]`. `.info` needs at minimum a version and total_parts field.
