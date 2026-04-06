#!/usr/bin/env python3
"""
mod_fill.py v2 — Small gap filler (random sampling approach)

Instead of grid-based gap detection (which fails with large tilted-part AABBs),
uses Monte Carlo: sample random positions in the oval, check for overlaps
against ALL existing parts parsed directly from LDR lines, place filler if clear.

Parses existing LDR to get placed positions + rotation-aware extents.
"""
import math, random as _random

# ── known part half-extents ────────────────────────────────────────────────────
DIMS = {
    "3001.dat":  (40, 12, 20), "3003.dat":  (20, 12, 20),
    "3010.dat":  (40, 12, 10), "3004.dat":  (20, 12, 10),
    "3005.dat":  (10, 12, 10), "3062b.dat": (10, 12, 10),
    "3020.dat":  (40,  2, 20), "3021.dat":  (30,  2, 20),
    "3022.dat":  (20,  2, 20), "3710.dat":  (40,  2, 10),
    "3023.dat":  (20,  2, 10), "3024.dat":  (10,  2, 10),
    "3068b.dat": (20,  2, 20), "3069b.dat": (20,  2, 10),
    "3070b.dat": (10,  2, 10), "4073.dat":  (10,  2, 10),
    "6636.dat":  (60,  2, 10), "3648b.dat": (20,  4, 20),
    "3647.dat":  (12,  5, 12), "2780.dat":  ( 4, 14,  4),
}

FILLER_GAP = 4   # gap between filler and existing parts

# ── filler palette: (pid, dims, type, max_count) ──────────────────────────────
FILLER_PALETTE = [
    ("3024.dat",  (10,  2, 10), "plate",   8),   # 1×1 plate
    ("3070b.dat", (10,  2, 10), "tile",    6),   # 1×1 tile
    ("4073.dat",  (10,  2, 10), "tile",    4),   # 1×1 round
    ("3005.dat",  (10, 12, 10), "brick",   4),   # 1×1 brick
    ("3062b.dat", (10, 12, 10), "brick",   3),   # 1×1 round brick
    ("3023.dat",  (20,  2, 10), "plate",   6),   # 1×2 plate
    ("3069b.dat", (20,  2, 10), "tile",    4),   # 1×2 tile
    ("3004.dat",  (20, 12, 10), "brick",   3),   # 1×2 brick
    ("3648b.dat", (20,  4, 20), "special", 1),   # 24T gear
    ("3647.dat",  (12,  5, 12), "special", 1),   # 8T gear
    ("2780.dat",  ( 4, 14,  4), "special", 1),   # Technic pin
]
MAX_FILL_PARTS = 20
MAX_TRIES_PER_PART = 300   # Monte Carlo attempts per filler

COLORS = [4, 1, 14, 25, 2, 6, 10, 3, 9, 11, 13, 12, 5, 15, 19, 72,
          28, 47, 18, 46]

