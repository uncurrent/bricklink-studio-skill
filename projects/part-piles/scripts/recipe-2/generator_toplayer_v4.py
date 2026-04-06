#!/usr/bin/env python3
"""
Pocket 12 — Top layer v4

Changes from v3:
1. GAP = 0 (no XZ overlaps — previous -6 caused visible plate collisions)
2. Larger oval OVAL_A=185, OVAL_B=145 to compensate for tighter packing
3. Bricks tilt_str = 0.40  → gauss(0,12°), occasionally 20-30° lean → looks thrown
4. Bricks Y spread: -30 to -4  (more height variation, some lean sideways)
5. Wider placement angle search (N_ANGLES=96) reduces 0/90 bias from AABB symmetry
6. Parts with smaller XZ footprint at their given angle are tried first (anti-axis-bias)
7. N_PARTS_MAX=50, best-of-60 seeds
"""
import math, sys, random as _random

# ── constants ──────────────────────────────────────────────────────────────────
CX, CZ   = -100, -130
OVAL_A   = 185
OVAL_B   = 145
GAP      = 0           # no overlaps
N_ANGLES = 96          # more touch-point candidates, reduces axis-aligned bias
N_PARTS_MAX = 50
N_SEEDS  = 60
TOP_K    = 10          # wider random pool → more organic layout

COLORS = [4, 1, 14, 25, 2, 6, 10, 3, 9, 11, 13, 12, 5, 15, 19, 72,
          28, 47, 18, 46]

# ── palette ───────────────────────────────────────────────────────────────────
# (part_file, (half_x, half_y, half_z), type)
PALETTE = [
    # Bricks (~30%) — tall, lean more
    ("3001.dat", (40, 12, 20), "brick"),  # 2×4
    ("3001.dat", (40, 12, 20), "brick"),
    ("3001.dat", (40, 12, 20), "brick"),
    ("3003.dat", (20, 12, 20), "brick"),  # 2×2
    ("3003.dat", (20, 12, 20), "brick"),
    ("3003.dat", (20, 12, 20), "brick"),
    ("3010.dat", (40, 12, 10), "brick"),  # 1×4
    ("3010.dat", (40, 12, 10), "brick"),
    ("3004.dat", (20, 12, 10), "brick"),  # 1×2
    ("3004.dat", (20, 12, 10), "brick"),
    ("3004.dat", (20, 12, 10), "brick"),
    ("3005.dat", (10, 12, 10), "brick"),  # 1×1
    ("3005.dat", (10, 12, 10), "brick"),
    ("3005.dat", (10, 12, 10), "brick"),

    # Plates (~50%) — flat
    ("3020.dat", (40, 2, 20), "plate"),   # 2×4
    ("3020.dat", (40, 2, 20), "plate"),
    ("3020.dat", (40, 2, 20), "plate"),
    ("3020.dat", (40, 2, 20), "plate"),
    ("3021.dat", (30, 2, 20), "plate"),   # 2×3
    ("3021.dat", (30, 2, 20), "plate"),
    ("3021.dat", (30, 2, 20), "plate"),
    ("3022.dat", (20, 2, 20), "plate"),   # 2×2
    ("3022.dat", (20, 2, 20), "plate"),
    ("3022.dat", (20, 2, 20), "plate"),
    ("3022.dat", (20, 2, 20), "plate"),
    ("3022.dat", (20, 2, 20), "plate"),
    ("3710.dat", (40, 2, 10), "plate"),   # 1×4
    ("3710.dat", (40, 2, 10), "plate"),
    ("3710.dat", (40, 2, 10), "plate"),
    ("3023.dat", (20, 2, 10), "plate"),   # 1×2
    ("3023.dat", (20, 2, 10), "plate"),
    ("3023.dat", (20, 2, 10), "plate"),
    ("3023.dat", (20, 2, 10), "plate"),
    ("3024.dat", (10, 2, 10), "plate"),   # 1×1
    ("3024.dat", (10, 2, 10), "plate"),
    ("3024.dat", (10, 2, 10), "plate"),

    # Tiles (~20%)
    ("3068b.dat", (20, 2, 20), "tile"),   # 2×2
    ("3068b.dat", (20, 2, 20), "tile"),
    ("3068b.dat", (20, 2, 20), "tile"),
    ("3069b.dat", (20, 2, 10), "tile"),   # 1×2
    ("3069b.dat", (20, 2, 10), "tile"),
    ("3069b.dat", (20, 2, 10), "tile"),
    ("3069b.dat", (20, 2, 10), "tile"),
    ("4073.dat",  (10, 2, 10), "tile"),   # 1×1 round
    ("4073.dat",  (10, 2, 10), "tile"),
    ("4073.dat",  (10, 2, 10), "tile"),
    ("3070b.dat", (10, 2, 10), "tile"),   # 1×1 tile
    ("3070b.dat", (10, 2, 10), "tile"),
    ("6636.dat",  (60, 2, 10), "tile"),   # 1×6 tile
    ("6636.dat",  (60, 2, 10), "tile"),
]

# ── Y assignment by type ───────────────────────────────────────────────────────
def assign_y(rng, ptype):
    if ptype == "brick":
        return rng.uniform(-30, -4)   # bricks stick up more
    elif ptype == "tile":
        return rng.uniform(-4, 6)
    else:
        return rng.uniform(-10, 10)   # plates spread naturally

