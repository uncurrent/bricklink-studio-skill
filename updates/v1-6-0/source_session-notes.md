# Brickit Pockets — Stud.io Session Notes

Last updated: 2026-04-04

---

## .io File Format

The `.io` file (Stud.io) is a ZIP archive containing the following files:

```
model.ldr       ← MAIN file — Stud.io uses this for 3D rendering
model.lxfml     ← XML metadata (Stud.io reads it, but rendering is based on model.ldr)
modelv2.ldr
model2.ldr
thumbnail.png
errorPartList.err
.info
```

**Critical:** Stud.io reads `model.ldr` for 3D rendering, NOT `model.lxfml`.
In early attempts we were editing only LXFML — the model did not change.
Always edit `model.ldr`.

---

## model.ldr Format (LDraw)

Each part is one line in the format:
```
1 <ldraw_color> <x> <y> <z> <r11> <r12> <r13> <r21> <r22> <r23> <r31> <r32> <r33> <partname>.dat
```

Example:
```
1 484 40.000000 17.447920 -130.831600 1.000000 0.000000 0.000000 0.000000 0.807990 -0.589197 0.000000 0.589197 0.807990 3005.dat
```

- Fields 2–4: position (X, Y, Z)
- Fields 5–13: 3×3 rotation matrix
- Field 14 (index 14 in split()): part filename

Comments start with `0 `. Part lines start with `1 `.

---

## Programmatic Editing of .io Files

```python
import zipfile

# Read
with zipfile.ZipFile("Pocket 1.io", 'r') as z:
    files = {name: z.read(name) for name in z.namelist()}

# Edit model.ldr
ldr = files['model.ldr'].decode('utf-8', errors='replace')

REPLACEMENTS = {
    '3022.dat': '3003.dat',   # Plate 2x2 → Brick 2x2
    # ...
}

new_lines = []
for line in ldr.splitlines(keepends=True):
    if line.strip().startswith('1 '):
        for old, new in REPLACEMENTS.items():
            line = line.replace(old, new, 1)
    new_lines.append(line)

files['model.ldr'] = ''.join(new_lines).encode('utf-8')

# Write new file
with zipfile.ZipFile("Pocket 2.io", 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        z.writestr(name, data)
```

**Important:** when creating a new ZIP, preserve ALL files from the archive (including thumbnail.png, .info, etc.), otherwise Stud.io may fail to open the file.

---

## Analyzing Parts in a .io File

```python
import zipfile
from collections import Counter

with zipfile.ZipFile("Pocket 1.io", 'r') as z:
    ldr = z.read("model.ldr").decode("utf-8", errors="replace")

counts = Counter(
    line.split()[14]
    for line in ldr.splitlines()
    if line.strip().startswith("1 ")
)
for part, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{count}x {part}")
```

---

## Manual Part Replacement in Stud.io (UI)

Workflow (slow, but gives precise control):

1. Open the model in Stud.io
2. In the Step List (right panel) — click a part → it gets highlighted in the viewport
3. Click the **REPLACE** tab (top left corner)
4. Type the desired part name in the REPLACE tab search field
5. Double-click the part from the results — the replacement is applied

**Multi-select:** Cmd+click multiple parts in the Step List, then double-click the replacement — all selected parts will be replaced.

**Known issues:**
- Cmd+A in the REPLACE search field types the letter "a" instead of selecting all → use the × button to clear instead
- With a mixed selection of different part types, REPLACE may find no candidates → replace one type at a time
- Stud.io **auto-saves** changes to the file without warning — undo (Cmd+Z) works, but does not always roll back everything

---

## Current File State

### Pocket 1.io
89 parts. Dominant pieces:
- 7× Plate 2×2 (3022.dat)
- 6× Tile 2×2 (3068b.dat)
- 5× Plate 1×2 (3023a.dat)
- 3× Brick 1×1 (3005.dat)
- 3× Brick 2×4 (3001.dat)
- 3× Plate 2×4 (3020.dat)
- and many unique decorative parts (wheel, ice cream cone, technic brick, etc.)

**Note:** Pocket 1.io was partially modified via UI (Stud.io auto-saved). If the original version is needed — restore from git.

### Pocket 2.io
89 parts. Dominant pieces (intentionally different from Pocket 1):
- 7× Brick 1×4 (3010.dat)
- 7× Brick 2×2 (3003.dat)
- 5× Slope 45° 2×1 (3040b.dat)
- 4× Brick 1×1 Round (3062b.dat)
- 3× Brick 2×3 (3002.dat)
- 3× Plate 2×6 (3795.dat)
- 2× Brick 1×6 (3009.dat)
- 2× Brick 1×8 (3008.dat)
- and the same unique decorative parts as in Pocket 1

**Positions and rotations** are copied from Pocket 1 — only part IDs were replaced. This means the overall "footprint" of the pile from above looks similar.

---

## Part Replacement Mapping: Pocket 1 → Pocket 2

| Pocket 1 | Part | Pocket 2 | Part |
|----------|------|----------|------|
| 3022.dat | Plate 2×2 | 3003.dat | Brick 2×2 |
| 3068b.dat | Tile 2×2 | 3010.dat | Brick 1×4 |
| 3023a.dat | Plate 1×2 | 3040b.dat | Slope 45° 2×1 |
| 3005.dat | Brick 1×1 | 3062b.dat | Brick 1×1 Round |
| 3001.dat | Brick 2×4 | 3002.dat | Brick 2×3 |
| 3020.dat | Plate 2×4 | 3795.dat | Plate 2×6 |
| 3710.dat | Plate 1×4 | 3009.dat | Brick 1×6 |
| 3460.dat | Plate 1×8 | 3008.dat | Brick 1×8 |

---

## Next Steps

- [ ] Open Pocket 2.io in Stud.io and verify the model renders correctly
- [ ] Confirm the top-down view looks like a believable pile of parts
- [ ] If needed — manually adjust positions/rotations of some parts
- [ ] Create Pocket 3, 4, etc. following the same scheme with different part sets
- [ ] Restore the original Pocket 1.io from git if it was corrupted

---

## Useful Commands

```bash
# Check Pocket 1.io history via git
git -C ~/Dev/BrickitStudio log --oneline Pockets/"Pocket 1.io"
git -C ~/Dev/BrickitStudio show HEAD:"Pockets/Pocket 1.io" > /tmp/pocket1_original.io

# Inspect parts in any .io file
python3 -c "
import zipfile; from collections import Counter
with zipfile.ZipFile('Pocket 1.io') as z:
    ldr = z.read('model.ldr').decode()
c = Counter(l.split()[14] for l in ldr.splitlines() if l.strip().startswith('1 '))
[print(f'{v}x {k}') for k,v in sorted(c.items(), key=lambda x:-x[1])]
"
```
