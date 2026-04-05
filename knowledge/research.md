# DEPRECATED — Research

> This file has been superseded by spatial-reasoning.md (SR01–SR05).
> Do not add new entries here. Add to spatial-reasoning.md instead.

---

# Research — Knowledge Base (ARCHIVED)

Academic papers and ML frameworks relevant to spatial reasoning and LEGO modeling.
Reference entries: S01–S03. See INDEX.md for access protocol.

---

## S01: SRM — Spatial Reasoning with Denoising Models (ICML 2025)

**Summary:** Framework for spatial reasoning over continuous variables using score-based generative models.
**Source:** https://github.com/Chrixtar/SRM
**Paper:** ICML 2025
**Tags:** spatial reasoning, denoising models, score-based, continuous variables, ICML

### What it does

- Models spatial reasoning tasks as inference over continuous spatial variables
- Uses denoising diffusion / score-matching to iteratively refine spatial predictions
- Generalizes across: 3D object placement, spatial relationship prediction, scene generation

### Architecture

- Input: partial scene description (object types + some positions)
- Output: full distribution over remaining spatial variables
- Training: denoising score matching on spatial configurations

### Relevance to LEGO

Directly applicable to the problem of "where should this part go?" given a partial model. Potential foundation for a neural model-generation approach that predicts plausible part placements.

---

## S02: SpaceTools — Tool-Augmented Spatial Reasoning

**Summary:** VLM augmented with external spatial tools (depth, segmentation, pose) trained via reinforcement learning.
**Source:** https://spacetools.github.io/
**Tags:** VLM, spatial reasoning, tool use, reinforcement learning, DIRL

### Algorithm: Double Interactive Reinforcement Learning (DIRL)

1. VLM receives spatial query + image
2. VLM selects which tool to invoke: depth estimator / segmentation / 6DoF pose estimator
3. Tool runs and returns spatial annotation back to VLM
4. VLM incorporates tool output, repeats if needed, produces final answer
5. DIRL trains: tool selection policy + answer quality jointly via RL reward

### Results

State-of-the-art on multiple spatial reasoning benchmarks (2024–2025) — outperforms chain-of-thought alone.

### Relevance to LEGO

- The "tool use" paradigm is analogous to how Claude interacts with Studio GUI
- Depth estimation ≈ understanding 3D layout from screenshots
- Pose estimation ≈ understanding part orientation from Studio viewport

---

## S03: Lambrecht Voxelization Paper

**Summary:** Foundational paper on converting boundary-representation 3D models to oriented LEGO plate structures.
**Source:** https://lego.bldesign.org/LSculpt/lambrecht_legovoxels.pdf
**Authors:** Lambrecht et al.
**Tags:** voxelization, LDraw, STL, boundary representation, plates, performance

### Key result

69,000 triangle mesh → complete LDraw output in under 500ms (2015 hardware).

### Contribution

- Formalizes the voxelization pipeline for LEGO specifically
- Addresses oriented plates (not just horizontal layers) for better surface detail
- Provides error metrics for evaluating reconstruction fidelity

### Algorithm (condensed)

1. Rasterize input mesh to voxel grid at target resolution
2. Classify voxels: exterior / surface / interior
3. For surface voxels: determine dominant face orientation → assign oriented plate
4. For interior voxels: assign standard brick (1×1 or larger)
5. Apply brick merging to reduce part count (1×1 → 1×2 → 1×4 etc.)
6. Export as LDraw type-1 lines

### Practical notes

- Plate bricks (1/3 height) give 3× vertical resolution compared to standard bricks
- Oriented plates (slope bricks, wedges) dramatically improve surface quality
- The merging step is a 2D rectangle packing problem per layer