# ── tilt strength per type ────────────────────────────────────────────────────
TILT = {"brick": 0.40, "plate": 0.07, "tile": 0.04}

# ── math ───────────────────────────────────────────────────────────────────────
def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def make_R(rng, ry_rad, tilt_str):
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
    a, b, c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ez

def r_str(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

def in_oval(x, z):
    return ((x-CX)/OVAL_A)**2 + ((z-CZ)/OVAL_B)**2 <= 1.0

def overlap_xz(p1, p2):
    x1,z1,ex1,ez1 = p1
    x2,z2,ex2,ez2 = p2
    return abs(x1-x2) < ex1+ex2+GAP and abs(z1-z2) < ez1+ez2+GAP

def touch_distance(rex, rez, ex, ez, ca, sa):
    aca, asa = abs(ca), abs(sa)
    if aca < 1e-9: return (rez + ez + GAP) / asa
    if asa < 1e-9: return (rex + ex + GAP) / aca
    return min((rex+ex+GAP)/aca, (rez+ez+GAP)/asa)

# ── generator ─────────────────────────────────────────────────────────────────
HEADER_TEMPLATE = """\
0 {title}
0 Name: {title}.ldr
0 Author: Brickit
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickControlPointUnitLength -1

"""

def generate(seed):
    rng = _random.Random(seed)

    parts = list(PALETTE[:N_PARTS_MAX])
    # Sort big→small footprint, shuffle within tiers
    parts.sort(key=lambda p: -(p[1][0] * p[1][2]))
    for i in range(len(parts)):
        j = i + rng.randint(0, min(4, len(parts)-i-1))
        parts[i], parts[j] = parts[j], parts[i]

    angles = [2 * math.pi * i / N_ANGLES for i in range(N_ANGLES)]

    placed_xz = []
    lines = []
    color_i = 0
    n_placed = 0

    for pid, dims, ptype in parts:
        color = COLORS[color_i % len(COLORS)]
        color_i += 1

        # Fully continuous random Y-rotation
        ry    = rng.uniform(0, 2 * math.pi)
        R     = make_R(rng, ry, TILT[ptype])
        ex,ez = extents_xz(dims, R)
        y     = assign_y(rng, ptype)

        if not placed_xz:
            x = CX + rng.gauss(0, 5)
            z = CZ + rng.gauss(0, 5)
            placed_xz.append((x, z, ex, ez))
            lines.append(f"1 {color} {x:.2f} {y:.2f} {z:.2f} {r_str(R)} {pid}")
            n_placed += 1
            continue

        candidates = []
        for ref in placed_xz:
            rx0,rz0,rex,rez = ref
            for angle in angles:
                ca, sa = math.cos(angle), math.sin(angle)
                d  = touch_distance(rex, rez, ex, ez, ca, sa)
                nx = rx0 + d * ca
                nz = rz0 + d * sa
                if not in_oval(nx, nz):
                    continue
                cxz = (nx, nz, ex, ez)
                if not any(overlap_xz(cxz, p) for p in placed_xz):
                    dist2 = (nx-CX)**2 + (nz-CZ)**2
                    candidates.append((dist2, nx, nz))

        if not candidates:
            continue

        candidates.sort(key=lambda c: c[0])
        k = min(TOP_K, len(candidates))
        # Weighted random from top-K: weight ∝ 1/(rank+1)
        weights = [1.0/(i+1) for i in range(k)]
        tw = sum(weights)
        r  = rng.uniform(0, tw)
        acc = 0.0; chosen = candidates[0]
        for i,w in enumerate(weights):
            acc += w
            if r <= acc:
                chosen = candidates[i]; break
        _, nx, nz = chosen

        placed_xz.append((nx, nz, ex, ez))
        lines.append(f"1 {color} {nx:.2f} {y:.2f} {nz:.2f} {r_str(R)} {pid}")
        n_placed += 1

    xs  = [p[0] for p in placed_xz]; exs = [p[2] for p in placed_xz]
    zs  = [p[1] for p in placed_xz]; ezs = [p[3] for p in placed_xz]
    fp_x = (max(x+e for x,e in zip(xs,exs)) - min(x-e for x,e in zip(xs,exs))) / 20
    fp_z = (max(z+e for z,e in zip(zs,ezs)) - min(z-e for z,e in zip(zs,ezs))) / 20
    return lines, n_placed, fp_x, fp_z

# ── run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Pocket 12 v4 — GAP=0, oval 185×145, bricks tilt 0.40", file=sys.stderr)

    best_lines, best_n, best_seed = None, 0, None

    for seed in range(42, 42 + N_SEEDS):
        lines, n, fpx, fpz = generate(seed)
        marker = " ◀" if n > best_n else ""
        print(f"seed={seed}: placed={n:2d}/50  footprint={fpx:.1f}×{fpz:.1f}{marker}",
              file=sys.stderr)
        if n > best_n:
            best_n, best_lines, best_seed = n, lines, seed

    print(f"\nBest seed={best_seed}: {best_n}/50 parts", file=sys.stderr)
    out = "/tmp/pocket12_toplayer_v4.ldr"
    with open(out, "w") as f:
        f.write(HEADER_TEMPLATE.format(title="Pocket 12 - Top Layer v4"))
        for line in best_lines:
            f.write(line + "\n")
    print(f"Written: {out}", file=sys.stderr)
