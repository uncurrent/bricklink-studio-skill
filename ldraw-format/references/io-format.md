# Stud.io .io File Format

## Overview

A `.io` file is a ZIP archive. Unzip to see its contents:

```
model.ldr         ← MAIN file — Studio renders from this
model.lxfml       ← XML metadata — Studio reads it, but 3D is driven by model.ldr
modelv2.ldr
model2.ldr
thumbnail.png
errorPartList.err
.info
```

**Critical:** Studio reads `model.ldr` for 3D rendering, NOT `model.lxfml`.
Editing only the LXFML will not change what is visible in the viewport.
Always edit `model.ldr`.

---

## Reading and Editing .io Files Programmatically

### Read

```python
import zipfile

with zipfile.ZipFile("model.io", 'r') as z:
    files = {name: z.read(name) for name in z.namelist()}

ldr = files['model.ldr'].decode('utf-8', errors='replace')
```

### Analyze Parts

```python
from collections import Counter

counts = Counter(
    line.split()[14]
    for line in ldr.splitlines()
    if line.strip().startswith("1 ")
)
for part, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{count}x {part}")
```

### Edit and Write

```python
REPLACEMENTS = {
    '3022.dat': '3003.dat',   # Plate 2x2 → Brick 2x2
    '3068b.dat': '3010.dat',  # Tile 2x2 → Brick 1x4
}

new_lines = []
for line in ldr.splitlines(keepends=True):
    if line.strip().startswith('1 '):
        for old, new in REPLACEMENTS.items():
            line = line.replace(old, new, 1)
    new_lines.append(line)

files['model.ldr'] = ''.join(new_lines).encode('utf-8')

with zipfile.ZipFile("model_new.io", 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        z.writestr(name, data)
```

**Important:** when creating a new ZIP, preserve ALL files from the original archive
(including `thumbnail.png`, `.info`, etc.) — otherwise Studio may refuse to open the file.

---

## Inspecting .io History via Git

```bash
# View commit history for a specific .io file
git log --oneline path/to/model.io

# Restore original version
git show HEAD:path/to/model.io > /tmp/original.io
```

---

## Known Behavior

- Studio **auto-saves** changes made via the UI without warning
- Undo (`Cmd+Z`) works but does not always roll back everything
- If the file appears corrupted after editing — restore from git
