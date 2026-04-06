import math, random, sys

CX, CZ   = -100, -130
# Овал для нижнего слоя — равномерное покрытие пола
OVAL_A   = 180   # радиус по X (≈9 студ → диаметр ~18)
OVAL_B   = 135   # радиус по Z (≈6.75 студ → диаметр ~13.5)
# Gaussian для верхнего слоя
SIGMA_X  = 46
SIGMA_Z  = 33
Y_MIN    = 0
Y_MAX    = 155
GAP      = 1

def sample_floor(rng):
    """Равномерно в эллипсе — для плейтов нижнего слоя."""
    while True:
        rx = rng.uniform(-1, 1)
        rz = rng.uniform(-1, 1)
        if rx*rx + rz*rz <= 1.0:
            return CX + rx*OVAL_A, CZ + rz*OVAL_B

def sample_pile(rng):
    """Gaussian — для кирпичей и акцентов верхнего слоя."""
    return rng.gauss(CX, SIGMA_X), rng.gauss(CZ, SIGMA_Z)

# (part_id, half-dims, tilt_strength, category, layer)
# layer="floor" → uniform-in-ellipse + Y near 0
# layer="pile"  → Gaussian + Y triangular
PARTS = [
    # ── FLOOR LAYER: крупные плейты, равномерно покрывают дно ──
    ("3034.dat", (80, 4,20), 0.08, "plate", "floor"),  # 2×8
    ("3795.dat", (60, 4,20), 0.08, "plate", "floor"),  # 2×6
    ("3795.dat", (60, 4,20), 0.08, "plate", "floor"),
    ("3020.dat", (40, 4,20), 0.10, "plate", "floor"),  # 2×4
    ("3020.dat", (40, 4,20), 0.10, "plate", "floor"),
    ("3020.dat", (40, 4,20), 0.10, "plate", "floor"),
    ("3020.dat", (40, 4,20), 0.10, "plate", "floor"),
    ("3710.dat", (40, 4,10), 0.10, "plate", "floor"),  # 1×4
    ("3710.dat", (40, 4,10), 0.10, "plate", "floor"),
    ("3710.dat", (40, 4,10), 0.10, "plate", "floor"),
    ("3021.dat", (30, 4,20), 0.10, "plate", "floor"),  # 2×3
    ("3021.dat", (30, 4,20), 0.10, "plate", "floor"),
    ("3022.dat", (20, 4,20), 0.12, "plate", "floor"),  # 2×2
    ("3022.dat", (20, 4,20), 0.12, "plate", "floor"),
    ("3022.dat", (20, 4,20), 0.12, "plate", "floor"),
    ("3023.dat", (20, 4,10), 0.12, "plate", "floor"),  # 1×2
    ("3023.dat", (20, 4,10), 0.12, "plate", "floor"),
    ("3023.dat", (20, 4,10), 0.12, "plate", "floor"),
    ("3023.dat", (20, 4,10), 0.12, "plate", "floor"),
    # ── PILE LAYER: кирпичи и акценты поверх ───────────────────
    ("3001.dat", (40,12,20), 0.22, "brick", "pile"),
    ("3001.dat", (40,12,20), 0.22, "brick", "pile"),
    ("3001.dat", (40,12,20), 0.22, "brick", "pile"),
    ("3001.dat", (40,12,20), 0.22, "brick", "pile"),
    ("3001.dat", (40,12,20), 0.22, "brick", "pile"),
    ("3001.dat", (40,12,20), 0.22, "brick", "pile"),
    ("3003.dat", (20,12,20), 0.22, "brick", "pile"),
    ("3003.dat", (20,12,20), 0.22, "brick", "pile"),
    ("3003.dat", (20,12,20), 0.22, "brick", "pile"),
    ("3003.dat", (20,12,20), 0.22, "brick", "pile"),
    ("3003.dat", (20,12,20), 0.22, "brick", "pile"),
    ("3004.dat", (20,12,10), 0.27, "brick", "pile"),
    ("3004.dat", (20,12,10), 0.27, "brick", "pile"),
    ("3004.dat", (20,12,10), 0.27, "brick", "pile"),
    ("3004.dat", (20,12,10), 0.27, "brick", "pile"),
    ("3010.dat", (40,12,10), 0.27, "brick", "pile"),
    ("3010.dat", (40,12,10), 0.27, "brick", "pile"),
    ("3010.dat", (40,12,10), 0.27, "brick", "pile"),
    ("3005.dat", (10,12,10), 0.38, "brick", "pile"),
    ("3005.dat", (10,12,10), 0.38, "brick", "pile"),
    ("3005.dat", (10,12,10), 0.38, "brick", "pile"),
    ("3039.dat",  (20,14,20), 0.38, "slope", "pile"),
    ("3039.dat",  (20,14,20), 0.38, "slope", "pile"),
    ("3039.dat",  (20,14,20), 0.38, "slope", "pile"),
    ("3040b.dat", (20,14,10), 0.38, "slope", "pile"),
    ("3040b.dat", (20,14,10), 0.38, "slope", "pile"),
    ("61678.dat", (40, 8,20), 0.32, "slope", "pile"),
    ("61678.dat", (40, 8,20), 0.32, "slope", "pile"),
    ("50950.dat", (30, 8,20), 0.32, "slope", "pile"),
    ("50950.dat", (30, 8,20), 0.32, "slope", "pile"),
    ("3062b.dat", (10,12,10), 0.42, "round", "pile"),
    ("3062b.dat", (10,12,10), 0.42, "round", "pile"),
    ("3062b.dat", (10,12,10), 0.42, "round", "pile"),
    ("3062b.dat", (10,12,10), 0.42, "round", "pile"),
    ("14769.dat", (20, 3,20), 0.22, "tile",  "pile"),
    ("14769.dat", (20, 3,20), 0.22, "tile",  "pile"),
    ("4073.dat",  (10, 3,10), 0.28, "tile",  "pile"),
    ("4073.dat",  (10, 3,10), 0.28, "tile",  "pile"),
    ("4073.dat",  (10, 3,10), 0.28, "tile",  "pile"),
    ("3069b.dat", (20, 3,10), 0.20, "tile",  "pile"),
    ("3069b.dat", (20, 3,10), 0.20, "tile",  "pile"),
    ("3068b.dat", (20, 3,20), 0.20, "tile",  "pile"),
    ("3068b.dat", (20, 3,20), 0.20, "tile",  "pile"),
    ("32316.dat", (50,10,10), 0.42, "technic","pile"),
    ("43093.dat", ( 8,16, 8), 0.52, "technic","pile"),
    ("2780.dat",  ( 8,16, 8), 0.52, "technic","pile"),
]

