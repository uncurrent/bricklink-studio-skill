# Part Piles — Failed Patterns & Anti-patterns

Documented from Pockets 1–19 development. Check before attempting anything unfamiliar.

---

## 2026-04-04 — Editing model.lxfml has no effect on Stud.io rendering
**What was tried:** Modifying the XML in `model.lxfml` inside the .io ZIP.
**What happened:** Model in Stud.io viewport didn't change at all despite correct XML edits.
**Avoid because:** Stud.io renders from `model.ldr` (LDraw), not from LXFML. LXFML is secondary metadata.
**Alternative:** Always edit `model.ldr`. LXFML can be left unchanged for programmatically generated files.

---

## 2026-04-05 — Y-rotation only produces fake-looking pile (Pocket 4)
**What was tried:** Generating part orientations with rotation around Y axis only.
**What happened:** All parts lie flat face-up — pile looks like parts laid out on a table for display.
**Avoid because:** Y is the vertical axis. Rotating around it only spins the part on its base.
**Alternative:** Full 3D rotation matrix (Ry × Rx × Rz) with per-category tilt_strength.

---

## 2026-04-05 — Fixed ellipsoid bounding volumes ignore orientation (Pocket 5)
**What was tried:** Assigning each part fixed `(r_horizontal, r_vertical)` radii for collision.
Flat plate: `r_v = 5 LDU`. Brick: `r_v = 14 LDU`.
**What happened:** ~25% of parts overlapped. A flat plate standing on its edge actually needs
`ey ≈ 40 LDU`, not 5 — but the check used the fixed `r_v = 5` regardless of orientation.
**Avoid because:** Bounding volume must reflect actual orientation, not default rest position.
**Alternative:** Rotation-aware AABB: `ex = |R[0][0]|·a + |R[0][1]|·b + |R[0][2]|·c`.

---

## 2026-04-05 — Uniform Y distribution makes pile look "airy" (Pocket 4–5)
**What was tried:** `y = random.uniform(Y_MIN, Y_MAX)` — equal probability across full height.
**What happened:** Parts evenly spread through the full height, looking unrealistic.
**Avoid because:** Real parts settle under gravity — most near the bottom, few near the top.
**Alternative:** `random.triangular(Y_MIN, Y_MAX, Y_MIN + 50)` — peak near bottom, long tail upward.

---

## 2026-04-05 — Gaussian placement without size ordering causes central congestion (Pocket 4–5)
**What was tried:** Placing all parts in random order from the same Gaussian distribution.
**What happened:** Large plates (160 LDU footprint) often landed in the center first, occupying
30–40% of prime space. Subsequent large parts couldn't fit → ~25% forced placements in the center.
**Avoid because:** Large parts placed late find no room.
**Alternative:** Sort by footprint area descending before placement — large parts first, tiny parts last.

---

## 2026-04-05 — Two-layer system (floor plates + Gaussian pile) for flat piles (Pocket 9)
**What was tried:** Floor layer: 19 plates with uniform-in-ellipse XZ distribution, near-zero Y.
Pile layer: 46 parts with Gaussian XZ. (Pocket 9)
**What happened:** 9% forced — worse than single-strategy Gaussian P8 (6% forced).
**Avoid because:** Floor plates pre-fill the low-Y region. When pile parts are placed afterward,
they have less available Y space and more conflicts.
**Alternative:** Stick to single Gaussian distribution for all parts with reduced tilt_strength.

---

## 2026-04-05 — Poisson disk XZ sampling for floor plates (Pocket 10)
**What was tried:** Poisson disk sampling (min_dist between XZ centers) for floor plates to
prevent floor-floor collisions.
**What happened:** 15% forced at best — worse than Gaussian (8%).
**Avoid because:** Poisson disk is 2D (XZ only). AABB collision check is 3D. Two plates at similar
XZ but different Y heights still produce 3D AABB overlaps.
**Alternative:** Single Gaussian with reduced tilt_strength (P8 approach).

---

## 2026-04-05 — Increasing parts to 80 in flat Y_MAX=145 configuration (Pocket 10)
**What was tried:** 80 parts (vs 65) in Y_MAX=145 LDU flat pile.
**What happened:** 27–48% forced across all seeds.
**Avoid because:** 80 parts × average AABB volume > total pile volume. Physical impossibility
for rejection sampling regardless of parameters.
**Alternative:** Keep parts at 65 for flat piles. 80 parts requires Y_MAX ≥ 240 (tall pile).

---

## 2026-04-05 — Y_HERO_MAX=90 for 45 parts in 4-layer system (Pocket 11)
**What was tried:** Placing 45 hero parts in Y=[0,90] range.
**What happened:** 17–31% forced — very high. Volume is too compressed for 45 large parts.
**Avoid because:** With 45 parts in a thin Y band, fill ratio approaches 86% — physically impossible
with rejection sampling.
**Alternative:** Expand Y_HERO_MAX to 175. Doubling the Y range nearly eliminates forced overlap.

---

## 2026-04-05 — Fill plates at boundary of placement oval cause footprint overflow
**What was tried:** P11 — gap-fill plates placed using the full PLACEMENT_OVAL without a tighter constraint.
**What happened:** Fill plates generated at 21.8×16.4 studs — 19% wider than target.
**Avoid because:** Fill plates placed near oval boundary have AABB extending outside the oval.
**Alternative:** Use FILL_OVAL = 85% of placement oval + overflow check:
`if abs(px - CX) + ex > FILL_OVAL_A * 1.12: continue`

