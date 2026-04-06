#!/usr/bin/env python3
"""
gen_pocket13.py — Brickit Pocket 13 generation script

Based on v3 algorithm (Pocket 6) with Pocket 7 parameter refinements:
  - Rotation-aware AABB rejection sampling
  - Multi-seed selection
  - Tighter XZ sigma, taller Y range, GAP=2, 1200 tries

Parameters: P7-tuned (0% forced target)
Seed range: 200–259 (fresh range, 60 seeds)
"""

import math, random, sys

# ── Part catalogue ─────────────────────────────────────────────────────────────
# (part_id, half-dims (a,b,c) in LDU, tilt_strength 0–1, category)
PARTS = [
    # Base bricks
    ("3001.dat", (40,12,20), 0.35, "brick"),   # 2×4
    ("3001.dat", (40,12,20), 0.35, "brick"),
    ("3001.dat", (40,12,20), 0.35, "brick"),
    ("3001.dat", (40,12,20), 0.35, "brick"),
    ("3001.dat", (40,12,20), 0.35, "brick"),
    ("3001.dat", (40,12,20), 0.35, "brick"),
    ("3003.dat", (20,12,20), 0.35, "brick"),   # 2×2
    ("3003.dat", (20,12,20), 0.35, "brick"),
    ("3003.dat", (20,12,20), 0.35, "brick"),
    ("3003.dat", (20,12,20), 0.35, "brick"),
    ("3003.dat", (20,12,20), 0.35, "brick"),
    ("3004.dat", (20,12,10), 0.40, "brick"),   # 1×2
    ("3004.dat", (20,12,10), 0.40, "brick"),
    ("3004.dat", (20,12,10), 0.40, "brick"),
    ("3004.dat", (20,12,10), 0.40, "brick"),
    ("3010.dat", (40,12,10), 0.40, "brick"),   # 1×4
    ("3010.dat", (40,12,10), 0.40, "brick"),
    ("3010.dat", (40,12,10), 0.40, "brick"),
    ("3005.dat", (10,12,10), 0.50, "brick"),   # 1×1
    ("3005.dat", (10,12,10), 0.50, "brick"),
    ("3005.dat", (10,12,10), 0.50, "brick"),
    # Base plates
    ("3023.dat", (20, 4,10), 0.25, "plate"),   # 1×2
    ("3023.dat", (20, 4,10), 0.25, "plate"),
    ("3023.dat", (20, 4,10), 0.25, "plate"),
    ("3023.dat", (20, 4,10), 0.25, "plate"),
    ("3022.dat", (20, 4,20), 0.25, "plate"),   # 2×2
    ("3022.dat", (20, 4,20), 0.25, "plate"),
    ("3022.dat", (20, 4,20), 0.25, "plate"),
    ("3020.dat", (40, 4,20), 0.22, "plate"),   # 2×4
    ("3020.dat", (40, 4,20), 0.22, "plate"),
    ("3020.dat", (40, 4,20), 0.22, "plate"),
    ("3020.dat", (40, 4,20), 0.22, "plate"),
    ("3710.dat", (40, 4,10), 0.22, "plate"),   # 1×4
    ("3710.dat", (40, 4,10), 0.22, "plate"),
    ("3710.dat", (40, 4,10), 0.22, "plate"),
    ("3034.dat", (80, 4,20), 0.18, "plate"),   # 2×8
    ("3034.dat", (80, 4,20), 0.18, "plate"),
    ("3795.dat", (60, 4,20), 0.18, "plate"),   # 2×6
    ("3795.dat", (60, 4,20), 0.18, "plate"),
    ("3021.dat", (30, 4,20), 0.22, "plate"),   # 2×3
    ("3021.dat", (30, 4,20), 0.22, "plate"),
    # Accent parts
    ("3039.dat",  (20,14,20), 0.55, "slope"),  # slope 45° 2×2
    ("3039.dat",  (20,14,20), 0.55, "slope"),
    ("3039.dat",  (20,14,20), 0.55, "slope"),
    ("3040b.dat", (20,14,10), 0.55, "slope"),  # slope 45° 1×2
    ("3040b.dat", (20,14,10), 0.55, "slope"),
    ("61678.dat", (40, 8,20), 0.50, "slope"),  # curved slope 1×4
    ("61678.dat", (40, 8,20), 0.50, "slope"),
    ("50950.dat", (30, 8,20), 0.50, "slope"),  # curved slope 1×3
    ("50950.dat", (30, 8,20), 0.50, "slope"),
    ("3062b.dat", (10,12,10), 0.65, "round"),  # round brick 1×1
    ("3062b.dat", (10,12,10), 0.65, "round"),
    ("3062b.dat", (10,12,10), 0.65, "round"),
    ("3062b.dat", (10,12,10), 0.65, "round"),
    ("14769.dat", (20, 3,20), 0.35, "tile"),   # round tile 2×2
    ("14769.dat", (20, 3,20), 0.35, "tile"),
    ("4073.dat",  (10, 3,10), 0.45, "tile"),   # round plate 1×1
    ("4073.dat",  (10, 3,10), 0.45, "tile"),
    ("4073.dat",  (10, 3,10), 0.45, "tile"),
    ("3069b.dat", (20, 3,10), 0.30, "tile"),   # tile 1×2
    ("3069b.dat", (20, 3,10), 0.30, "tile"),
    ("3068b.dat", (20, 3,20), 0.30, "tile"),   # tile 2×2
    ("3068b.dat", (20, 3,20), 0.30, "tile"),
    # Technic accents (max 3)
    ("32316.dat", (50,10,10), 0.60, "technic"), # liftarm 1×5
    ("43093.dat", ( 8,16, 8), 0.70, "technic"), # axle pin
    ("2780.dat",  ( 8,16, 8), 0.70, "technic"), # pin with friction
]

