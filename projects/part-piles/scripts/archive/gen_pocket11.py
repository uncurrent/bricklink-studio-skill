#!/usr/bin/env python3
"""
Pocket 11 — 4-layer coverage system
  Layer 1+2: Hero bricks + accents  (Gaussian XZ, Y=[0..175], moderate tilt)
  Layer 3:   Gap-fill plates        (coverage-based, Y=[190..240], near-flat)
  Layer 4:   Tiny fill              (coverage-based, remaining gaps)

Key insight:
  - Heroes at Y=[0,175] get full volume room → low forced placements
  - Gap-fill at Y=[190,240] is physically BELOW the pile → almost no collisions with heroes
  - Coverage grid uses FLAT-only footprint (ex/ez with ey ignored) for visual gap detection
"""
import math, sys, random as _random

# ── constants ──────────────────────────────────────────────────────────────────
CX, CZ      = -100, -130
OVAL_A      = 190       # Hero placement oval (wider, natural scatter)
OVAL_B      = 140
FILL_OVAL_A = 162       # Coverage oval for gap-fill (tighter = no plate overhang)
FILL_OVAL_B = 125
SIGMA_X     = 48
SIGMA_Z     = 33
Y_HERO_MAX  = 175       # Heroes: ~21.9 plates of volume
Y_FILL_MIN  = 182       # Gap-fill: near floor
Y_FILL_MAX  = 210       # Cap height ≈ reference 208 LDU
GAP         = 2         # LDU clearance between AABBs
GRID_RES    = 12        # LDU per coverage cell (~0.6 studs; coarser = truer visual)
MAX_TRIES   = 450       # Per-part placement attempts (hero layer)
MAX_FILL    = 22        # Max gap-fill plates (layer 3)
MAX_TINY    = 12        # Max tiny fill parts (layer 4)
N_SEEDS     = 80

COLORS = [4, 1, 14, 25, 2, 6, 10, 3, 9, 11, 13, 12, 5, 15, 19, 72,
          28, 47, 18, 46, 7, 8, 20, 21, 26, 120, 216, 272]

# ── part lists ─────────────────────────────────────────────────────────────────
# (part_id, half_dims(a,b,c), tilt_strength, count)
LAYER12_DEFS = [
    # ── Heroes: bricks (moderate tilt, good visual interest) ──────────────────
    ("3001.dat",  (40,12,20), 0.40, 8),   # Brick 2×4
    ("3002.dat",  (30,12,20), 0.40, 3),   # Brick 2×3
    ("3003.dat",  (20,12,20), 0.40, 6),   # Brick 2×2
    ("3010.dat",  (40,12,10), 0.40, 3),   # Brick 1×4
    ("3004.dat",  (20,12,10), 0.40, 5),   # Brick 1×2
    ("3005.dat",  (10,12,10), 0.55, 3),   # Brick 1×1
    ("3039.dat",  (20,14,20), 0.50, 4),   # Slope 45° 2×2
    ("3040b.dat", (20,14,10), 0.50, 5),   # Slope 45° 2×1
    # ── Accents: flatter, more varied ─────────────────────────────────────────
    ("3062b.dat", (10,12,10), 0.55, 3),   # Round brick 1×1
    ("14769.dat", (20, 3,20), 0.45, 2),   # Round tile 2×2 (nearly flat)
    ("3069b.dat", (20, 3,10), 0.45, 3),   # Tile 1×2
]
# Total layer 1+2: 8+3+6+3+5+3+4+5+3+2+3 = 45 parts

# Gap-fill candidates, tried largest→smallest for each gap
GAP_FILL_DEFS = [
    ("3034.dat", (80, 4,20)),   # Plate 2×8
    ("3795.dat", (60, 4,20)),   # Plate 2×6
    ("3020.dat", (40, 4,20)),   # Plate 2×4
    ("3021.dat", (30, 4,20)),   # Plate 2×3
    ("3022.dat", (20, 4,20)),   # Plate 2×2
    ("3710.dat", (40, 4,10)),   # Plate 1×4
    ("3023.dat", (20, 4,10)),   # Plate 1×2
]