# Порядок: floor-плейты крупные→мелкие, затем pile крупные→мелкие
floor = sorted([p for p in PARTS if p[4]=="floor"], key=lambda p: p[1][0]*p[1][2], reverse=True)
pile  = sorted([p for p in PARTS if p[4]=="pile"],  key=lambda p: p[1][0]*p[1][2], reverse=True)
PARTS_ORDERED = floor + pile

COLORS = [4, 1, 14, 2, 25, 5, 71, 10, 26, 7]

def make_R(ts, rng):
    ry = math.radians(rng.uniform(-180, 180))
    r = rng.random()
    if r < 0.60:
        rx = math.radians(rng.gauss(0, 8+28*ts)); rz = math.radians(rng.gauss(0, 8+28*ts))
    elif r < 0.85:
        lim = 25+55*ts; rx = math.radians(rng.uniform(-lim,lim)); rz = math.radians(rng.uniform(-lim,lim))
    else:
        rx = math.radians(rng.uniform(-180,180)); rz = math.radians(rng.uniform(-180,180))
    cy,sy=math.cos(ry),math.sin(ry); cx,sx=math.cos(rx),math.sin(rx); cz,sz=math.cos(rz),math.sin(rz)
    def mm(A,B): return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(mm([[cy,0,sy],[0,1,0],[-sy,0,cy]],[[1,0,0],[0,cx,-sx],[0,sx,cx]]),[[cz,-sz,0],[sz,cz,0],[0,0,1]])