# Place largest footprint first
PARTS_SORTED = sorted(PARTS, key=lambda p: p[1][0]*p[1][2], reverse=True)

COLORS = [4, 1, 14, 2, 25, 5, 71, 10, 26, 7]  # red, blue, yellow, green, orange...

# ── Parameters (P7-tuned) ─────────────────────────────────────────────────────
CX, CZ = -100, -130
SIGMA_X, SIGMA_Z = 44, 32       # tighter than P6 (52, 42)
Y_MIN, Y_MAX = 0, 300           # taller range than P6 (240)
GAP = 2                         # tighter clearance than P6 (4)
MAX_TRIES = 1200                # more attempts than P6 (600)
N_SEEDS = 60                    # more seeds than P6 (20)
SEED_START = 200                # fresh seed range


def make_R(ts, rng):
    """Full 3D rotation matrix R = Ry × Rx × Rz. ts = tilt_strength (0–1)."""
    ry = math.radians(rng.uniform(-180, 180))
    r = rng.random()
    if r < 0.55:
        s = 10 + 35 * ts
        rx = math.radians(rng.gauss(0, s))
        rz = math.radians(rng.gauss(0, s))
    elif r < 0.80:
        lim = 35 + 70 * ts
        rx = math.radians(rng.uniform(-lim, lim))
        rz = math.radians(rng.uniform(-lim, lim))
    else:
        rx = math.radians(rng.uniform(-180, 180))
        rz = math.radians(rng.uniform(-180, 180))
    cy, sy = math.cos(ry), math.sin(ry)
    cx, sx = math.cos(rx), math.sin(rx)
    cz, sz = math.cos(rz), math.sin(rz)
    def mm(A, B):
        return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)


