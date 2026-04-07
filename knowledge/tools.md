# Tools — Knowledge Base

Software tools, libraries, and resources for LDraw/LEGO modeling and rendering.
Reference entries: T01–T05. See INDEX.md for access protocol.

---

## T01: LSculpt — STL to LDraw Converter

**Summary:** Open-source command-line tool that converts STL/OBJ 3D meshes into LDraw via voxelization.
**Source:** https://lego.bldesign.org/LSculpt/
**Tags:** STL, OBJ, conversion, voxelization, LDraw, CLI

### What it does

LSculpt implements the voxelization algorithm (see A01 in algorithms.md):
- Reads STL or OBJ mesh files
- Voxelizes the surface and/or volume
- Maps voxels to LEGO brick shapes
- Outputs `.ldr` file importable in Studio

### Key options

| Flag | Effect |
|---|---|
| `--scale` | Set brick size relative to mesh units |
| `--stud` | Use stud-top orientation (studs face up) |
| `--plate` | Use plate bricks for finer vertical detail |
| `--nofill` | Surface-only (hollow sculpture) |

### Workflow

```
LSculpt model.stl --scale 1.0 --plate -o output.ldr
# Open output.ldr in BrickLink Studio
```

### Limitations

- Part selection limited to basic bricks and plates
- No color mapping (all parts output in one color)
- Complex concave meshes may have fill artifacts

---

## T02: LDraw Standard

**Summary:** Open text-based format and parts library for LEGO CAD; the foundation for all LEGO modeling tools.
**Source:** https://ldraw.org
**Tags:** LDraw, standard, parts library, file format, specification

### Key resources

| Resource | URL | Contents |
|---|---|---|
| File format spec | https://www.ldraw.org/article/218.html | Line types 0–5, matrix format |
| Parts library | https://www.ldraw.org/parts/latest-parts.html | 18,000+ official parts as .dat files |
| Parts tracker | https://www.ldraw.org/parts/unofficial-parts.html | Community-submitted parts not yet official |
| Color reference | https://www.ldraw.org/article/547.html | Official color IDs and RGB values |

### File format summary

```
0 Comment or metadata
1 color x y z a b c d e f g h i partfile.dat   ← sub-file reference (part or submodel)
2 color x1 y1 z1 x2 y2 z2                       ← line
3 color x1 y1 z1 x2 y2 z2 x3 y3 z3             ← triangle
4 color x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4   ← quad
5 color x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4   ← optional line
```

1 LDU = 0.4mm real-world. 1 stud width = 20 LDU. 1 plate height = 8 LDU.

---

## T03: three.js LDraw Loader

**Summary:** JavaScript library for rendering LDraw models in the browser using three.js WebGL.
**Source:** https://threejs.org/examples/?q=ldraw#webgl_loader_ldraw
**GitHub:** https://github.com/nfriend/ldraw-visualizer (example implementation)
**Tags:** three.js, browser, rendering, JavaScript, WebGL, LDraw

### What it does

- Parses `.ldr` and `.mpd` files client-side
- Renders full 3D model with correct part geometry and colors
- Supports orbit controls, zoom, pan
- Parts library loaded from CDN or local

### Usage snippet

```javascript
import { LDrawLoader } from 'three/addons/loaders/LDrawLoader.js';

const loader = new LDrawLoader();
loader.setPartsLibraryPath('/ldraw/');
loader.load('model.ldr', (group) => {
  scene.add(group);
});
```

### Use cases

- Web-based LDraw viewers
- Building instruction websites
- Model preview tools
- Automated screenshot generation

---

## T04: Community Resources

**Summary:** Key online repositories of LDraw models, MOC instructions, and rendering guides.
**Source:** multiple
**Tags:** community, models, MOC, Rebrickable, BrickHub, OMR

### Resources

| Resource | URL | Contents |
|---|---|---|
| LDraw Official Model Repository (OMR) | https://omr.ldraw.org | 1,800+ official LEGO sets in LDraw format |
| BrickHub | https://brickhub.org | 500+ original MOC models with LDraw files |
| Rebrickable | https://rebrickable.com | 1M+ sets + MOCs; LDraw files; rendering guides |
| BrickLink Parts Catalog | https://www.bricklink.com/catalogTree.asp | Complete LEGO part database |
| Studio Help Center | https://studiohelp.bricklink.com | Official Studio documentation |

### Rebrickable Studio guide

Rebrickable has a detailed guide for creating building instructions in Studio:
https://rebrickable.com/help/studio-instructions/
Covers: step setup, page layout, callouts, buffer exchange, export.

---

## T05 — Parts Catalog (Local SQLite Database)
**Accesses:** 0
**Source:** Built in-house from Rebrickable data
**Location:** `projects/parts-catalog/`

Local SQLite database with ~70k LEGO parts, all colors, cross-system ID mapping (BrickLink ↔ LDraw ↔ LEGO Element ID), and rarity scoring. Built from Rebrickable CSV dumps + API enrichment.

Key tables: `parts`, `colors`, `elements`, `part_color_stats`, `rarity_scores`, `external_ids`.
Query with `query_catalog.py` or directly via SQL.

**Integration points:** BOM export enrichment, model generation part selection, coloring palette weighting.
