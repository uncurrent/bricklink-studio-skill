#!/usr/bin/env python3
"""
Pocket 12 — Top layer v3

Key changes from v2:
1. GAP = 4 (positive, no visual overlaps)
2. XZ-only collision detection → Y assigned per-type after placement
   - Bricks:  y = rng.uniform(-20, -6)  → stick up above the pile surface
   - Plates:  y = rng.uniform(-6,  6)   → relatively flat
   - Tiles:   y = rng.uniform(-4,  8)   → slightly above plates
3. Mixed palette: ~30% bricks, 70% plates/tiles for height variation
4. Tilt per type: bricks tilt more (feel thrown), plates almost flat
5. Keep fully continuous Y-rotation (no discrete snapping)
6. Randomized TOP_K candidate selection (anti-ring pattern)
"""
import math, sys, random as _random

# ── constants ──────────────────────────────────────────────────────────────────
CX, CZ   = -100, -130
OVAL_A   = 170
OVAL_B   = 132
GAP      = -6          # slight XZ overlap at edges (realistic for angled scattered parts)
N_ANGLES = 72
N_PARTS_MAX = 50
N_SEEDS  = 50
TOP_K    = 8           # pick randomly from top-K closest-to-center

COLORS = [4, 1, 14, 25, 2, 6, 10, 3, 9, 11, 13, 12, 5, 15, 19, 72,
          28, 47, 18, 46]

# ── palette ───────────────────────────────────────────────────────────────────
# Format: (part_file, (half_x_LDU, half_y_LDU, half_z_LDU), type)
# half_y for bricks = 12, for plates = 2, for tiles ≈ 1.5
# "type" controls Y placement: "brick", "plate", "tile"
PALETTE = [
    # ── Bricks (~30%) ─────────────────────────────────────────────────
    ("3001.dat", (40, 12, 20), "brick"),  # 2×4 Brick
    ("3001.dat", (40, 12, 20), "brick"),
    ("3001.dat", (40, 12, 20), "brick"),
    ("3003.dat", (20, 12, 20), "brick"),  # 2×2 Brick
    ("3003.dat", (20, 12, 20), "brick"),
    ("3003.dat", (20, 12, 20), "brick"),
    ("3010.dat", (40, 12, 10), "brick"),  # 1×4 Brick
    ("3010.dat", (40, 12, 10), "brick"),
    ("3004.dat", (20, 12, 10), "brick"),  # 1×2 Brick
    ("3004.dat", (20, 12, 10), "brick"),
    ("3004.dat", (20, 12, 10), "brick"),
    ("3005.dat", (10, 12, 10), "brick"),  # 1×1 Brick
    ("3005.dat", (10, 12, 10), "brick"),

    # ── Plates (~50%) ─────────────────────────────────────────────────
    ("3020.dat", (40, 2, 20), "plate"),   # 2×4 Plate
    ("3020.dat", (40, 2, 20), "plate"),
    ("3020.dat", (40, 2, 20), "plate"),
    ("3020.dat", (40, 2, 20), "plate"),
    ("3021.dat", (30, 2, 20), "plate"),   # 2×3 Plate
    ("3021.dat", (30, 2, 20), "plate"),
    ("3021.dat", (30, 2, 20), "plate"),
    ("3022.dat", (20, 2, 20), "plate"),   # 2×2 Plate
    ("3022.dat", (20, 2, 20), "plate"),
    ("3022.dat", (20, 2, 20), "plate"),
    ("3022.dat", (20, 2, 20), "plate"),
    ("3710.dat", (40, 2, 10), "plate"),   # 1×4 Plate
    ("3710.dat", (40, 2, 10), "plate"),
    ("3710.dat", (40, 2, 10), "plate"),
    ("3023.dat", (20, 2, 10), "plate"),   # 1×2 Plate
    ("3023.dat", (20, 2, 10), "plate"),
    ("3023.dat", (20, 2, 10), "plate"),
    ("3023.dat", (20, 2, 10), "plate"),
    ("3024.dat", (10, 2, 10), "plate"),   # 1×1 Plate
    ("3024.dat", (10, 2, 10), "plate"),
    ("3024.dat", (10, 2, 10), "plate"),
    ("3024.dat", (10, 2, 10), "plate"),

    # ── Tiles (~20%) ──────────────────────────────────────────────────
    ("3068b.dat", (20, 2, 20), "tile"),   # 2×2 Tile
    ("3068b.dat", (20, 2, 20), "tile"),
    ("3068b.dat", (20, 2, 20), "tile"),
    ("3069b.dat", (20, 2, 10), "tile"),   # 1×2 Tile
    ("3069b.dat", (20, 2, 10), "tile"),
    ("3069b.dat", (20, 2, 10), "tile"),
    ("3069b.dat", (20, 2, 10), "tile"),
    ("4073.dat",  (10, 2, 10), "tile"),   # 1×1 Round Tile
    ("4073.dat",  (10, 2, 10), "tile"),
    ("4073.dat",  (10, 2, 10), "tile"),
]

