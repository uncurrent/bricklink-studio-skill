#!/usr/bin/env python3
"""
gen_pocket12_BCD.py — Driver: generates Pocket 12-B, 12-C, 12-D

  12-B = v4 base  + rotation shuffle (mod_rotate)
  12-C = v4 base  + small fillers   (mod_fill)
  12-D = v4 base  + both

The v4 base is re-generated here (seed=100, same params as v4).
"""
import sys, os, math, random as _random
sys.path.insert(0, '/tmp')

# ── import modifiers ───────────────────────────────────────────────────────────
from mod_rotate import apply_rotation_shuffle
from mod_fill   import apply_fill_small

# ── replicate v4 generator inline (same params) ────────────────────────────────
import math, random as _random

CX, CZ   = -100, -130
OVAL_A   = 185
OVAL_B   = 145
GAP      = 0
N_ANGLES = 96
TOP_K    = 10

COLORS = [4, 1, 14, 25, 2, 6, 10, 3, 9, 11, 13, 12, 5, 15, 19, 72,
          28, 47, 18, 46]

PALETTE = [
    ("3001.dat", (40, 12, 20), "brick"),
    ("3001.dat", (40, 12, 20), "brick"),
    ("3001.dat", (40, 12, 20), "brick"),
    ("3003.dat", (20, 12, 20), "brick"),
    ("3003.dat", (20, 12, 20), "brick"),
    ("3003.dat", (20, 12, 20), "brick"),
    ("3010.dat", (40, 12, 10), "brick"),
    ("3010.dat", (40, 12, 10), "brick"),
    ("3004.dat", (20, 12, 10), "brick"),
    ("3004.dat", (20, 12, 10), "brick"),
    ("3004.dat", (20, 12, 10), "brick"),
    ("3005.dat", (10, 12, 10), "brick"),
    ("3005.dat", (10, 12, 10), "brick"),
    ("3005.dat", (10, 12, 10), "brick"),
    ("3020.dat", (40,  2, 20), "plate"),
    ("3020.dat", (40,  2, 20), "plate"),
    ("3020.dat", (40,  2, 20), "plate"),
    ("3020.dat", (40,  2, 20), "plate"),
    ("3021.dat", (30,  2, 20), "plate"),
    ("3021.dat", (30,  2, 20), "plate"),
    ("3021.dat", (30,  2, 20), "plate"),
    ("3022.dat", (20,  2, 20), "plate"),
    ("3022.dat", (20,  2, 20), "plate"),
    ("3022.dat", (20,  2, 20), "plate"),
    ("3022.dat", (20,  2, 20), "plate"),
    ("3022.dat", (20,  2, 20), "plate"),
    ("3710.dat", (40,  2, 10), "plate"),
    ("3710.dat", (40,  2, 10), "plate"),
    ("3710.dat", (40,  2, 10), "plate"),
    ("3023.dat", (20,  2, 10), "plate"),
    ("3023.dat", (20,  2, 10), "plate"),
    ("3023.dat", (20,  2, 10), "plate"),
    ("3023.dat", (20,  2, 10), "plate"),
    ("3024.dat", (10,  2, 10), "plate"),
    ("3024.dat", (10,  2, 10), "plate"),
    ("3024.dat", (10,  2, 10), "plate"),
    ("3068b.dat",(20,  2, 20), "tile"),
    ("3068b.dat",(20,  2, 20), "tile"),
    ("3068b.dat",(20,  2, 20), "tile"),
    ("3069b.dat",(20,  2, 10), "tile"),
    ("3069b.dat",(20,  2, 10), "tile"),
    ("3069b.dat",(20,  2, 10), "tile"),
    ("3069b.dat",(20,  2, 10), "tile"),
    ("4073.dat", (10,  2, 10), "tile"),
    ("4073.dat", (10,  2, 10), "tile"),
    ("4073.dat", (10,  2, 10), "tile"),
    ("3070b.dat",(10,  2, 10), "tile"),
    ("3070b.dat",(10,  2, 10), "tile"),
    ("6636.dat", (60,  2, 10), "tile"),
    ("6636.dat", (60,  2, 10), "tile"),
]

TILT = {"brick": 0.40, "plate": 0.07, "tile": 0.04}

def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def make_R(rng, ry, tilt_str):
    rx = math.radians(rng.gauss(0, tilt_str*30))
    rz = math.radians(rng.gauss(0, tilt_str*30))
    cy,sy=math.cos(ry),math.sin(ry)
    cx,sx=math.cos(rx),math.sin(rx)
    cz,sz=math.cos(rz),math.sin(rz)
    Ry=[[cy,0,sy],[0,1,0],[-sy,0,cy]]
    Rx=[[1,0,0],[0,cx,-sx],[0,sx,cx]]
    Rz=[[cz,-sz,0],[sz,cz,0],[0,0,1]]
    return mm(mm(Ry,Rx),Rz)

def extents_xz(dims, R):
    a,b,c=dims
    ex=abs(R[0][0])*a+abs(R[0][1])*b+abs(R[0][2])*c
    ez=abs(R[2][0])*a+abs(R[2][1])*b+abs(R[2][2])*c
    return ex,ez

def r_str(R):
    return " ".join(f"{R[i][j]:.6f}" for i in range(3) for j in range(3))

def in_oval(x,z): return ((x-CX)/OVAL_A)**2+((z-CZ)/OVAL_B)**2<=1.0
def overlap_xz(p1,p2):
    x1,z1,ex1,ez1=p1; x2,z2,ex2,ez2=p2
    return abs(x1-x2)<ex1+ex2+GAP and abs(z1-z2)<ez1+ez2+GAP

