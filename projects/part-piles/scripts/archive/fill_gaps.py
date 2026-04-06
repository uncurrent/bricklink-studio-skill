#!/usr/bin/env python3
"""
fill_gaps.py — Gap-fill post-processor for Brickit Pockets

Takes an existing pocket .ldr file, analyzes XZ coverage from top-down view,
and adds small parts to fill visual gaps. Outputs a new .ldr file.

Small fill parts: 1×1/1×2 plates, tiles, bricks, round plates/bricks,
plus 1–2 gears and 1 pin for visual interest.

Usage:
    python3 fill_gaps.py <input.ldr> <output.ldr> [--seed N]
"""

import math, sys, random as _random, re

# ── Fill part palette ─────────────────────────────────────────────────────────
# (part_id, half_dims (a,b,c), description)
FILL_PLATES = [
    ("3023.dat",  (20, 4, 10), "Plate 1×2"),
    ("3023.dat",  (20, 4, 10), "Plate 1×2"),
    ("3023.dat",  (20, 4, 10), "Plate 1×2"),
    ("3023.dat",  (20, 4, 10), "Plate 1×2"),
    ("3024.dat",  (10, 4, 10), "Plate 1×1"),
    ("3024.dat",  (10, 4, 10), "Plate 1×1"),
    ("3024.dat",  (10, 4, 10), "Plate 1×1"),
    ("4073.dat",  (10, 3, 10), "Round Plate 1×1"),
    ("4073.dat",  (10, 3, 10), "Round Plate 1×1"),
    ("4073.dat",  (10, 3, 10), "Round Plate 1×1"),
]

FILL_TILES = [
    ("3069b.dat", (20, 3, 10), "Tile 1×2"),
    ("3069b.dat", (20, 3, 10), "Tile 1×2"),
    ("3069b.dat", (20, 3, 10), "Tile 1×2"),
    ("3070b.dat", (10, 3, 10), "Tile 1×1"),
    ("3070b.dat", (10, 3, 10), "Tile 1×1"),
    ("3070b.dat", (10, 3, 10), "Tile 1×1"),
]

FILL_BRICKS = [
    ("3005.dat",  (10, 12, 10), "Brick 1×1"),
    ("3005.dat",  (10, 12, 10), "Brick 1×1"),
    ("3004.dat",  (20, 12, 10), "Brick 1×2"),
    ("3004.dat",  (20, 12, 10), "Brick 1×2"),
    ("3062b.dat", (10, 12, 10), "Round Brick 1×1"),
    ("3062b.dat", (10, 12, 10), "Round Brick 1×1"),
]

FILL_TECHNIC = [
    ("3648b.dat", (12, 4, 12),  "Gear 24 Tooth"),
    ("3647.dat",  (10, 4, 10),  "Gear 8 Tooth"),
    ("2780.dat",  (8, 16, 8),   "Pin with Friction"),
]

ALL_FILL = FILL_PLATES + FILL_TILES + FILL_BRICKS + FILL_TECHNIC

COLORS = [4, 1, 14, 2, 25, 5, 71, 10, 26, 7, 15, 19, 72, 28, 6, 3, 9, 11, 13, 12]

# ── Parameters ────────────────────────────────────────────────────────────────
CX, CZ       = -100, -130
GRID_RES     = 14          # LDU per coverage cell
VIS_FACTOR   = 0.60        # visual footprint correction (tilted parts cover less)
GAP          = 3           # LDU clearance for fill parts
MAX_FILL     = 30          # max fill parts to add
TILT_STR     = 0.12        # fill parts are mostly flat
Y_FILL_RANGE = (220, 310)  # place fill parts below main pile

# ── Math ──────────────────────────────────────────────────────────────────────
def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def make_R_flat(rng, ry_rad, tilt=TILT_STR):
    """Near-flat rotation: fixed Y-angle + tiny X/Z wobble."""
    rx = math.radians(rng.gauss(0, tilt * 30))
    rz = math.radians(rng.gauss(0, tilt * 30))
    cy, sy = math.cos(ry_rad), math.sin(ry_rad)
    cx, sx = math.cos(rx), math.sin(rx)
    cz, sz = math.cos(rz), math.sin(rz)
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)

def make_R_tilted(rng, ts):
    """Moderate tilt for bricks/technic fill."""
    ry = math.radians(rng.uniform(-180, 180))
    s = 10 + 35 * ts
    rx = math.radians(rng.gauss(0, s))
    rz = math.radians(rng.gauss(0, s))
    cy, sy = math.cos(ry), math.sin(ry)
    cx, sx = math.cos(rx), math.sin(rx)
    cz, sz = math.cos(rz), math.sin(rz)
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