# ── Y assignment by type ───────────────────────────────────────────────────────
def assign_y(rng, part_type):
    """Assign Y center in LDraw coords.
    Y increases downward, so negative = higher up visually.
    Bricks stick up (-20 to -6), plates are flat (-6 to 6), tiles slightly above plates.
    """
    if part_type == "brick":
        return rng.uniform(-22, -8)   # bricks visually stick up
    elif part_type == "tile":
        return rng.uniform(-6, 4)     # tiles sit nearly flat
    else:  # plate
        return rng.uniform(-8, 8)     # plates spread across the surface

# ── tilt by type ──────────────────────────────────────────────────────────────
TILT_BY_TYPE = {"brick": 0.25, "plate": 0.06, "tile": 0.04}

# ── math ───────────────────────────────────────────────────────────────────────
def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def make_R(rng, ry_rad, tilt_str):
    """Random continuous Y-rotation + small tilt."""
    rx = math.radians(rng.gauss(0, tilt_str * 30))
    rz = math.radians(rng.gauss(0, tilt_str * 30))
    cy, sy = math.cos(ry_rad), math.sin(ry_rad)
    cx, sx = math.cos(rx),     math.sin(rx)
    cz, sz = math.cos(rz),     math.sin(rz)
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)

def extents_xz(dims, R):
    """XZ extents only (for XZ-based collision)."""
    a, b, c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ez

