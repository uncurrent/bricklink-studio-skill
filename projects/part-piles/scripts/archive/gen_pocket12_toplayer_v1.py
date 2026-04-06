#!/usr/bin/env python3
"""
Pocket 12 — Top layer only (first iteration)

Algorithm: sequential outward from center (crystal growth)
- Place part 1 at center
- Each next part finds the position CLOSEST to center that:
    a) touches (is flush with) at least one already-placed part
    b) does not overlap any placed part
    c) stays within the oval boundary
- Result: naturally dense, gap-free packing from center out

Part composition: mostly flat plates & tiles (like P1 reference)
All parts nearly flat, Y ≈ 0, slight random tilt for natural look
"""
import math, sys, random as _random

# ── constants ──────────────────────────────────────────────────────────────────
CX, CZ      = -100, -130
OVAL_A      = 162       # tighter oval for top layer (≈ 16.2 studs)
OVAL_B      = 125
GAP         = 2         # LDU clearance between touching parts
Y_BASE      = 0         # Y position of top layer (LDU, downward = positive)
Y_JITTER    = 6         # ±jitter for natural settling look
TILT_STR    = 0.07      # very flat, slight wobble
N_ANGLES    = 48        # angular resolution for touch-point search
N_PARTS_MAX = 32        # stop after this many parts
N_SEEDS     = 30

COLORS = [4, 1, 14, 25, 2, 6, 10, 3, 9, 11, 13, 12, 5, 15, 19, 72,
          28, 47, 18, 46]

# ── top-layer part palette (flat plates & tiles, like P1) ─────────────────────
# (part_id, half_dims (a,b,c))
# Sorted largest→smallest for natural look (big parts toward center)
PALETTE = [
    ("3020.dat",  (40, 4, 20)),   # Plate 2×4
    ("3020.dat",  (40, 4, 20)),
    ("3020.dat",  (40, 4, 20)),
    ("3021.dat",  (30, 4, 20)),   # Plate 2×3
    ("3021.dat",  (30, 4, 20)),
    ("3022.dat",  (20, 4, 20)),   # Plate 2×2
    ("3022.dat",  (20, 4, 20)),
    ("3022.dat",  (20, 4, 20)),
    ("3022.dat",  (20, 4, 20)),
    ("3022.dat",  (20, 4, 20)),
    ("3068b.dat", (20, 3, 20)),   # Tile 2×2
    ("3068b.dat", (20, 3, 20)),
    ("3068b.dat", (20, 3, 20)),
    ("3710.dat",  (40, 4, 10)),   # Plate 1×4
    ("3710.dat",  (40, 4, 10)),
    ("3023.dat",  (20, 4, 10)),   # Plate 1×2
    ("3023.dat",  (20, 4, 10)),
    ("3023.dat",  (20, 4, 10)),
    ("3023.dat",  (20, 4, 10)),
    ("3069b.dat", (20, 3, 10)),   # Tile 1×2
    ("3069b.dat", (20, 3, 10)),
    ("3069b.dat", (20, 3, 10)),
    ("3024.dat",  (10, 4, 10)),   # Plate 1×1
    ("3024.dat",  (10, 4, 10)),
    ("3024.dat",  (10, 4, 10)),
    ("4073.dat",  (10, 3, 10)),   # Plate 1×1 Round
    ("4073.dat",  (10, 3, 10)),
    ("3005.dat",  (10,12, 10)),   # Brick 1×1 (accent)
    ("3005.dat",  (10,12, 10)),
    ("3062b.dat", (10,12, 10)),   # Brick 1×1 Round (accent)
    ("3062b.dat", (10,12, 10)),
    ("3039.dat",  (20,14, 20)),   # Slope 2×2 (accent)
]

# ── math ───────────────────────────────────────────────────────────────────────
def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def make_R_flat(rng, ry_rad):
    """Nearly flat: fixed Y-rotation, tiny X/Z wobble."""
    rx = math.radians(rng.gauss(0, TILT_STR * 30))
    rz = math.radians(rng.gauss(0, TILT_STR * 30))
    cy, sy = math.cos(ry_rad), math.sin(ry_rad)
    cx, sx = math.cos(rx),     math.sin(rx)
    cz, sz = math.cos(rz),     math.sin(rz)
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)