def overlap(p1, p2):
    x1,y1,z1,ex1,ey1,ez1 = p1
    x2,y2,z2,ex2,ey2,ez2 = p2
    return (abs(x1-x2) < ex1+ex2+GAP and
            abs(y1-y2) < ey1+ey2+GAP and
            abs(z1-z2) < ez1+ez2+GAP)

def r_str(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

# ── Coverage grid ─────────────────────────────────────────────────────────────
def part_cells(x, z, ex, ez):
    x0 = int(math.floor((x - ex) / GRID_RES))
    x1 = int(math.floor((x + ex) / GRID_RES))
    z0 = int(math.floor((z - ez) / GRID_RES))
    z1 = int(math.floor((z + ez) / GRID_RES))
    return {(gx, gz) for gx in range(x0, x1+1) for gz in range(z0, z1+1)}

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

# ── Parse existing LDR ────────────────────────────────────────────────────────
def parse_ldr(path):
    """Parse LDR file, return (header_lines, part_lines, placed_aabbs)."""
    header = []
    part_lines = []
    placed = []

    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("1 "):
                part_lines.append(line)
                # Parse: 1 color x y z R00 R01 R02 R10 R11 R12 R20 R21 R22 part.dat
                tokens = line.split()
                x, y, z = float(tokens[2]), float(tokens[3]), float(tokens[4])
                R = [[float(tokens[5+i*3+j]) for j in range(3)] for i in range(3)]
                pid = tokens[14]
                # Look up dims from known parts
                dims = KNOWN_DIMS.get(pid)
                if dims:
                    ex, ey, ez = extents(dims, R)
                else:
                    # Unknown part — estimate conservatively
                    ex, ey, ez = 25, 15, 25
                placed.append((x, y, z, ex, ey, ez))
            else:
                header.append(line)

    return header, part_lines, placed

# Known part half-dimensions for AABB computation
KNOWN_DIMS = {
    "3001.dat": (40,12,20), "3003.dat": (20,12,20), "3004.dat": (20,12,10),
    "3010.dat": (40,12,10), "3005.dat": (10,12,10),
    "3023.dat": (20, 4,10), "3022.dat": (20, 4,20), "3020.dat": (40, 4,20),
    "3710.dat": (40, 4,10), "3034.dat": (80, 4,20), "3795.dat": (60, 4,20),
    "3021.dat": (30, 4,20), "3024.dat": (10, 4,10),
    "3039.dat": (20,14,20), "3040b.dat": (20,14,10), "3062b.dat": (10,12,10),
    "14769.dat": (20, 3,20), "4073.dat": (10, 3,10),
    "3069b.dat": (20, 3,10), "3068b.dat": (20, 3,20), "3070b.dat": (10, 3,10),
    "61678.dat": (40, 8,20), "50950.dat": (30, 8,20),
    "32316.dat": (50,10,10), "43093.dat": (8,16,8), "2780.dat": (8,16,8),
    "3648b.dat": (12, 4,12), "3647.dat": (10, 4,10),
}

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 3:
        print("Usage: fill_gaps.py <input.ldr> <output.ldr> [--seed N]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    seed = 42
    if "--seed" in sys.argv:
        idx = sys.argv.index("--seed")
        seed = int(sys.argv[idx + 1])

    rng = _random.Random(seed)

    # 1. Parse existing model
    header, part_lines, placed = parse_ldr(input_path)
    n_original = len(part_lines)
    print(f"Parsed {n_original} parts from {input_path}", file=sys.stderr)

    # 2. Compute existing XZ coverage
    covered = set()
    all_xs = [p[0] for p in placed]
    all_zs = [p[2] for p in placed]
    all_exs = [p[3] for p in placed]
    all_ezs = [p[5] for p in placed]

    for x, y, z, ex, ey, ez in placed:
        vis_ex = ex * VIS_FACTOR
        vis_ez = ez * VIS_FACTOR
        covered |= part_cells(x, z, vis_ex, vis_ez)

    # Compute coverage oval from actual footprint (with some margin)
    x_min = min(x - e for x, e in zip(all_xs, all_exs))
    x_max = max(x + e for x, e in zip(all_xs, all_exs))
    z_min = min(z - e for z, e in zip(all_zs, all_ezs))
    z_max = max(z + e for z, e in zip(all_zs, all_ezs))

    # Use 85% of actual extent as fill oval (don't fill extreme edges)
    fill_cx = (x_min + x_max) / 2
    fill_cz = (z_min + z_max) / 2
    fill_a = (x_max - x_min) / 2 * 0.85
    fill_b = (z_max - z_min) / 2 * 0.85

    all_oval = oval_cells(fill_cx, fill_cz, fill_a, fill_b)

    gaps_before = all_oval - covered
    n_gaps_before = len(gaps_before)
    pct_before = 100.0 * len(covered & all_oval) / max(len(all_oval), 1)
    print(f"Coverage oval: center=({fill_cx:.0f},{fill_cz:.0f}) "
          f"size={fill_a:.0f}×{fill_b:.0f} LDU", file=sys.stderr)
    print(f"Coverage before fill: {pct_before:.0f}% ({n_gaps_before} gap cells)", file=sys.stderr)

    # 3. Sort gaps by distance from center (fill center first)
    def dist2(cell):
        px = cell[0] * GRID_RES + GRID_RES / 2.0
        pz = cell[1] * GRID_RES + GRID_RES / 2.0
        return (px - fill_cx)**2 + (pz - fill_cz)**2

    gaps_sorted = sorted(gaps_before, key=dist2)

    # 4. Shuffle fill parts, try to place them in gaps
    fill_parts = list(ALL_FILL)
    rng.shuffle(fill_parts)

    RY_ANGLES = [0, math.pi/2, math.pi/4, -math.pi/4, math.pi/8, -math.pi/8,
                 3*math.pi/8, -3*math.pi/8]

    new_lines = []
    n_fill = 0
    color_idx = rng.randint(0, len(COLORS) - 1)

    for gx, gz in gaps_sorted:
        if n_fill >= MAX_FILL:
            break
        if (gx, gz) in covered:
            continue

        px = gx * GRID_RES + GRID_RES / 2.0
        pz = gz * GRID_RES + GRID_RES / 2.0

        placed_here = False
        for pid, dims, desc in fill_parts:
            if placed_here:
                break
            for ry_rad in RY_ANGLES:
                if placed_here:
                    break

                # Choose rotation based on part type
                is_brick = dims[1] >= 12
                is_technic = pid in ("3648b.dat", "3647.dat", "2780.dat")

                if is_technic:
                    R = make_R_tilted(rng, 0.45)
                elif is_brick:
                    R = make_R_tilted(rng, 0.35)
                else:
                    R = make_R_flat(rng, ry_rad)

                ex, ey, ez = extents(dims, R)

                # Check if part stays within fill oval
                if abs(px - fill_cx) + ex > fill_a * 1.15:
                    continue
                if abs(pz - fill_cz) + ez > fill_b * 1.15:
                    continue

                # Try a few Y positions
                for _ in range(8):
                    y = rng.uniform(Y_FILL_RANGE[0], Y_FILL_RANGE[1])
                    cand = (px, y, pz, ex, ey, ez)
                    if not any(overlap(cand, p) for p in placed):
                        color = COLORS[color_idx % len(COLORS)]
                        color_idx += 1
                        placed.append(cand)
                        new_lines.append(
                            f"1 {color} {px:.2f} {y:.2f} {pz:.2f} {r_str(R)} {pid}")
                        covered |= part_cells(px, pz, ex, ez)
                        n_fill += 1
                        placed_here = True
                        # Remove used part from pool (each part used once)
                        fill_parts.remove((pid, dims, desc))
                        break

    # 5. Stats
    pct_after = 100.0 * len(covered & all_oval) / max(len(all_oval), 1)
    gaps_after = len(all_oval - covered)
    print(f"\nFill results:", file=sys.stderr)
    print(f"  Parts added: {n_fill}", file=sys.stderr)
    print(f"  Coverage: {pct_before:.0f}% → {pct_after:.0f}%", file=sys.stderr)
    print(f"  Gap cells: {n_gaps_before} → {gaps_after}", file=sys.stderr)
    print(f"  Total parts: {n_original} + {n_fill} = {n_original + n_fill}", file=sys.stderr)

    # 6. Write output
    with open(output_path, "w") as f:
        for line in header:
            # Update model name in header
            if line.startswith("0 Pocket ") and not line.startswith("0 Name"):
                f.write(line + " (filled)\n")
            else:
                f.write(line + "\n")
        f.write("\n")
        # Original parts
        for line in part_lines:
            f.write(line + "\n")
        # Fill parts
        if new_lines:
            f.write("0 // ── Gap-fill parts ──\n")
            for line in new_lines:
                f.write(line + "\n")

    print(f"Written: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