TINY_DEFS = [
    ("3024.dat", (10, 4,10)),   # Plate 1×1
    ("4073.dat", (10, 3,10)),   # Plate 1×1 Round
    ("3023.dat", (20, 4,10)),   # Plate 1×2  (fallback if 1×1 won't fit)
]

# ── math ───────────────────────────────────────────────────────────────────────
def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

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
    cy,sy = math.cos(ry),math.sin(ry)
    cx,sx = math.cos(rx),math.sin(rx)
    cz,sz = math.cos(rz),math.sin(rz)
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)

def make_R_flat(rng, ry_rad):
    """Near-flat: fixed Y-angle, tiny X/Z wobble only."""
    rx = math.radians(rng.gauss(0, 2.5))
    rz = math.radians(rng.gauss(0, 2.5))
    cy,sy = math.cos(ry_rad),math.sin(ry_rad)
    cx,sx = math.cos(rx),math.sin(rx)
    cz,sz = math.cos(rz),math.sin(rz)
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)

def extents(dims, R):
    a,b,c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ey = abs(R[1][0])*a + abs(R[1][1])*b + abs(R[1][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ey, ez

def overlap(p1, p2):
    x1,y1,z1,ex1,ey1,ez1 = p1
    x2,y2,z2,ex2,ey2,ez2 = p2
    return (abs(x1-x2) < ex1+ex2+GAP and
            abs(y1-y2) < ey1+ey2+GAP and
            abs(z1-z2) < ez1+ez2+GAP)

def r_flat(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

# ── coverage grid ──────────────────────────────────────────────────────────────
def part_cells_xz(x, z, ex, ez):
    """Cells covered by XZ footprint of a part (for visual coverage)."""
    x0 = int(math.floor((x - ex) / GRID_RES))
    x1 = int(math.floor((x + ex) / GRID_RES))
    z0 = int(math.floor((z - ez) / GRID_RES))
    z1 = int(math.floor((z + ez) / GRID_RES))
    return {(gx, gz) for gx in range(x0, x1+1) for gz in range(z0, z1+1)}

def flat_footprint(dims, ry_only=True):
    """XZ extents of a part lying flat (no tilt) — pure visual footprint.
    For hero coverage, use dims directly (ey ignored, tilt causes conservative overcount).
    For gap-fill, use this to compute exact flat plate footprint.
    """
    a, b, c = dims
    # For a flat plate with ry rotation only, ex=a, ez=c (ry doesn't change ex/ez for axis-aligned)
    return a, c

def oval_cells(cx, cz, a, b):
    cells = set()
    gx0 = int(math.floor((cx - a) / GRID_RES)) - 1
    gx1 = int(math.floor((cx + a) / GRID_RES)) + 1
    gz0 = int(math.floor((cz - b) / GRID_RES)) - 1
    gz1 = int(math.floor((cz + b) / GRID_RES)) + 1
    for gx in range(gx0, gx1+1):
        for gz in range(gz0, gz1+1):
            px = gx * GRID_RES + GRID_RES / 2.0
            pz = gz * GRID_RES + GRID_RES / 2.0
            if ((px-cx)/a)**2 + ((pz-cz)/b)**2 <= 1.0:
                cells.add((gx, gz))
    return cells

# ── LDR ────────────────────────────────────────────────────────────────────────
HEADER = """\
0 Pocket 11
0 Name: model.ldr
0 Author: Brickit
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickControlPointUnitLength -1

"""

def ldr_line(color, x, y, z, R, pid):
    return f"1 {color} {x:.2f} {y:.2f} {z:.2f} {r_flat(R)} {pid}"

# ── generator ──────────────────────────────────────────────────────────────────
def generate(seed):
    rng = _random.Random(seed)

    # Expand + sort largest footprint first
    layer12 = []
    for pid, dims, ts, count in LAYER12_DEFS:
        for _ in range(count):
            layer12.append((pid, dims, ts))
    layer12.sort(key=lambda x: x[1][0]*x[1][2], reverse=True)

    placed = []     # (x,y,z,ex,ey,ez)
    lines  = []
    n_forced = 0
    color_idx = 0

    # ── Layers 1+2: Heroes + Accents ──────────────────────────────────────────
    for pid, dims, ts in layer12:
        color = COLORS[color_idx % len(COLORS)]
        color_idx += 1
        placed_ok = False

        for _ in range(MAX_TRIES):
            x = rng.gauss(CX, SIGMA_X)
            z = rng.gauss(CZ, SIGMA_Z)
            if ((x-CX)/OVAL_A)**2 + ((z-CZ)/OVAL_B)**2 > 1.0:
                continue
            y = rng.triangular(0, Y_HERO_MAX, 12)
            R = make_R(ts, rng)
            ex, ey, ez = extents(dims, R)
            cand = (x, y, z, ex, ey, ez)
            if not any(overlap(cand, p) for p in placed):
                placed.append(cand)
                lines.append(ldr_line(color, x, y, z, R, pid))
                placed_ok = True
                break

        if not placed_ok:
            n_forced += 1
            best_cand = None
            best_hits = 999
            best_R = None
            for _ in range(100):
                x = rng.gauss(CX, SIGMA_X * 0.6)
                z = rng.gauss(CZ, SIGMA_Z * 0.6)
                y = rng.triangular(0, Y_HERO_MAX, 12)
                R = make_R(ts, rng)
                ex, ey, ez = extents(dims, R)
                cand = (x, y, z, ex, ey, ez)
                hits = sum(1 for p in placed if overlap(cand, p))
                if hits < best_hits:
                    best_hits = hits
                    best_cand = cand
                    best_R = R
            if best_cand:
                placed.append(best_cand)
                x,y,z,ex,ey,ez = best_cand
                lines.append(ldr_line(color, x, y, z, best_R, pid))

    # ── Visual coverage from layers 1+2 ───────────────────────────────────────
    # Use only HORIZONTAL projection (ex, ez at full tilt) for real XZ footprint.
    # This is more conservative: tilted parts cover less visually than their full AABB.
    # We use half of the rotation-aware ex/ez as a rough visual footprint estimate.
    covered = set()
    for i, (x, y, z, ex, ey, ez) in enumerate(placed):
        # Halve ex/ez to approximate visible top-down footprint of tilted parts
        vis_ex = ex * 0.65
        vis_ez = ez * 0.65
        covered |= part_cells_xz(x, z, vis_ex, vis_ez)

    all_oval = oval_cells(CX, CZ, FILL_OVAL_A, FILL_OVAL_B)

    def dist2(cell):
        px = cell[0] * GRID_RES + GRID_RES / 2.0
        pz = cell[1] * GRID_RES + GRID_RES / 2.0
        return (px-CX)**2 + (pz-CZ)**2

    gaps_before_fill = len(all_oval - covered)

    # ── Layer 3: Gap-fill plates ───────────────────────────────────────────────
    RY_ANGLES = [0, math.pi/2, math.pi/4, -math.pi/4, math.pi/8, -math.pi/8,
                 3*math.pi/8, -3*math.pi/8]
    n_fill = 0
    gaps = sorted(all_oval - covered, key=dist2)

    for gx, gz in gaps:
        if n_fill >= MAX_FILL:
            break
        if (gx, gz) in covered:
            continue
        px = gx * GRID_RES + GRID_RES / 2.0
        pz = gz * GRID_RES + GRID_RES / 2.0

        placed_fill = False
        for plate_id, dims in GAP_FILL_DEFS:
            for ry_rad in RY_ANGLES:
                # Pre-check: skip if plate would overflow coverage oval too much
                # Compute AABB ex/ez for this rotation (flat plate, use dims directly)
                _ex_pre = abs(math.cos(ry_rad))*dims[0] + abs(math.sin(ry_rad))*dims[2]
                _ez_pre = abs(math.sin(ry_rad))*dims[0] + abs(math.cos(ry_rad))*dims[2]
                if abs(px - CX) + _ex_pre > FILL_OVAL_A * 1.12:
                    continue
                if abs(pz - CZ) + _ez_pre > FILL_OVAL_B * 1.12:
                    continue

                # Try multiple Y positions to avoid rare deep-tilt hero conflicts
                for _ytry in range(6):
                    y = rng.uniform(Y_FILL_MIN, Y_FILL_MAX)
                    R = make_R_flat(rng, ry_rad)
                    ex, ey, ez = extents(dims, R)
                    cand = (px, y, pz, ex, ey, ez)
                    if not any(overlap(cand, p) for p in placed):
                        color = COLORS[color_idx % len(COLORS)]
                        color_idx += 1
                        placed.append(cand)
                        lines.append(ldr_line(color, px, y, pz, R, plate_id))
                        # Visual coverage: flat plate uses full ex/ez
                        covered |= part_cells_xz(px, pz, ex, ez)
                        n_fill += 1
                        placed_fill = True
                        break
                if placed_fill:
                    break
            if placed_fill:
                break

    # ── Layer 4: Tiny fill ─────────────────────────────────────────────────────
    n_tiny = 0
    gaps2 = sorted(all_oval - covered, key=dist2)

    for gx, gz in gaps2:
        if n_tiny >= MAX_TINY:
            break
        if (gx, gz) in covered:
            continue
        px = gx * GRID_RES + GRID_RES / 2.0
        pz = gz * GRID_RES + GRID_RES / 2.0

        for tiny_id, dims in TINY_DEFS:
            for ry_rad in [0, math.pi/2, math.pi/4]:
                for _ytry in range(4):
                    y = rng.uniform(Y_FILL_MIN - 15, Y_FILL_MAX)
                    R = make_R_flat(rng, ry_rad)
                    ex, ey, ez = extents(dims, R)
                    cand = (px, y, pz, ex, ey, ez)
                    if not any(overlap(cand, p) for p in placed):
                        color = COLORS[color_idx % len(COLORS)]
                        color_idx += 1
                        placed.append(cand)
                        lines.append(ldr_line(color, px, y, pz, R, tiny_id))
                        covered |= part_cells_xz(px, pz, ex, ez)
                        n_tiny += 1
                        placed_fill = True
                        break
                if placed_fill:
                    break
                placed_fill = False
            else:
                continue
            break

    total_oval = len(all_oval)
    final_cov  = len(covered & all_oval)
    cov_pct    = 100.0 * final_cov / max(total_oval, 1)
    total      = len(lines)

    return lines, n_forced, n_fill, n_tiny, total, cov_pct, gaps_before_fill, placed

# ── multi-seed search ──────────────────────────────────────────────────────────
best_result = None
best_forced = float('inf')
best_seed   = None

for seed in range(42, 42 + N_SEEDS):
    lines, n_forced, n_fill, n_tiny, total, cov_pct, gaps_pre, placed = generate(seed)
    print(f"seed={seed:3d}: forced={n_forced:2d} fill={n_fill:2d} tiny={n_tiny:2d} "
          f"total={total:2d} gaps_pre={gaps_pre:3d} cov_final={cov_pct:.0f}%", file=sys.stderr)
    if n_forced < best_forced:
        best_forced = n_forced
        best_result = (lines, n_forced, n_fill, n_tiny, total, cov_pct, gaps_pre, placed)
        best_seed   = seed

lines, n_forced, n_fill, n_tiny, total, cov_pct, gaps_pre, placed = best_result

print(f"\nBest seed={best_seed}: total={total} forced={n_forced} "
      f"fill={n_fill} tiny={n_tiny} cov={cov_pct:.0f}%", file=sys.stderr)

xs  = [p[0] for p in placed]; exs = [p[3] for p in placed]
zs  = [p[2] for p in placed]; ezs = [p[5] for p in placed]
ys  = [p[1] for p in placed]; eys = [p[4] for p in placed]
fp_x = (max(x+e for x,e in zip(xs,exs)) - min(x-e for x,e in zip(xs,exs))) / 20
fp_z = (max(z+e for z,e in zip(zs,ezs)) - min(z-e for z,e in zip(zs,ezs))) / 20
fp_y = (max(y+e for y,e in zip(ys,eys)) - min(y-e for y,e in zip(ys,eys)))
print(f"  footprint: {fp_x:.1f}×{fp_z:.1f} studs  height: {fp_y:.0f} LDU ≈{fp_y/8:.1f} plates",
      file=sys.stderr)
print(f"  (ref: 17.7×13.2 studs, ~26 plates)", file=sys.stderr)

out = "/tmp/pocket11_model.ldr"
with open(out, "w") as f:
    f.write(HEADER)
    for line in lines:
        f.write(line + "\n")
print(f"Written: {out}  ({total} parts)", file=sys.stderr)
