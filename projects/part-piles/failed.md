# Part Piles — Failed Patterns & Anti-patterns

Documented from Pockets 3–6 development. Check before attempting anything unfamiliar.

---

## 2026-04-05 — Y-rotation only produces fake-looking pile (Pocket 4)
**What was tried:** Generating part orientations with rotation around Y axis only (`rot_y(angle)`)
**What happened:** All parts lie flat face-up — pile looks like parts laid out on a table for display, not scattered. Zero parts standing on edge or tilted.
**Avoid because:** Y is the vertical axis. Rotating around it only spins the part on its base — it never tilts.
**Alternative:** Full 3D rotation matrix (Ry × Rx × Rz) with per-category tilt_strength. See guide.md.

---

## 2026-04-05 — Fixed ellipsoid bounding volumes ignore orientation (Pocket 5)
**What was tried:** Assigning each part fixed `(r_horizontal, r_vertical)` radii for collision. Flat plate: `r_v = 5 LDU`. Brick: `r_v = 14 LDU`.
**What happened:** ~25% of parts overlapped. A flat plate standing on its edge actually needs `ey ≈ 40 LDU`, not 5 — but the check used the fixed `r_v = 5` regardless of orientation.
**Avoid because:** Bounding volume must reflect actual orientation, not default rest position.
**Alternative:** Rotation-aware AABB: `ex = |R[0][0]|·a + |R[0][1]|·b + |R[0][2]|·c`. Reduced overlap from 25% to 8%.

---

## 2026-04-05 — Uniform Y distribution makes pile look "airy" (Pocket 4–5)
**What was tried:** `y = random.uniform(Y_MIN, Y_MAX)` — equal probability across full height
**What happened:** Parts evenly spread through the full height. Pile looked railed and unrealistic, especially from the side — too few parts near the bottom.
**Avoid because:** Real parts settle under gravity — most near the bottom, few near the top.
**Alternative:** `random.triangular(Y_MIN, Y_MAX, Y_MIN + 40)` — peak near bottom, long tail upward.

---

## 2026-04-05 — Gaussian placement without size ordering causes central congestion (Pocket 4–5)
**What was tried:** Placing all parts in random order from the same Gaussian distribution.
**What happened:** Large plates (160 LDU footprint) often landed in the center first, occupying 30–40% of prime space. Subsequent large parts couldn't fit → ~25% forced placements concentrated in the center.
**Avoid because:** Large parts placed late find no room; small parts placed early wastefully block space that large parts need.
**Alternative:** Sort by footprint area descending before placement — large parts first, tiny parts last.

---

## 2026-04-04 — Editing model.lxfml has no effect on Stud.io rendering
**What was tried:** Modifying the XML in `model.lxfml` inside the .io ZIP.
**What happened:** Model in Stud.io viewport didn't change at all despite correct XML edits.
**Avoid because:** Stud.io renders from `model.ldr` (LDraw), not from LXFML. LXFML is secondary metadata.
**Alternative:** Always edit `model.ldr`. LXFML can be left unchanged or omitted for programmatically generated files.

---

## 2026-04-05 — Creating ZIP directly in workspace fails with EROFS (Pocket 3–5)
**What was tried:** Running `zip` shell command directly inside the mounted workspace directory.
**What happened:** `EROFS: read-only file system` error. ZIP not created.
**Avoid because:** Workspace dirs (mnt/) are writable via file tools (Write/Edit) but may be read-only for native shell commands like `zip`.
**Alternative:**
```bash
cd /tmp && zip -r /tmp/PocketN.io model.ldr .info errorPartList.err
cp /tmp/PocketN.io "/path/to/workspace/Pocket N.io"
```
Always build the ZIP in `/tmp`, then `cp` to workspace.

---

## 2026-04-05 — print() output contaminates LDR file content (Pocket 5)
**What was tried:** Using `print()` for debug stats while also writing LDR to stdout via `sys.stdout.write()`.
**What happened:** Debug lines like `// --- DONE: 71 parts ---` appeared inside the LDR file. Stud.io failed to parse it correctly.
**Avoid because:** In a subprocess, any `print()` goes to stdout and gets captured as file content.
**Alternative:** Redirect stats to stderr: `print(..., file=sys.stderr)`. Write LDR directly to a file: `open(path, 'w')`. Never mix diagnostic output and file data in the same stream.