def ext(dims, R):
    a,b,c=dims
    return (abs(R[0][0])*a+abs(R[0][1])*b+abs(R[0][2])*c,
            abs(R[1][0])*a+abs(R[1][1])*b+abs(R[1][2])*c,
            abs(R[2][0])*a+abs(R[2][1])*b+abs(R[2][2])*c)

def ov(p1,p2):
    x1,y1,z1,ex1,ey1,ez1=p1; x2,y2,z2,ex2,ey2,ez2=p2
    return abs(x1-x2)<ex1+ex2+GAP and abs(y1-y2)<ey1+ey2+GAP and abs(z1-z2)<ez1+ez2+GAP

def generate(seed):
    rng=random.Random(seed); placed=[]; parts_out=[]; nc=nf=0
    for pid,dims,ts,cat,layer in PARTS_ORDERED:
        R=make_R(ts,rng); ex,ey,ez=ext(dims,R); color=rng.choice(COLORS)
        bp=None; bo=9999
        for _ in range(1800):
            if layer=="floor":
                x,z = sample_floor(rng)
                y = rng.triangular(Y_MIN, 60, Y_MIN+8)   # прижаты ко дну
            else:
                x,z = sample_pile(rng)
                y = rng.triangular(Y_MIN, Y_MAX, Y_MIN+18)
            pos=(x,y,z,ex,ey,ez); ovlp=sum(1 for p in placed if ov(pos,p))
            if ovlp==0: bp=pos; bo=0; nc+=1; break
            elif ovlp<bo: bo=ovlp; bp=pos
        if bo>0: nf+=1
        placed.append(bp); parts_out.append((pid,bp[0],bp[1],bp[2],R,color))
    return parts_out,nc,nf

def write_ldr(parts_out, path):
    with open(path,"w") as f:
        f.write("0 Pocket 9\n0 Name: model.ldr\n0 Author: Brickit\n0 !LEGOCOM BrickLink Studio 2.0\n0 CustomBrick\n0 FlexibleBrickControlPointUnitLength -1\n0 FlexibleBrickLockedControlPoint\n0\n")
        for pid,x,y,z,R,color in parts_out:
            f.write(f"1 {color} {x:.1f} {y:.1f} {z:.1f} {' '.join(f'{v:.4f}' for row in R for v in row)} {pid}\n")

print("Trying 100 seeds...", file=sys.stderr)
best=None; bf=9999
for seed in range(42, 142):
    po,nc,nf=generate(seed)
    pct=nf/len(po)*100
    marker=" ◀ best" if nf<bf else ""
    print(f"  seed={seed}: {nf}/{len(po)} ({pct:.0f}%){marker}", file=sys.stderr)
    if nf<bf: bf=nf; best=(seed,po,nc,nf)
    if bf==0: print("  → Zero forced, stopping early", file=sys.stderr); break

seed,po,nc,nf=best; n=len(po)
print(f"\nBest seed={seed}: {nc}/{n} clean, {nf} forced ({nf/n*100:.0f}%)", file=sys.stderr)
xs=[p[1] for p in po]; zs=[p[3] for p in po]; ys=[p[2] for p in po]
print(f"X: {min(xs):.0f}→{max(xs):.0f}  ({(max(xs)-min(xs))/20:.1f} studs, ref 17.7)", file=sys.stderr)
print(f"Z: {min(zs):.0f}→{max(zs):.0f}  ({(max(zs)-min(zs))/20:.1f} studs, ref 13.2)", file=sys.stderr)
print(f"Y: {min(ys):.0f}→{max(ys):.0f}", file=sys.stderr)
write_ldr(po, "/tmp/pocket9_model.ldr")
print("Written: /tmp/pocket9_model.ldr", file=sys.stderr)