---

## 2026-04-05 — Coverage=1.0 (full AABB) reports false 100% coverage
**What was tried:** Using full rotation-aware AABB extents for XZ coverage grid marking.
**What happened:** Coverage reported as 100% after placing only a few tilted plates — no gaps detected
even when visual holes clearly existed.
**Avoid because:** AABB overstates visual footprint. A tilted part's AABB covers a much larger area
than it visually occupies from the top.
**Alternative:** Apply VIS_FACTOR=0.60–0.65 to AABB extents for coverage calculation.

---

## 2026-04-06 — Small size with GAP=2 produces visible overlaps in Stud.io (Pocket 13)
**What was tried:** P13 with P7 params (SIGMA 44×32, GAP=2) — 1/66 forced (2% algorithmic).
**What happened:** Visible overlaps in Stud.io rendering despite 98% algorithmic clean rate.
**Avoid because:** GAP=2 is 0.1 studs. Parts that don't overlap by 2 LDU still LOOK overlapping
in Stud.io's rendering. Visual threshold for "not overlapping" is around GAP=4.
**Alternative:** Use Medium size (SIGMA 58×46, GAP=4) — 0% forced, no visual artifacts.

---

## 2026-04-06 — Recipe 2 v1: discrete N_ANGLES=8 produces mechanical arrangement
**What was tried:** P12 v1 — sequential outward placement with only 8 angle choices (0°, 45°, etc.)
**What happened:** Parts aligned to the 8 allowed angles, creating a visually mechanical grid-like arrangement.
**Avoid because:** N_ANGLES=8 creates implicit axis-alignment bias. Looks like a regular grid, not a scattered pile.
**Alternative:** N_ANGLES=96 (3.75° steps). Reduces but doesn't fully eliminate bias (inherent in AABB geometry).

---

## 2026-04-06 — Recipe 2 v1: always-closest-to-center selection creates concentric rings
**What was tried:** P12 v1 — always pick the closest-to-center candidate from all positions.
**What happened:** Clear "crystal growth" pattern — each new ring of parts exactly one AABB-width
away from the previous ring. Looks like concentric shapes, not a scattered pile.
**Avoid because:** Greedy center-selection is deterministic and produces regular patterns.
**Alternative:** TOP_K=10 — pick randomly from top-10 center-closest positions.

---

## 2026-04-06 — Recipe 2 v2: GAP=-4 causes massive visible overlaps
**What was tried:** P12 v2 — negative GAP (-4 LDU) to achieve "nearly touching" effect.
**What happened:** Massive transparent overlaps visible in Stud.io from top view. For plates (ez=10),
GAP=-4 allows 40% overlap in each XZ direction — very visible.
**Avoid because:** "Nearly touching" look comes from varied angles and part density, not AABB overlap.
**Alternative:** GAP=0 + larger oval achieves the tight look without visible overlaps.

---

## 2026-04-06 — Recipe 2: 3D AABB collision prevents mixed-height piles
**What was tried:** P12 v2 — 3D AABB collision check including Y dimension.
**What happened:** A brick (ey=12) and plate (ey=2) beside each other in XZ would always "collide"
in the Y dimension: `abs(0-0) = 0 < 12+2 = 14`. Algorithm couldn't generate any mixed-height pile.
**Avoid because:** For top-layer piles with mixed brick and plate heights, Y overlap is expected and normal.
**Alternative:** XZ-only collision. Assign Y per-type as a decoration step after XZ placement.

---

## 2026-04-06 — Recipe 2: grid-based gap detection fails due to AABB overestimation
**What was tried:** P12-C modifier_fill_small_parts — grid coverage detection using rotation-aware AABB.
**What happened:** Only 98 gap cells found out of 1423 total oval cells. Zero valid filler positions found.
**Avoid because:** Tilted bricks (TILT_STR=0.40) have rotation-aware AABB up to 2× nominal size.
With 31 parts, their inflated AABBs cover the entire oval — no gaps detected.
**Alternative:** Monte Carlo placement with EXISTING_SCALE=0.65 on nominal dims.

---

## 2026-04-06 — Studio cannot open .io files via macOS `open` command
**What was tried:** `open -a "/Applications/Studio 2.0/Studio.app" file.io`
**What happened:** Studio shows "cannot open files in Stud.io Format" error dialog.
**Avoid because:** Studio does not register as a macOS file handler for `.io` files (Unity build omit).
**Alternative:** Use AppleScript-driven File → Open dialog:
Cmd+O → Cmd+Shift+G → type absolute path → Enter → Enter.

---

## 2026-04-06 — Backtick key (key code 50) for Studio perspective toggle doesn't work via AppleScript
**What was tried:** Sending `key code 50` via AppleScript to toggle Studio's perspective view mode.
**What happened:** Keystroke didn't register. Script hung waiting for view to change.
**Avoid because:** Studio may not handle this specific key via accessibility API. Also keyboard-layout
dependent (Russian keyboard layout may have different key codes).
**Alternative:** Capture Studio's DEFAULT view (already 3/4 perspective) as the first screenshot,
before switching to any orthographic projections.
