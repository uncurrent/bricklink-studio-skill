---
name: bricklink-studio/ldraw-format
description: >
  Read, parse, validate and understand LDraw files (.ldr, .mpd).
  Use when user uploads or references a .ldr or .mpd file, wants to understand
  its structure, count parts, find specific elements, or validate the format.
  Works in all environments — no special tools required.
compatibility:
  any: true
---

# LDraw Format — Sub-skill

> **Language policy:** All entries written to skill files during this session must be in English.
> The user interface may be in any language.


LDraw is a plain-text format. Every line is a command. Files can be opened in any text editor.

---

## File Types

| Extension | Description |
|---|---|
| `.ldr` | Single model (Linear Drawing) |
| `.mpd` | Multi-Part Document — multiple models/subfiles in one file |
| `.dat` | Part definition (from LDraw parts library) |
| `.io` | BrickLink Studio native — a ZIP archive; unzip to get LDraw inside |

To read a `.io` file: unzip it, then find the `.ldr` or `.mpd` inside.

---

## Line Format

Every non-empty line starts with a **line type** (0–5):

### Type 0 — Comment / Meta
```
0 <comment text>
0 FILE submodel.ldr        ← MPD subfile declaration
0 Name: My Model           ← model name
0 Author: Username
0 STEP                     ← instruction step break
0 NOFILE                   ← end of subfile in MPD
```

### Type 1 — Part Reference (most important)
```
1 <color> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <partfile>
```
- `color` — LDraw color ID (see `bom-export/references/color-ids.md`)
- `x y z` — position in LDraw Units (LDU). 1 stud = 20 LDU, 1 plate height = 8 LDU, 1 brick height = 24 LDU
- `a–i` — 3×3 rotation matrix (identity = `1 0 0 0 1 0 0 0 1`)
- `partfile` — part filename, e.g. `3001.dat`

**Example:**
```
1 4 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat
```
= red (color 4) 2×4 brick at origin, no rotation

### Type 2 — Line (used in part definitions, rarely in models)
### Type 3 — Triangle (part geometry)
### Type 4 — Quadrilateral (part geometry)
### Type 5 — Optional line

---

## Parsing Algorithm

To extract all parts from an LDraw file:

```python
parts = []
with open('model.ldr', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('0'):
            continue
        tokens = line.split()
        if tokens[0] == '1':
            color = int(tokens[1])
            x, y, z = float(tokens[2]), float(tokens[3]), float(tokens[4])
            # tokens[5:14] = rotation matrix
            partfile = tokens[14]  # e.g. "3001.dat"
            part_id = partfile.replace('.dat', '')
            parts.append({'part_id': part_id, 'color': color, 'x': x, 'y': y, 'z': z})
```

For MPD files — split on `0 FILE` lines first, parse each subfile separately.

---

## Common Analysis Tasks

### Count total parts
```python
from collections import Counter
counts = Counter(p['part_id'] for p in parts)
```

### Find parts by color
```python
red_parts = [p for p in parts if p['color'] == 4]
```

### Find bounding box
```python
xs = [p['x'] for p in parts]
print(f"Width: {max(xs) - min(xs)} LDU = {(max(xs)-min(xs))/20:.1f} studs")
```

### Detect submodels (MPD)
Look for lines: `0 FILE <name>` — each is a separate submodel.

---

## Reference Files

- `references/syntax.md` — Full line type reference with edge cases
- `references/common-parts.md` — Top-200 part IDs with names and dimensions

---

## See Also

- LDraw packaging and IO scripts: `projects/*/scripts/` (ZIP handling and file conversion)
- Recipes for LDraw processing: `projects/*/recipes/` and `recipes/`
- Always check existing conversion scripts before implementing custom parsers