# ── math ───────────────────────────────────────────────────────────────────────
def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def make_R_flat(rng, ry, tilt_str):
    rx = math.radians(rng.gauss(0, tilt_str * 30))
    rz = math.radians(rng.gauss(0, tilt_str * 30))
    cy,sy=math.cos(ry),math.sin(ry); cx,sx=math.cos(rx),math.sin(rx)
    cz,sz=math.cos(rz),math.sin(rz)
    Ry=[[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx=[[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz=[[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry,Rx),Rz)

def extents_xz(dims, R):
    a,b,c=dims
    return (abs(R[0][0])*a+abs(R[0][1])*b+abs(R[0][2])*c,
            abs(R[2][0])*a+abs(R[2][1])*b+abs(R[2][2])*c)

def r_str(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

def in_oval(x, z, cx, cz, oa, ob):
    return ((x-cx)/oa)**2 + ((z-cz)/ob)**2 <= 1.0

def overlap_xz(p1, p2, gap):
    x1,z1,ex1,ez1=p1; x2,z2,ex2,ez2=p2
    return abs(x1-x2)<ex1+ex2+gap and abs(z1-z2)<ez1+ez2+gap

def assign_y_filler(rng, ptype):
    if ptype=="brick":   return rng.uniform(-18, -2)
    if ptype=="special": return rng.uniform(-8, 4)
    return rng.uniform(-6, 8)

# ── parse existing LDR for placements ─────────────────────────────────────────
# Scale factor for existing parts' effective collision radius.
# AABB of a tilted part (e.g. 45° rotation) is ~2× the actual dims, which
# would block all gap space. Using 0.65× of the nominal dims gives a much
# better approximation of the actual visual footprint for gap detection.
EXISTING_SCALE = 0.65

def parse_ldr_xz(lines):
    """
    Re-parse LDR lines to get (x, z, ex, ez) for gap-filling purposes.
    Uses NOMINAL dims × EXISTING_SCALE, not the rotation-aware AABB,
    to avoid over-blocking the available space.
    """
    placed = []
    for line in lines:
        tokens = line.strip().split()
        if len(tokens) < 15 or tokens[0] != '1': continue
        x = float(tokens[2]); z = float(tokens[4])
        pid = tokens[14]
        dims = DIMS.get(pid)
        if dims:
            # Use nominal XZ dims scaled down, ignoring actual rotation
            ex = dims[0] * EXISTING_SCALE
            ez = dims[2] * EXISTING_SCALE
            placed.append((x, z, ex, ez))
    return placed

# ── main function ─────────────────────────────────────────────────────────────
def apply_fill_small(base_lines, _ignored_placed_xz=None, seed=42,
                     cx=-100, cz=-130, oval_a=185, oval_b=145):
    """
    Parse base_lines to get exact placements, then fill gaps with small parts.
    Returns (new_filler_lines, updated_placed_xz).
    """
    rng = _random.Random(seed + 2000)

    # Parse existing placements directly from LDR (uses actual rotation matrix)
    placed_xz = parse_ldr_xz(base_lines)
    print(f"    [fill] Parsed {len(placed_xz)} existing parts from LDR", flush=True)

    # Check a sample of AABB extents
    if placed_xz:
        sample = placed_xz[:3]
        for s in sample:
            print(f"    [fill]   sample: x={s[0]:.0f} z={s[1]:.0f} ex={s[2]:.1f} ez={s[3]:.1f}")

    # Build flat pool of filler parts
    pool = []
    counts = {}
    for (pid, dims, ptype, max_c) in FILLER_PALETTE:
        pool.extend([(pid, dims, ptype)] * max_c)
        counts[pid] = 0
    rng.shuffle(pool)

    max_counts = {pid: max_c for pid, dims, ptype, max_c in FILLER_PALETTE}

    placed_now = list(placed_xz)
    new_lines  = []
    fill_count = 0
    color_i    = rng.randint(0, len(COLORS)-1)

    for pid, dims, ptype in pool:
        if fill_count >= MAX_FILL_PARTS:
            break
        if counts.get(pid, 0) >= max_counts.get(pid, 99):
            continue

        # Monte Carlo: try random positions in oval
        tilt = 0.05 if ptype in ("plate", "tile") else 0.20
        placed_this = False

        for _ in range(MAX_TRIES_PER_PART):
            # Sample random position within oval (rejection sampling)
            rx = rng.uniform(-oval_a, oval_a)
            rz = rng.uniform(-oval_b, oval_b)
            nx = cx + rx; nz = cz + rz
            if not in_oval(nx, nz, cx, cz, oval_a, oval_b):
                continue

            ry = rng.uniform(0, 2 * math.pi)
            R  = make_R_flat(rng, ry, tilt)
            ex, ez = extents_xz(dims, R)

            cand = (nx, nz, ex, ez)
            if any(overlap_xz(cand, p, FILLER_GAP) for p in placed_now):
                continue

            # Placed!
            y = assign_y_filler(rng, ptype)
            color = COLORS[color_i % len(COLORS)]
            color_i += 1
            placed_now.append(cand)
            new_lines.append(f"1 {color} {nx:.2f} {y:.2f} {nz:.2f} {r_str(R)} {pid}")
            fill_count += 1
            counts[pid] = counts.get(pid, 0) + 1
            placed_this = True
            break

        if not placed_this:
            pass  # Skip this part type, try next

    print(f"    [fill] Added {fill_count} filler parts", flush=True)
    return new_lines, placed_now
