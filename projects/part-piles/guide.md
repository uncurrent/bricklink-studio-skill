---
project: part-piles
status: active
created: 2026-04-05
---

# Part Piles — Project Guide

Generate photorealistic renders of random LEGO part piles — used as app graphics,
"bag of parts" imagery, and decorative UI assets.

---

## Goal

Final deliverable: rendered PNG/JPEG of a natural-looking pile of LEGO parts,
suitable for use in app UI (e.g. part bag illustrations, category headers, hero images).

---

## Constraints

- **Visual:** parts must look naturally scattered, not arranged in a grid or symmetric pattern
- **Composition:** pile should read clearly against the intended background (transparent or solid)
- **Scale:** parts should be recognizable — not too small
- **Count:** enough parts to look like a "bag" (15–40 parts typically), not a single part or a mountain
- **Variety:** mix of part types and colors unless a specific set is requested
- **No instructions:** this is for render output only, not buildable models

---

## Sub-skills to Load

| Sub-skill | Why needed |
|---|---|
| `gui-navigation/guide.md` | Placing and arranging parts in Studio |
| `render/guide.md` | Render settings for app graphics output |
| `model-generation/guide.md` | If generating LDraw code for the pile directly |

---

## Workflow

### Option A: Studio Random Pile (GUI)

1. Open Studio → new empty file
2. Add parts from palette (or paste from LDraw) — 15–40 parts, varied
3. Select all → **Edit → Random Pile** (Workflow 8 in `gui-navigation/references/workflows.md`)
4. Adjust camera: slightly elevated angle, parts fill ~70% of frame
5. Render → export PNG

### Option B: LDraw Code Generation (no GUI)

1. Generate a list of parts with randomized positions and rotations using `model-generation/guide.md`
2. Each part: random X/Z position within a defined footprint, Y slightly above 0, random rotation on all axes
3. No connectivity required — parts can float slightly or overlap (realistic pile look)
4. Save as `.ldr` → import into Studio → render

### Option C: Blender Pipeline

For highest quality. See `render/guide.md` → Blender section.

---

## Key Settings

### Studio Random Pile

- Grid: OFF (snapping disabled for pile generation)
- Collision Detection: OFF (parts can overlap naturally)
- Pile radius: ~100–200 LDU for a 20-part pile

### Render Settings

| Setting | Value | Notes |
|---|---|---|
| Resolution | 800×800 or 1200×1200 | Square for app tiles |
| Background | Transparent or white | Depends on app context |
| Camera angle | 35–55° elevation | Lower = more dramatic |
| FOV | 30–45° | Tighter FOV feels more "product photo" |
| Lighting | Three-point or HDR | Avoid flat directional only |
| Stud logo | ON | Makes parts clearly recognizable as LEGO |

### LDraw random positioning

```python
import random, math

def random_pile_position(index, radius=150):
    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, radius) ** 0.5 * radius  # sqrt for even distribution
    x = r * math.cos(angle)
    z = r * math.sin(angle)
    y = random.uniform(0, 20)  # slight vertical spread
    rx = random.randint(0, 3) * 90
    ry = random.randint(0, 3) * 90
    rz = random.randint(0, 3) * 90
    return x, y, z, rx, ry, rz
```

---

## Known Good Results

*(Append links or descriptions of accepted renders here as the project progresses)*

---

## Related Knowledge

- `knowledge/INDEX.md` → GEN01 (3D-to-Lego for converting 3D meshes to piles of bricks)
- `gui-navigation/references/workflows.md` → Workflow 8: Random Pile
- `render/references/settings.md` → quality presets and Stud Logo toggle
