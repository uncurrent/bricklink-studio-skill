# Session Log — Pockets 3–6 Development

## Overview

Two Claude sessions (2026-04-04 and 2026-04-05) developing a procedural generation pipeline for Brickit Pocket models. Starting point: Pocket 1 & 2 were hand-made in Stud.io. Goal: generate realistic-looking piles programmatically.

---

## Session 1 (2026-04-04) — Pockets 1–2, format discovery

**What happened:**
- Discovered that `.io` is a ZIP archive; `model.ldr` (LDraw) drives rendering, not `model.lxfml`
- Early attempts edited only LXFML → model didn't change
- Pocket 1 analyzed: 89 parts, colorful mix of common bricks + decorative accents
- Pocket 2 created by part-swapping Pocket 1's LDR in Python (positions kept identical)
- Stud.io auto-saves — Pocket 1 was partially modified via UI without warning

**Key learnings → SESSION_NOTES.md**

---

## Session 2 (2026-04-05) — Pockets 3–6, pile generation

### Pocket 3 — first generated model

**Goal:** Very different composition from Pockets 1/2, Technic-heavy, all white, no overlaps.

**Approach:** Manual part list (Technic liftarms, pins, axle connectors, beams), simple Gaussian XZ placement, Y-axis-only rotation, no collision detection. All parts recolored to LDraw color 15 (white).

**Result:** 26 parts, cleanly spread — but too sparse, all facing up. Pile looked like parts floating in air, not a heap.

**Packaged as:** `Pocket 3.io` (minimal ZIP: model.ldr + .info + errorPartList.err).

---

### Pocket 4 — first colorful pile

**Goal:** Dense pile matching Pocket 1/2 reference. Common bricks + plates as base, Technic as accent only (≤3 pcs). Measure "Small Size" and set as standard.

**Measured Small Size standard from Pocket 1:**
- 89 parts, footprint ~354×264 LDU (~17.7×13.2 studs), height ~208 LDU
- Center: X≈−100, Z≈−130

**Approach:** Gaussian XZ placement (σ≈55, 44), uniform Y [0–200], Y-axis-only rotation (no X/Z tilt). Random colors from a palette.

**Result:** 71 parts. Problem: all parts "face up" — zero X/Z tilt makes the pile look fake. Also ~20–25% parts semi-transparent (overlapping) because no collision detection.

---

### Pocket 5 — full 3D rotations + ellipsoid collision

**Goal:** Fix the "facing up" look and reduce overlaps.

**Changes:**
1. Full 3D rotation matrix (R = Ry × Rx × Rz) with per-category `tilt_strength`
2. Ellipsoidal bounding volume: each part assigned fixed `(r_horizontal, r_vertical)` radii
3. Rejection sampling: try 400 positions, fallback to position with fewest overlaps

**Result:** 71 parts, 23.4 studs × 13.8 studs. Tilts looked much more realistic. But still ~25% overlapping because the ellipsoid radii were fixed — a tilted plate still used `r_v = 5 LDU` instead of accounting for its actual orientation. The ey of a flat plate standing on its edge is ~40 LDU, not 5 LDU.

---

### Pocket 6 — rotation-aware AABB (current best)

**Goal:** Fix the root cause of Pocket 5's overlaps.

**Root cause:** Fixed bounding volumes ignore orientation. A plate lying flat has `ey ≈ 4 LDU`. Standing on edge: `ey ≈ 40 LDU`. The v2 ellipsoid always used `r_v = 5` regardless.

**Fix: rotation-aware AABB**

The axis-aligned bounding box of a rotated box with local half-dims `(a,b,c)` and rotation matrix `R`:
```
ex = |R[0][0]|·a + |R[0][1]|·b + |R[0][2]|·c
ey = |R[1][0]|·a + |R[1][1]|·b + |R[1][2]|·c
ez = |R[2][0]|·a + |R[2][1]|·b + |R[2][2]|·c
```
This correctly handles any rotation. Tilted plates now get their actual ey — no false "flat" assumption.

**Additional improvements over v2:**
- GAP = 4 LDU minimum clearance between AABBs
- Triangular Y distribution biased toward Y_MIN (parts settle naturally)
- Placement order: largest footprint first (big plates placed first find open space; small parts fill gaps)
- Multi-seed selection: run 20 seeds, pick the one with fewest forced placements

**Result (seed=43):** 61/66 clean, 5/66 forced = **8% overlap** (vs 25% in Pocket 5)
Footprint: 18.2 × 16.9 studs (reference: 17.7 × 13.2)

**Packaged as:** `Pocket 6.io` → `Pockets/Pocket 6/gen_pocket6.py` has the full script.

---

## Algorithm Evolution Summary

| Version | Pocket | Collision | Rotation | Forced % |
|---------|--------|-----------|----------|----------|
| v0 | 3 | None | Y-axis only | N/A (spread) |
| v1 | 4 | None | Y-axis only | ~25% |
| v2 | 5 | Fixed ellipsoid | Full 3D | ~25% |
| v3 | 6 | Rotation-aware AABB | Full 3D | **~8%** |

---

## Technical Pitfalls & Solutions

### EROFS when creating ZIP in workspace
**Problem:** `zip` command fails with "read-only file system" on mounted workspace dirs.
**Fix:** Create zip in `/tmp`, then `cp` to workspace.
```bash
cd /tmp && zip -r /tmp/PocketN.io model.ldr .info errorPartList.err
cp /tmp/PocketN.io "/path/to/Pockets/Pocket N.io"
```

### Script output appearing in LDR file
**Problem:** `print()` in Python script was being captured and mixed into LDR output.
**Fix:** Redirect stats to stderr (`print(..., file=sys.stderr)`), write LDR directly to file.

### skills/learning/ is read-only
**Problem:** `/sessions/.../skills/bricklink-studio/learning/` is mounted read-only.
**Status:** Cannot write skill observations there — document in project files instead.

### Stud.io auto-save
**Problem:** Stud.io saves UI changes (part replacements, color changes) immediately without prompt.
**Fix:** Always keep git history. Before manual editing: `git commit` the current state.

---

## Open Questions / Future Work

- Z footprint is still ~16.9 studs vs reference 13.2 — could tighten SIGMA_Z further
- Could try a layered placement strategy (explicit Y layers by part size) for more realistic settling
- Physics simulation in Blender would give truly collision-free results (see MODELING_BESTPRACTICES.md)
- 8% forced = ~5 parts still semi-transparent in Stud.io — acceptable for now, may want to get to <5%
