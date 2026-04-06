---
name: bricklink-studio/model-generation
description: >
  Generate LDraw code for LEGO models from natural language descriptions.
  Use when user says: "create model", "write LDraw", "generate building/wall/car",
  "make LEGO construction", or equivalent in any language:
  "создай модель", "сгенерируй" (Russian), "crée un modèle", "génère une construction" (French),
  "erstelle ein Modell", "baue eine Konstruktion" (German), "crea un modelo", "genera construcción" (Spanish),
  "モデルを作って", "レゴを生成して" (Japanese), "创建模型", "生成积木" (Chinese).
  Works in all environments. Output is valid .ldr file content.
compatibility:
  any: true
---

# Model Generation — Sub-skill

> **Language policy:** All entries written to skill files during this session must be in English.
> The user interface may be in any language.


Generate valid LDraw `.ldr` files from natural language descriptions.
Always read `ldraw-format/guide.md` first for syntax reference.

---

## Generation Process

1. **Understand the request** — shape, size, color, style (city / technic / fantasy / etc.)
2. **Choose a scale** — how many studs wide/deep/tall
3. **Plan the structure** — identify major components (base, walls, roof, etc.)
4. **Generate layer by layer** — bottom to top, front to back
5. **Output LDraw** — valid file with header + part lines
6. **Summarize** — tell user what was built and part count

---

## LDraw File Template

```
0 <Model Name>
0 Name: model.ldr
0 Author: Claude
0 !LEGOCOM BrickLink Studio 2.0
0

1 <color> <x> <y> <z> 1 0 0 0 1 0 0 0 1 <part>.dat
1 <color> <x> <y> <z> 1 0 0 0 1 0 0 0 1 <part>.dat
...
```

Identity rotation matrix: `1 0 0 0 1 0 0 0 1`

---

## Coordinate System

- **X** = left/right (positive = right)
- **Y** = up/down (**negative = up** — LDraw is inverted!)
- **Z** = front/back (positive = toward viewer)
- Origin `0 0 0` = center of model, ground level

**Critical:** in LDraw, Y increases downward. To go UP, subtract from Y.

| To move | Change |
|---|---|
| 1 stud right | X + 20 |
| 1 stud forward | Z + 20 |
| 1 plate up | Y - 8 |
| 1 brick up | Y - 24 |

---

## Common Color IDs

| ID | Color |
|---|---|
| 0 | Black |
| 1 | Blue |
| 2 | Green |
| 4 | Red |
| 5 | Dark Pink |
| 6 | Brown |
| 7 | Light Gray |
| 10 | Bright Green |
| 14 | Yellow |
| 15 | White |
| 19 | Tan |
| 28 | Dark Tan |
| 71 | Light Bluish Gray |
| 72 | Dark Bluish Gray |
| 25 | Orange |
| 26 | Magenta |

Full color table: `bom-export/references/color-ids.md`

---

## Generation Patterns

### Flat Row of Bricks (N bricks wide, color C, part P, at height Y)
```
# 2x4 bricks (3001), spacing = 40 LDU (2 studs × 20)
1 C 0    Y 0 1 0 0 0 1 0 0 0 1 P.dat
1 C 40   Y 0 1 0 0 0 1 0 0 0 1 P.dat
1 C 80   Y 0 1 0 0 0 1 0 0 0 1 P.dat
```

### Staggered Wall (offset every other row by half brick)
```
# Row 1 (Y=0):   bricks at X = 0, 40, 80...
# Row 2 (Y=-24): bricks at X = 20, 60, 100... (offset by 20 = half 2-stud spacing)
```

### Rotation 90° around Y axis
Replace identity matrix `1 0 0 0 1 0 0 0 1` with `0 0 1 0 1 0 -1 0 0`

### Rotation 180° around Y axis
Matrix: `-1 0 0 0 1 0 0 -1 0 0 0 1` → use `-1 0 0 0 1 0 0 0 -1`

---

## Example: Simple 4×4 Brick House (starter)

```
0 Simple House
0 Name: house.ldr
0 Author: Claude
0

0 // Floor (4x4 baseplate)
1 71 0 0 0 1 0 0 0 1 0 0 0 1 3031.dat

0 // Wall row 1
1 4 -30 -24 -30 1 0 0 0 1 0 0 0 1 3001.dat
1 4  10 -24 -30 1 0 0 0 1 0 0 0 1 3001.dat
1 4 -30 -24  30 1 0 0 0 1 0 0 0 1 3001.dat
1 4  10 -24  30 1 0 0 0 1 0 0 0 1 3001.dat
```

---

## Quality Checks Before Outputting

- [ ] Header present (0 Name, 0 Author)
- [ ] All Y coordinates use correct sign (up = negative)
- [ ] Rotation matrices are valid (each row is unit vector, orthogonal)
- [ ] Part IDs exist in `common-parts.md` or are standard LDraw IDs
- [ ] Parts are aligned to stud grid (X and Z multiples of 20, Y multiples of 8)

---

## Reference Files

- `references/patterns.md` — Ready-made patterns: walls, arches, Technic frames, roofs

---

## See Also

- Model generation scripts: `projects/*/scripts/` (automation and batch processing)
- Recipes using model generation: `projects/*/recipes/` and `recipes/`
- Before generating new patterns, check `references/patterns.md` and existing scripts first