def compute_half_extents(dims, R):
    """Rotation-aware AABB half-extents."""
    a, b, c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ey = abs(R[1][0])*a + abs(R[1][1])*b + abs(R[1][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ey, ez


def overlaps(p1, p2):
    x1,y1,z1,ex1,ey1,ez1 = p1
    x2,y2,z2,ex2,ey2,ez2 = p2
    return (abs(x1-x2) < ex1+ex2+GAP and
            abs(y1-y2) < ey1+ey2+GAP and
            abs(z1-z2) < ez1+ez2+GAP)


def generate(seed):
    rng = random.Random(seed)
    placed = []
    parts_out = []
    n_clean = n_forced = 0

    for part_id, dims, ts, cat in PARTS_SORTED:
        R = make_R(ts, rng)
        ex, ey, ez = compute_half_extents(dims, R)
        color = rng.choice(COLORS)

        best_pos = None
        best_ovlp = 9999

        for _ in range(MAX_TRIES):
            x = rng.gauss(CX, SIGMA_X)
            z = rng.gauss(CZ, SIGMA_Z)
            y = rng.triangular(Y_MIN, Y_MAX, Y_MIN + 50)  # biased toward bottom
            pos = (x, y, z, ex, ey, ez)
            ovlp = sum(1 for p in placed if overlaps(pos, p))
            if ovlp == 0:
                best_pos = pos
                best_ovlp = 0
                n_clean += 1
                break
            elif ovlp < best_ovlp:
                best_ovlp = ovlp
                best_pos = pos

        if best_ovlp > 0:
            n_forced += 1

        placed.append(best_pos)
        parts_out.append((part_id, best_pos[0], best_pos[1], best_pos[2], R, color))

    return parts_out, n_clean, n_forced


def write_ldr(parts_out, path):
    header = (
        "0 Pocket 13\n"
        "0 Name: model.ldr\n"
        "0 Author: Brickit\n"
        "0 !LEGOCOM BrickLink Studio 2.0\n"
        "0 CustomBrick\n"
        "0 FlexibleBrickControlPointUnitLength -1\n"
        "0 FlexibleBrickLockedControlPoint\n"
        "0\n"
    )
    lines = [header]
    for part_id, x, y, z, R, color in parts_out:
        rm = " ".join(f"{v:.4f}" for row in R for v in row)
        lines.append(f"1 {color} {x:.1f} {y:.1f} {z:.1f} {rm} {part_id}\n")
    with open(path, "w") as f:
        f.writelines(lines)


# ── Multi-seed search ──────────────────────────────────────────────────────────
print("Pocket 13 — v3 algorithm (P7 params), searching seeds...", file=sys.stderr)
best_result = None
best_forced = 9999

for seed in range(SEED_START, SEED_START + N_SEEDS):
    parts_out, n_clean, n_forced = generate(seed)
    pct = n_forced / len(parts_out) * 100
    print(f"  seed={seed}: forced={n_forced}/{len(parts_out)} ({pct:.0f}%)", file=sys.stderr)
    if n_forced < best_forced:
        best_forced = n_forced
        best_result = (seed, parts_out, n_clean, n_forced)

seed, parts_out, n_clean, n_forced = best_result
n = len(parts_out)
print(f"\nBest seed={seed}: {n_clean}/{n} clean, {n_forced}/{n} forced ({n_forced/n*100:.0f}%)",
      file=sys.stderr)

xs = [p[1] for p in parts_out]
ys = [p[2] for p in parts_out]
zs = [p[3] for p in parts_out]
print(f"X: {min(xs):.0f}→{max(xs):.0f}  ({(max(xs)-min(xs))/20:.1f} studs, ref 17.7)",
      file=sys.stderr)
print(f"Y: {min(ys):.0f}→{max(ys):.0f}  ({(max(ys)-min(ys))/8:.0f} plates)",
      file=sys.stderr)
print(f"Z: {min(zs):.0f}→{max(zs):.0f}  ({(max(zs)-min(zs))/20:.1f} studs, ref 13.2)",
      file=sys.stderr)

out = "/tmp/pocket13_model.ldr"
write_ldr(parts_out, out)
print(f"Written: {out}  ({n} parts)", file=sys.stderr)