def touch_d(rex,rez,ex,ez,ca,sa):
    aca,asa=abs(ca),abs(sa)
    if aca<1e-9: return(rez+ez+GAP)/asa
    if asa<1e-9: return(rex+ex+GAP)/aca
    return min((rex+ex+GAP)/aca,(rez+ez+GAP)/asa)

def assign_y(rng, ptype):
    if ptype=="brick": return rng.uniform(-30,-4)
    if ptype=="tile":  return rng.uniform(-4,6)
    return rng.uniform(-10,10)

def generate_v4_base(seed):
    rng = _random.Random(seed)
    parts = list(PALETTE[:50])
    parts.sort(key=lambda p: -(p[1][0]*p[1][2]))
    for i in range(len(parts)):
        j = i + rng.randint(0, min(4, len(parts)-i-1))
        parts[i], parts[j] = parts[j], parts[i]

    angles = [2*math.pi*i/N_ANGLES for i in range(N_ANGLES)]
    placed_xz = []
    lines = []
    color_i = 0

    for pid, dims, ptype in parts:
        color = COLORS[color_i % len(COLORS)]
        color_i += 1
        ry  = rng.uniform(0, 2*math.pi)
        R   = make_R(rng, ry, TILT[ptype])
        ex,ez = extents_xz(dims, R)
        y   = assign_y(rng, ptype)

        if not placed_xz:
            x = CX + rng.gauss(0,5); z = CZ + rng.gauss(0,5)
            placed_xz.append((x,z,ex,ez))
            lines.append(f"1 {color} {x:.2f} {y:.2f} {z:.2f} {r_str(R)} {pid}")
            continue

        candidates = []
        for ref in placed_xz:
            rx0,rz0,rex,rez = ref
            for angle in angles:
                ca,sa = math.cos(angle),math.sin(angle)
                d  = touch_d(rex,rez,ex,ez,ca,sa)
                nx = rx0+d*ca; nz = rz0+d*sa
                if not in_oval(nx,nz): continue
                cxz = (nx,nz,ex,ez)
                if not any(overlap_xz(cxz,p) for p in placed_xz):
                    dist2 = (nx-CX)**2+(nz-CZ)**2
                    candidates.append((dist2,nx,nz))

        if not candidates: continue
        candidates.sort(key=lambda c:c[0])
        k = min(TOP_K, len(candidates))
        weights = [1.0/(i+1) for i in range(k)]
        tw=sum(weights); r=rng.uniform(0,tw)
        acc=0.0; chosen=candidates[0]
        for i,w in enumerate(weights):
            acc+=w
            if r<=acc: chosen=candidates[i]; break
        _, nx, nz = chosen
        placed_xz.append((nx,nz,ex,ez))
        lines.append(f"1 {color} {nx:.2f} {y:.2f} {nz:.2f} {r_str(R)} {pid}")

    return lines, placed_xz

# ── generate base ──────────────────────────────────────────────────────────────
print("Generating v4 base (seed=100)...", file=sys.stderr)
base_lines, base_xz = generate_v4_base(seed=100)
print(f"  Base: {len(base_lines)} parts placed", file=sys.stderr)

HEADER = """\
0 {title}
0 Name: model.ldr
0 Author: Brickit
0 !LEGOCOM BrickLink Studio 2.0
0 CustomBrick
0 FlexibleBrickControlPointUnitLength -1
0 FlexibleBrickControlPointUnitLength -1

"""

def write_ldr(path, title, part_lines):
    with open(path, 'w') as f:
        f.write(HEADER.format(title=title))
        for line in part_lines:
            f.write(line + "\n")
    print(f"  Written: {path} ({len(part_lines)} parts)", file=sys.stderr)

# ── 12-B: rotation shuffle ────────────────────────────────────────────────────
print("\n--- Pocket 12-B: Rotation shuffle ---", file=sys.stderr)
lines_B = apply_rotation_shuffle(base_lines, seed=100)
write_ldr("/tmp/pocket12B.ldr", "Pocket 12-B - Rotation Shuffle", lines_B)

# ── 12-C: small fillers ───────────────────────────────────────────────────────
print("\n--- Pocket 12-C: Small fillers ---", file=sys.stderr)
fill_lines_C, xz_C = apply_fill_small(base_lines, base_xz, seed=100,
                                       cx=CX, cz=CZ, oval_a=OVAL_A, oval_b=OVAL_B)
print(f"  Fillers added: {len(fill_lines_C)}", file=sys.stderr)
lines_C = base_lines + fill_lines_C
write_ldr("/tmp/pocket12C.ldr", "Pocket 12-C - Small Fillers", lines_C)

# ── 12-D: both modifications ──────────────────────────────────────────────────
print("\n--- Pocket 12-D: Rotation shuffle + fillers ---", file=sys.stderr)
lines_D_base = apply_rotation_shuffle(base_lines, seed=100)
fill_lines_D, _ = apply_fill_small(lines_D_base, base_xz, seed=100,
                                    cx=CX, cz=CZ, oval_a=OVAL_A, oval_b=OVAL_B)
print(f"  Fillers added: {len(fill_lines_D)}", file=sys.stderr)
lines_D = lines_D_base + fill_lines_D
write_ldr("/tmp/pocket12D.ldr", "Pocket 12-D - Both Mods", lines_D)

print("\nAll done!", file=sys.stderr)
