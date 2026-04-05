---
name: bricklink-studio/knowledge
description: >
  Hierarchical knowledge base: algorithms, tools, recognition, assembly planning,
  model generation, rendering/datasets, spatial reasoning, and collections.
  Always read INDEX.md first. Open domain files only when needed.
  Update access counters on every use. Promote hot items inline.
compatibility:
  any: true
last-updated: 2026-04-05
---

# Knowledge Base — Index

**Always read this file first.** Check ⚡ Hot before opening any domain file.
After using any entry: **increment its counter** in the Directory table.

---

## ⚡ Hot  (accessed 5+ times — inlined for instant access)

*No items promoted yet. Items promote automatically when counter reaches 5.*

---

## Directory

### 🔧 Algorithms  →  `algorithms.md`

| ID | Entry | Accesses |
|---|---|---|
| A01 | Voxelization: 3D mesh → LEGO bricks via voxel grid | 0 |
| A02 | Legolization: layer-by-layer stability optimization | 0 |
| A03 | Assembly Sequence Planning via Graph Transformer | 0 |
| A04 | Collision Detection for LDraw geometry | 0 |

### 🛠 Tools  →  `tools.md`

| ID | Entry | Accesses |
|---|---|---|
| T01 | LSculpt — STL→LDraw open-source voxel converter | 0 |
| T02 | LDraw standard: spec, parts library, community resources | 0 |
| T03 | three.js LDraw loader — browser-based 3D rendering | 0 |
| T04 | Community resources: BrickHub, Rebrickable, OMR | 0 |

### 🔍 Part Recognition  →  `part-recognition.md`

| ID | Entry | Accesses |
|---|---|---|
| REC01 | Brickognize — web app, 98.7% AP50, Mask R-CNN + ConvNeXt | 0 |
| REC02 | RebrickNet (Rebrickable) — production, 300+ parts + colors | 0 |
| REC03 | Hierarchical 2-step detection (2021) + 28-model comparison | 0 |
| REC04 | Mobile apps: Bricksee, Brickit, InstaBrick, Minifig Finder | 0 |
| REC05 | Synthetic data protocol: 20 real + renders → 98.7% AP50 | 0 |

### 🏗 Assembly Planning  →  `assembly-planning.md`

| ID | Entry | Accesses |
|---|---|---|
| ASM01 | Graph Transformer for Assembly Sequence Planning (2022) | 0 |
| ASM02 | Translating Visual LEGO Manual to Machine Plan (ECCV 2022) | 0 |
| ASM03 | Break and Make: structural understanding simulator (ECCV 2022) | 0 |
| ASM04 | Robotic LEGO Assembly from Human Demonstration (2023) | 0 |

### ⚙️ Model Generation  →  `model-generation.md`

| ID | Entry | Accesses |
|---|---|---|
| GEN01 | 3D-to-Lego: Python STL→LDraw voxelizer (open source) | 0 |
| GEN02 | LSculpt: oriented plates for better surface quality | 0 |
| GEN03 | Legolization (2015): formal stability-optimized generation | 0 |
| GEN04 | Architectural LEGO sculpture generation (2019) | 0 |
| GEN05 | Deep Generative Models of Graphs for LEGO (NeurIPS 2020) | 0 |
| GEN06 | Stable Diffusion: Lego Minifig XL + Brickheadz XL (2023) | 0 |

### 🎨 Datasets & Rendering  →  `datasets-rendering.md`

| ID | Entry | Accesses |
|---|---|---|
| RND01 | BrickRenderer (2023) — photorealistic LDraw part renders for ML | 0 |
| RND02 | Lego Renderer for ML (2020) — Python/Blender, RGB+depth+mask+normals | 0 |
| RND03 | BrickRegistration (2021) — multi-part 3D scenes + segmentation | 0 |
| RND04 | Brickognize synthetic dataset protocol | 0 |
| RND05 | Public LEGO datasets: Nature 2023, Roboflow, York University | 0 |

### 🧠 Spatial Reasoning  →  `spatial-reasoning.md`

| ID | Entry | Accesses |
|---|---|---|
| SR01 | SRM: Spatial Reasoning with Denoising Models (ICML 2025) | 0 |
| SR02 | SpaceTools / DIRL: VLM + tool-augmented spatial reasoning | 0 |
| SR03 | Lambrecht voxelization paper (69k tris → LDraw in <500ms) | 0 |
| SR04 | Awesome Spatial Intelligence in VLM (SpatialCoT, SpaRC, Sparkle) | 0 |
| SR05 | Awesome Multimodal Spatial Reasoning (survey + benchmarks) | 0 |

### 📚 Collections & Meta  →  `collections.md`

| ID | Entry | Accesses |
|---|---|---|
| COL01 | Awesome LEGO Machine Learning (primary entry point for ML) | 0 |
| COL02 | Awesome Spatial Intelligence in VLM (entry point) | 0 |
| COL03 | Awesome Multimodal Spatial Reasoning (entry point) | 0 |
| COL04 | Awesome LEGO — general tools, CAD, community | 0 |

---

## Routing Hints

| User asks about... | IDs to check first |
|---|---|
| Convert STL / 3D mesh to LEGO | A01, GEN01, GEN02 |
| Structural stability of a build | A02, GEN03 |
| Collision / part overlap | A04 |
| Build sequence / step ordering for instructions | A03, ASM01 |
| Reading/parsing a LEGO instruction PDF | ASM02 |
| Identify unknown part from photo | REC01, REC02, REC04 |
| Build a custom part classifier | REC03, REC05, RND01 |
| Generate training images / synthetic data | RND01, RND02, RND03 |
| Public LEGO image datasets | RND05 |
| View LDraw in browser | T03 |
| LDraw file format spec | T02 |
| AI-generated LEGO images (not LDraw) | GEN06 |
| Generative model for new LEGO designs | GEN05 |
| Robotic or automated LEGO assembly | ASM04 |
| ML + spatial reasoning, VLM capabilities | SR01, SR02, SR04 |
| What tools/papers exist for X? | COL01, then domain files |

---

## Protocol

### How to use

1. **Always read INDEX.md first**
2. Check ⚡ Hot — if the answer is there, use it and increment counter
3. If not in Hot — find the entry ID in Directory → open the domain file → read that entry
4. **After every use:** increment the Accesses counter for that entry (+1)
5. When an entry reaches **5 accesses**: paste its key facts (2–5 lines + source URL) inline into Hot

### Promotion rules

- Hot section maximum: **8 items**
- Format when promoting: `**[ID]** Entry title — key fact 1. Key fact 2. Source: URL`
- To demote: when Hot exceeds 8 items, remove the entry with the lowest counter (counter preserved in Directory)

### Adding new knowledge

- Decide which domain file fits (algorithms / tools / recognition / assembly / generation / rendering / spatial / collections)
- Assign the next available ID in that series
- Add the entry to the domain file with full Source URL
- Add a row to the appropriate Directory table in this INDEX
- Do NOT add to deprecated files (repos.md, research.md)
