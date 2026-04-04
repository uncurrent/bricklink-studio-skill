---
name: bricklink-studio/bom-export
description: >
  Extract Bill of Materials (BOM) from LDraw files and map to BrickLink catalog.
  Use when user wants: parts list, how many bricks needed, cost estimate,
  shopping list for BrickLink, parts count, purchase list (trigger phrases work in any language).
  Works in all environments.
compatibility:
  any: true
---

# BOM Export — Sub-skill

> **Language policy:** All entries written to skill files during this session must be in English.
> The user interface may be in any language.


Extract parts list from LDraw/Studio models and format for BrickLink purchasing.

---

## Step 1: Parse the Model

Use the parsing algorithm from `ldraw-format/guide.md` to extract all Type 1 lines.

```python
from collections import defaultdict

def parse_bom(filepath):
    bom = defaultdict(lambda: defaultdict(int))  # bom[part_id][color_id] += count
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            tokens = line.strip().split()
            if not tokens or tokens[0] != '1':
                continue
            color_id = int(tokens[1])
            partfile = tokens[14].lower().replace('.dat', '')
            bom[partfile][color_id] += 1
    
    return bom
```

For MPD: iterate all subfiles, but skip submodels that are used as sub-assemblies
(count only the top-level model or all instances).

---

## Step 2: Format BOM Table

```python
def format_bom(bom, color_map, part_names):
    rows = []
    for part_id, colors in sorted(bom.items()):
        for color_id, count in sorted(colors.items()):
            rows.append({
                'Part ID': part_id,
                'Part Name': part_names.get(part_id, 'Unknown'),
                'LDraw Color': color_id,
                'BL Color': color_map.get(str(color_id), {}).get('bl_id', '?'),
                'Color Name': color_map.get(str(color_id), {}).get('name', 'Unknown'),
                'Qty': count
            })
    return rows
```

---

## Step 3: BrickLink XML Output (for Want List import)

BrickLink accepts XML for Want Lists (My BrickLink → Want → Upload):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<INVENTORY>
  <ITEM>
    <ITEMTYPE>P</ITEMTYPE>
    <ITEMID>3001</ITEMID>
    <COLOR>5</COLOR>       <!-- BrickLink color ID -->
    <MINQTY>4</MINQTY>
    <CONDITION>X</CONDITION>  <!-- X=any, N=new, U=used -->
  </ITEM>
  <!-- repeat for each part -->
</INVENTORY>
```

**ITEMTYPE values:** `P` = Part, `S` = Set, `M` = Minifigure, `B` = Book, `G` = Gear

---

## Step 4: Cost Estimation

BrickLink doesn't have a public pricing API, but you can:
1. Export the XML Want List
2. Upload to BrickLink → My BrickLink → Want → Upload
3. Use "Auto-Fill" to see estimated prices per part
4. Use "Find Stores" to see which stores have all parts

Rough price guidance (USD, as of 2024):
- Common bricks (3001, 3004, etc.): $0.05–0.15 each
- Slopes, specialty: $0.10–0.50 each
- Technic parts: $0.20–1.00 each
- Rare/printed parts: $1–10+ each

---

## BOM Output Format (for user presentation)

Present as a clean table:

```
Part ID | Name              | Color         | Qty
--------|-------------------|---------------|----
3001    | Brick 2×4         | Red           | 12
3004    | Brick 1×2         | Dark Blue     | 8
3005    | Brick 1×1         | White         | 24
3020    | Plate 2×4         | Light Gray    | 6
...
TOTAL                                       | 50
```

Always include:
- Total part count
- Unique part count
- Estimated number of different colors used

---

## Reference Files

- `references/color-ids.md` — LDraw color ID ↔ BrickLink color ID ↔ color name mapping