def r_str(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

def in_oval(x, z):
    return ((x-CX)/OVAL_A)**2 + ((z-CZ)/OVAL_B)**2 <= 1.0

# ── XZ-only collision ─────────────────────────────────────────────────────────
def overlap_xz(p1, p2):
    x1, z1, ex1, ez1 = p1
    x2, z2, ex2, ez2 = p2
    return abs(x1-x2) < ex1+ex2+GAP and abs(z1-z2) < ez1+ez2+GAP

# ── touch-point formula (XZ only) ─────────────────────────────────────────────
def touch_distance(rex, rez, ex, ez, ca, sa):
    aca, asa = abs(ca), abs(sa)
    if aca < 1e-9: return (rez + ez + GAP) / asa
    if asa < 1e-9: return (rex + ex + GAP) / aca
    dx = (rex + ex + GAP) / aca
    dz = (rez + ez + GAP) / asa
    return min(dx, dz)

# ── generator ─────────────────────────────────────────────────────────────────
HEADER = """\
0 Pocket 12 - Top Layer v3
0 Name: model.ldr
0 Author: Brickit
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickControlPointUnitLength -1

"""

def generate(seed):
    rng = _random.Random(seed)

    parts = list(PALETTE[:N_PARTS_MAX])
    # Sort big→small by footprint area so large parts fill first, small parts fill gaps
    # Then shuffle within same-size groups slightly
    parts.sort(key=lambda p: -(p[1][0] * p[1][2]))
    # Add small shuffle within each size tier to vary order across seeds
    for i in range(len(parts)):
        j = i + rng.randint(0, min(3, len(parts)-i-1))
        parts[i], parts[j] = parts[j], parts[i]

    placed_xz = []  # (x, z, ex, ez) — XZ only for collision
    lines = []
    color_i = 0
    n_placed = 0

    angles = [2 * math.pi * i / N_ANGLES for i in range(N_ANGLES)]

    for pid, dims, ptype in parts:
        color = COLORS[color_i % len(COLORS)]
        color_i += 1

        # Fully continuous random Y-rotation
        ry     = rng.uniform(0, 2 * math.pi)
        tilt   = TILT_BY_TYPE[ptype]
        R      = make_R(rng, ry, tilt)
        ex, ez = extents_xz(dims, R)
        y      = assign_y(rng, ptype)

        if not placed_xz:
            x = CX + rng.gauss(0, 4)
            z = CZ + rng.gauss(0, 4)
            placed_xz.append((x, z, ex, ez))
            lines.append(f"1 {color} {x:.2f} {y:.2f} {z:.2f} {r_str(R)} {pid}")
            n_placed += 1
            continue

        # Find all touching positions around all placed parts
        candidates = []
        for ref in placed_xz:
            rx0, rz0, rex, rez = ref
            for angle in angles:
                ca, sa = math.cos(angle), math.sin(angle)
                d = touch_distance(rex, rez, ex, ez, ca, sa)
                nx = rx0 + d * ca
                nz = rz0 + d * sa

                if not in_oval(nx, nz):
                    continue

                cand_xz = (nx, nz, ex, ez)
                if not any(overlap_xz(cand_xz, p) for p in placed_xz):
                    dist2 = (nx - CX)**2 + (nz - CZ)**2
                    candidates.append((dist2, nx, nz))

        if not candidates:
            print(f"  [{pid}] no XZ position, skipping", file=sys.stderr)
            continue

        candidates.sort(key=lambda c: c[0])
        k = min(TOP_K, len(candidates))
        pool = candidates[:k]
        # Weighted random: closer to center = higher weight
        weights = [1.0 / (i + 1) for i in range(k)]
        total_w = sum(weights)
        r = rng.uniform(0, total_w)
        acc = 0.0
        chosen = pool[0]
        for i, w in enumerate(weights):
            acc += w
            if r <= acc:
                chosen = pool[i]
                break
        _, nx, nz = chosen

        placed_xz.append((nx, nz, ex, ez))
        lines.append(f"1 {color} {nx:.2f} {y:.2f} {nz:.2f} {r_str(R)} {pid}")
        n_placed += 1

    # Footprint stats
    xs  = [p[0] for p in placed_xz]; exs = [p[2] for p in placed_xz]
    zs  = [p[1] for p in placed_xz]; ezs = [p[3] for p in placed_xz]
    fp_x = (max(x+e for x,e in zip(xs,exs)) - min(x-e for x,e in zip(xs,exs))) / 20
    fp_z = (max(z+e for z,e in zip(zs,ezs)) - min(z-e for z,e in zip(zs,ezs))) / 20

    return lines, n_placed, fp_x, fp_z

# ── run ────────────────────────────────────────────────────────────────────────
print("Pocket 12 v3 — mixed bricks/plates, XZ-only collision, Y by type", file=sys.stderr)

best_lines = None
best_n = 0
best_seed = None

for seed in range(42, 42 + N_SEEDS):
    lines, n, fpx, fpz = generate(seed)
    print(f"seed={seed}: placed={n:2d}/{N_PARTS_MAX}  footprint={fpx:.1f}×{fpz:.1f} studs",
          file=sys.stderr)
    if n > best_n:
        best_n = n
        best_lines = lines
        best_seed = seed

print(f"\nBest seed={best_seed}: {best_n}/{N_PARTS_MAX} parts", file=sys.stderr)

out = "/tmp/pocket12_toplayer_v3.ldr"
with open(out, "w") as f:
    f.write(HEADER)
    for line in best_lines:
        f.write(line + "\n")
print(f"Written: {out}", file=sys.stderr)
