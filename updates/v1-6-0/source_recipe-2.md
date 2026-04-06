# Pockets — Recipe 2: Sequential Outward Placement

## Concept

Parts are placed **sequentially from center outward** using a touch-point formula.
Each new part is placed at the position closest to center that touches an existing part
without XZ-overlapping any already-placed part. Fully random Y-rotation (0–360°) gives
organic angle variety. Y positions are assigned by part type (bricks stick up, plates lie flat).

This is distinct from Recipe 1 (developed in a separate chat) which uses a different approach.

---

## Pipeline

```
generator_toplayer_v4.py
        │
        ▼  (31 parts, seed=100, oval 185×145 LDU, GAP=0)
   base top layer
        │
   ┌────┴────┐
   │         │
mod_rotate  mod_fill
   │         │
12-B        12-C
   └────┬────┘
        │
       12-D
```

### Scripts

| File | What it does |
|------|-------------|
| `generator_toplayer_v4.py` | Generates the base top layer. Sequential outward placement, XZ-only collision, mixed bricks + plates + tiles. Best of 60 seeds. |
| `generator_toplayer_with_modifiers.py` | Driver: runs v4 base, then applies both modifiers, writes 12-B / 12-C / 12-D. |
| `modifier_rotation_shuffle.py` | Shuffles rotations of all parts: 50% upright, 20% leaning, 17% on-side (shows side face from top), 5% upside-down, 8% extreme diagonal. |
| `modifier_fill_small_parts.py` | Fills gaps with small parts: 1×1 / 1×2 plates, tiles, bricks + 1 gear (24T or 8T) + 1 Technic pin. Monte Carlo placement with `EXISTING_SCALE=0.65` to account for AABB over-estimation of tilted parts. |

### Key parameters (v4 base)

```python
OVAL_A, OVAL_B = 185, 145   # placement oval (LDU)
GAP            = 0           # no XZ overlap allowed
N_ANGLES       = 96          # touch-point candidates per existing part
TOP_K          = 10          # pick randomly from top-K center-closest positions
TILT           = {"brick": 0.40, "plate": 0.07, "tile": 0.04}
```

### Running

```bash
cd BrickitStudio/Pockets-recipe-2
python3 generator_toplayer_with_modifiers.py
# → writes /tmp/pocket12B.ldr  /tmp/pocket12C.ldr  /tmp/pocket12D.ldr
```

---

## Outputs

| File | Parts | Description |
|------|-------|-------------|
| `Pocket 12 (base-v4).io` | 31 | Base placement, v4 algorithm |
| `Pocket 12-B (rotation-shuffle).io` | 31 | Same positions, radically varied rotations |
| `Pocket 12-C (small-fillers).io` | 51 | Base + 20 small gap-fillers |
| `Pocket 12-D (both-mods).io` | 51 | Rotation shuffle + gap-fillers |

---

## Known issues / next steps

- Some AABB overlap remains for tilted bricks (acceptable for pile look)
- `modifier_fill_small_parts.py` uses `EXISTING_SCALE=0.65` on nominal dims for collision — good approximation but some fillers may visually overlap heavy-tilted parts
- Next iteration: add lower hero layers (bricks with tilt) + accent layer below the top layer