def extents(dims, R):
    a, b, c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ey = abs(R[1][0])*a + abs(R[1][1])*b + abs(R[1][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ey, ez

def overlap_3d(p1, p2):
    x1,y1,z1,ex1,ey1,ez1 = p1
    x2,y2,z2,ex2,ey2,ez2 = p2
    return (abs(x1-x2) < ex1+ex2+GAP and
            abs(y1-y2) < ey1+ey2+GAP and
            abs(z1-z2) < ez1+ez2+GAP)

def in_oval(x, z):
    return ((x-CX)/OVAL_A)**2 + ((z-CZ)/OVAL_B)**2 <= 1.0

def r_str(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

# ── touch-point formula ────────────────────────────────────────────────────────
def touch_distance(ref_ex, ref_ez, new_ex, new_ez, ca, sa):
    """
    Distance to move new part center from ref part center (in direction ca,sa)
    so that new part AABB just touches (not overlaps) ref part AABB.

    d = min( (ref_ex+new_ex+GAP)/|ca|,  (ref_ez+new_ez+GAP)/|sa| )

    This is the MINIMUM d where at least one AABB axis is separated.
    """
    aca, asa = abs(ca), abs(sa)
    if aca < 1e-9:
        return (ref_ez + new_ez + GAP) / asa
    if asa < 1e-9:
        return (ref_ex + new_ex + GAP) / aca
    dx = (ref_ex + new_ex + GAP) / aca
    dz = (ref_ez + new_ez + GAP) / asa
    return min(dx, dz)

# ── sequential outward placement ───────────────────────────────────────────────
HEADER = """\
0 Pocket 12 - Top Layer
0 Name: model.ldr
0 Author: Brickit
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickControlPointUnitLength -1

"""

def generate(seed):
    rng = _random.Random(seed)

    # Shuffle palette (but keep large-ish parts toward front of list)
    parts = list(PALETTE[:N_PARTS_MAX])
    # Keep the first few big plates at front, shuffle the rest
    rng.shuffle(parts[3:])

    placed  = []   # (x, y, z, ex, ey, ez)  for collision
    lines   = []   # LDR output lines
    color_i = 0
    n_placed = 0

    angles = [2 * math.pi * i / N_ANGLES for i in range(N_ANGLES)]

    for pid, dims in parts:
        color = COLORS[color_i % len(COLORS)]
        color_i += 1

        # Choose a random near-flat rotation (0/90/45/135 degrees in Y + tiny wobble)
        ry_choices = [0, math.pi/2, math.pi, 3*math.pi/2, math.pi/4, -math.pi/4,
                      3*math.pi/4, -3*math.pi/4]
        ry = rng.choice(ry_choices)
        R  = make_R_flat(rng, ry)
        ex, ey, ez = extents(dims, R)

        if not placed:
            # First part: place at center with tiny jitter
            x = CX + rng.gauss(0, 5)
            z = CZ + rng.gauss(0, 5)
            y = Y_BASE + rng.uniform(-Y_JITTER, Y_JITTER)
            cand = (x, y, z, ex, ey, ez)
            placed.append(cand)
            lines.append(f"1 {color} {x:.2f} {y:.2f} {z:.2f} {r_str(R)} {pid}")
            n_placed += 1
            continue

        # Find the touch-point closest to center across all placed parts × all angles
        candidates = []  # (dist_from_center, x, z, y, R)

        for ref in placed:
            rx, ry_ref, rz, rex, rey, rez = ref

            for angle in angles:
                ca, sa = math.cos(angle), math.sin(angle)
                d = touch_distance(rex, rez, ex, ez, ca, sa)

                nx = rx + d * ca
                nz = rz + d * sa

                if not in_oval(nx, nz):
                    continue

                ny = Y_BASE + rng.uniform(-Y_JITTER, Y_JITTER)
                cand = (nx, ny, nz, ex, ey, ez)

                if not any(overlap_3d(cand, p) for p in placed):
                    dist2 = (nx - CX)**2 + (nz - CZ)**2
                    candidates.append((dist2, nx, ny, nz))

        if not candidates:
            # Part doesn't fit — skip
            print(f"  [{pid}] no position found, skipping", file=sys.stderr)
            continue

        # Pick the position closest to center
        candidates.sort(key=lambda c: c[0])
        _, nx, ny, nz = candidates[0]

        cand = (nx, ny, nz, ex, ey, ez)
        placed.append(cand)
        lines.append(f"1 {color} {nx:.2f} {ny:.2f} {nz:.2f} {r_str(R)} {pid}")
        n_placed += 1

    # Stats
    xs  = [p[0] for p in placed]; exs = [p[3] for p in placed]
    zs  = [p[2] for p in placed]; ezs = [p[5] for p in placed]
    fp_x = (max(x+e for x,e in zip(xs,exs)) - min(x-e for x,e in zip(xs,exs))) / 20
    fp_z = (max(z+e for z,e in zip(zs,ezs)) - min(z-e for z,e in zip(zs,ezs))) / 20

    return lines, n_placed, fp_x, fp_z

# ── run ────────────────────────────────────────────────────────────────────────
print("Running sequential outward placement...", file=sys.stderr)

best_lines = None
best_n = 0
best_seed = None

for seed in range(42, 42 + N_SEEDS):
    lines, n, fpx, fpz = generate(seed)
    print(f"seed={seed}: placed={n:2d}  footprint={fpx:.1f}×{fpz:.1f} studs", file=sys.stderr)
    if n > best_n:
        best_n = n
        best_lines = lines
        best_seed = seed

print(f"\nBest seed={best_seed}: {best_n} parts placed", file=sys.stderr)

out = "/tmp/pocket12_toplayer.ldr"
with open(out, "w") as f:
    f.write(HEADER)
    for line in best_lines:
        f.write(line + "\n")
print(f"Written: {out}", file=sys.stderr)
