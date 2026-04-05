# Algorithms — Knowledge Base

Computational methods for LEGO/LDraw modeling, conversion, and analysis.
Reference entries: A01–A04. See INDEX.md for access protocol.

---

## A01: Voxelization — 3D mesh to LEGO bricks

**Summary:** Convert any 3D mesh (STL/OBJ) into a discrete voxel grid, then map voxels to LEGO bricks.
**Source:** https://lego.bldesign.org/LSculpt/lambrecht_legovoxels.pdf
**Tags:** voxelization, STL, LDraw conversion, 3D mesh

### How it works

1. **Surface sampling** — cast rays through the mesh surface on a regular grid; record intersection points
2. **Flood-fill** — from each surface point, fill the enclosed interior volume with voxels
3. **Sub-voxel sampling** — sample at higher resolution than brick size to capture fine details accurately
4. **Brick mapping** — map each occupied voxel (or cluster) to the closest available LEGO brick shape
5. **Structural optimization** — optionally re-arrange bricks to maximize stud connections between layers

### Key parameters

| Parameter | Typical value | Effect |
|---|---|---|
| Voxel resolution | 1 LDU per stud (20 LDU) | Higher = more detail, more parts |
| Fill mode | surface-only vs. solid fill | Solid = heavier, more stable |
| Brick palette | 1×1, 1×2, 1×3, 1×4, 2×2, 2×4 | Wider palette = better fit |

### Performance

From Lambrecht et al.: 69,000 triangle mesh → LDraw output in under 500ms on 2015 hardware.

### Output

LDraw `.ldr` file, directly importable into Studio or any LDraw viewer.

---

## A02: Legolization — Stability Optimization

**Summary:** Layer-by-layer brick placement that maximizes stud connections between layers for structural stability.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (Legolization, 2015)
**Tags:** stability, structural, layer-by-layer, optimization

### Objectives

The Legolization algorithm optimizes simultaneously for:
- **Stability** — maximize stud-to-stud connections across layer boundaries
- **Aesthetics** — preserve visual fidelity to the source shape
- **Efficiency** — minimize total part count

### Approach

1. Slice the voxelized model into horizontal layers (one plate = 1/3 brick height)
2. For each layer: solve a 2D packing problem using available brick shapes
3. Evaluate connectivity score (how many studs overlap with adjacent layers)
4. Iterate placement to maximize that score while respecting brick geometry constraints
5. Export final arrangement as LDraw

### Practical implication for Studio

When building manually, apply the same principle: **offset brick joints between layers** (running bond / Flemish bond patterns) — never stack bricks with seams aligned vertically.

---

## A03: Assembly Sequence Planning — Graph Transformer

**Summary:** Represent a LEGO model as a part-connection graph, then find the optimal build order using a neural network.
**Source:** https://github.com/topics/bricklink (search "assembly sequence planning", 2022)
**Tags:** assembly sequence, build order, graph neural network, instructions

### Problem

Given a completed LEGO model (all parts placed), find the sequence of steps in which to attach parts such that:
- Each step is physically possible (no floating parts)
- The build is stable at each intermediate step
- The sequence is learnable / intuitive for a human builder

### Architecture

**Heterogeneous Graph Attention Network (HGAT)**:
- Nodes: individual LEGO parts
- Edges: stud connections between parts (type + orientation)
- Model predicts which part to add next at each step

### Practical implication for Instruction Maker

The algorithm's output informs how to structure steps: build outward from a stable base, attach large structural elements before small details, resolve symmetrical sections early.

---

## A04: Collision Detection for LDraw

**Summary:** Detect geometrically intersecting (overlapping) parts in an LDraw model.
**Source:** https://forums.ldraw.org/thread-23987.html
**Tags:** collision, geometry, validation, LDraw

### Challenge

LEGO parts have complex non-convex shapes (slopes, arches, technic beams). Exact collision detection requires:
- Decompose each part into **compound convex volumes** (convex hull approximations)
- Test all pairwise combinations — O(n²) worst case
- False positives common at stud connection points (overlap is intentional)

### Simplification strategies

1. **AABB first pass** — filter with axis-aligned bounding boxes before running exact tests
2. **Connection-point whitelist** — mark known-valid stud overlap regions as non-colliding
3. **Layer-wise check** — for regular builds, only check parts within the same layer and one layer above/below

### Studio's approach

Studio uses built-in collision detection (toggle: Ctrl+Alt+C). It is approximate — some overlapping geometry at stud connections is allowed by design. Disable for large models to improve performance (see `gui-navigation/references/performance.md`).
