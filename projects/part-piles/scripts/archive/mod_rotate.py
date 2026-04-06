#!/usr/bin/env python3
"""
mod_rotate.py — Rotation shuffle modifier

Takes a list of LDR lines, returns new lines with diversified rotations:
- ~50% upright (small tilt, studs face up)
- ~20% leaning (15-35° tilt, dramatic angles)
- ~20% on-side (≈90° around X or Z — shows side face from top)
-  ~5% upside-down (≈180° around X — shows anti-stud underside from top)
-  ~5% extreme (40-70° dramatic diagonal)

All Y-rotations remain fully random (no discrete snapping).
X/Z positions are preserved. Y is re-assigned by part type to look natural.
"""
import math, random as _random

# ── known part dims (half-extents in LDU) ─────────────────────────────────────
DIMS = {
    "3001.dat":  (40, 12, 20),  # Brick 2×4
    "3003.dat":  (20, 12, 20),  # Brick 2×2
    "3010.dat":  (40, 12, 10),  # Brick 1×4
    "3004.dat":  (20, 12, 10),  # Brick 1×2
    "3005.dat":  (10, 12, 10),  # Brick 1×1
    "3020.dat":  (40,  2, 20),  # Plate 2×4
    "3021.dat":  (30,  2, 20),  # Plate 2×3
    "3022.dat":  (20,  2, 20),  # Plate 2×2
    "3710.dat":  (40,  2, 10),  # Plate 1×4
    "3023.dat":  (20,  2, 10),  # Plate 1×2
    "3024.dat":  (10,  2, 10),  # Plate 1×1
    "3068b.dat": (20,  2, 20),  # Tile 2×2
    "3069b.dat": (20,  2, 10),  # Tile 1×2
    "3070b.dat": (10,  2, 10),  # Tile 1×1
    "4073.dat":  (10,  2, 10),  # Plate 1×1 round
    "6636.dat":  (60,  2, 10),  # Tile 1×6
    "3648b.dat": (20,  4, 20),  # Gear 24T
    "3647.dat":  (12,  5, 12),  # Gear 8T
    "2780.dat":  ( 4, 14,  4),  # Technic Pin
}

TYPE_OF = {
    "3001.dat": "brick", "3003.dat": "brick", "3010.dat": "brick",
    "3004.dat": "brick", "3005.dat": "brick",
    "3020.dat": "plate", "3021.dat": "plate", "3022.dat": "plate",
    "3710.dat": "plate", "3023.dat": "plate", "3024.dat": "plate",
    "3068b.dat": "tile", "3069b.dat": "tile", "3070b.dat": "tile",
    "4073.dat":  "tile", "6636.dat":  "tile",
    "3648b.dat": "special", "3647.dat": "special", "2780.dat": "special",
}

def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def make_R(ry, rx, rz):
    cy,sy = math.cos(ry),math.sin(ry)
    cx,sx = math.cos(rx),math.sin(rx)
    cz,sz = math.cos(rz),math.sin(rz)
    Ry = [[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx = [[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz = [[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry, Rx), Rz)

def r_str(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

def assign_y_for_mode(rng, ptype, mode):
    """Y by part type and rotation mode. LDraw Y increases downward.
    Negative Y = visually higher. We keep similar ranges to v4 but
    adjust: on-side parts sit lower (bigger visual extent)."""
    if ptype == "brick":
        if mode == "upright":    return rng.uniform(-28, -6)
        if mode == "leaning":    return rng.uniform(-22, -4)
        if mode == "on_side":    return rng.uniform(-16, 0)   # wider, sits lower
        if mode == "upsidedown": return rng.uniform(-28, -8)
        return rng.uniform(-25, -4)
    elif ptype == "tile":
        return rng.uniform(-4, 6)
    else:  # plate
        return rng.uniform(-10, 10)

def apply_rotation_shuffle(lines, seed=42):
    """Return new LDR lines with shuffled rotations."""
    rng = _random.Random(seed)
    new_lines = []

    for line in lines:
        stripped = line.strip()
        tokens   = stripped.split()

        if len(tokens) < 15 or tokens[0] != '1':
            new_lines.append(stripped)
            continue

        color = tokens[1]
        x     = tokens[2]
        z     = tokens[4]   # keep original XZ
        pid   = tokens[14]

        dims  = DIMS.get(pid)
        ptype = TYPE_OF.get(pid, "plate")

        if dims is None:
            new_lines.append(stripped)
            continue

        # ── choose rotation mode ──────────────────────────────────────
        ry = rng.uniform(0, 2 * math.pi)
        r  = rng.random()

        if r < 0.50:          # upright — small tilt
            mode = "upright"
            rx = math.radians(rng.gauss(0, 8))
            rz = math.radians(rng.gauss(0, 8))

        elif r < 0.70:        # leaning — 15-35° tilt
            mode = "leaning"
            rx = math.radians(rng.gauss(0, 22))
            rz = math.radians(rng.gauss(0, 22))

        elif r < 0.87:        # on side — ≈90° around X or Z
            mode = "on_side"
            if rng.random() < 0.5:
                rx = math.radians(90 + rng.gauss(0, 10))
                rz = math.radians(rng.gauss(0,  5))
            else:
                rx = math.radians(rng.gauss(0,  5))
                rz = math.radians(90 + rng.gauss(0, 10))

        elif r < 0.92:        # upside-down — ≈180° around X
            mode = "upsidedown"
            rx = math.radians(180 + rng.gauss(0, 6))
            rz = math.radians(rng.gauss(0, 6))

        else:                 # extreme diagonal — 40-70°
            mode = "extreme"
            rx = math.radians(rng.choice([45, -45, 60, -60]) + rng.gauss(0, 8))
            rz = math.radians(rng.gauss(0, 15))

        y = assign_y_for_mode(rng, ptype, mode)
        R = make_R(ry, rx, rz)
        new_lines.append(f"1 {color} {x} {y:.2f} {z} {r_str(R)} {pid}")

    return new_lines
