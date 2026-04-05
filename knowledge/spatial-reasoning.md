# Spatial Reasoning — Knowledge Base

ML frameworks, papers, and curated collections on spatial reasoning in AI systems —
especially those applicable to 3D LEGO modeling and part placement.
Reference entries: SR01–SR05. See INDEX.md for access protocol.

---

## SR01: SRM — Spatial Reasoning with Denoising Models (ICML 2025)

**Summary:** Framework for reasoning over continuous spatial variables using score-based generative
models (denoising diffusion). Solves: "given a partial scene, where should the remaining
objects go?"
**Source:** https://github.com/Chrixtar/SRM
**Paper:** ICML 2025
**Tags:** denoising diffusion, continuous spatial variables, scene completion, ICML

### Architecture

- Input: partial spatial configuration (some objects placed, some missing)
- Model: denoising score function over joint distribution of all spatial variables
- Output: full distribution → sample valid completions
- Training: score matching on spatial configurations from a dataset

### Application to LEGO

Directly maps to: "given a partially built model, where should the next part go?"
A potential foundation for a learned model-generation sub-skill that predicts
plausible part placements rather than requiring explicit LDraw coordinates.

---

## SR02: SpaceTools — Tool-Augmented Spatial Reasoning (2024)

**Summary:** VLM augmented with external spatial perception tools (depth, segmentation, pose
estimation) and trained via reinforcement learning to select which tool to invoke.
**Source:** https://spacetools.github.io/
**Algorithm:** Double Interactive Reinforcement Learning (DIRL)
**Tags:** VLM, tool use, depth estimation, segmentation, pose, reinforcement learning

### DIRL algorithm

1. VLM receives spatial query + image
2. VLM selects which tool to call: depth estimator / segmentation / 6DoF pose estimator
3. Tool returns spatial annotation → VLM incorporates it
4. Repeat as needed (multi-turn tool use)
5. Final spatial answer produced

### State of the art

Outperforms chain-of-thought prompting alone on multiple 2024–2025 spatial reasoning
benchmarks. Key insight: spatial tasks benefit from external perception tools, not
just language reasoning.

### Parallel to Claude + Studio

Claude using BrickLink Studio GUI tools = VLM using SpaceTools' spatial perception tools.
Screenshots → spatial understanding of the 3D scene.

---

## SR03: Lambrecht Voxelization Paper

**Summary:** Foundational academic treatment of converting boundary-representation 3D meshes to
oriented LEGO plate structures.
**Source:** https://lego.bldesign.org/LSculpt/lambrecht_legovoxels.pdf
**Tags:** voxelization, LDraw, boundary representation, plates, performance, academic

### Key result

69,000 triangle mesh → LDraw in under 500ms (2015 hardware).

**See also:** algorithms.md A01 for full voxelization algorithm details.

---

## SR04: Awesome Spatial Intelligence in VLM

**Summary:** Curated paper list tracking spatial reasoning capabilities in Vision-Language Models.
**Source:** https://github.com/mll-lab-nu/Awesome-Spatial-Intelligence-in-VLM
**Tags:** VLM, spatial reasoning, survey, curated list, multimodal

### Notable entries in the list

| Paper | What it solves |
|---|---|
| SpatialCoT | Chain-of-thought reasoning for spatial queries |
| SpatialPIN | Spatial reasoning via precise location pinpointing |
| SpaRC | Spatial relationship comprehension benchmark |
| Sparkle | Structured spatial reasoning with intermediate states |

### Relevance

Benchmark suite for evaluating how well a model (including Claude) handles
3D spatial questions — useful for assessing model-generation sub-skill quality.

---

## SR05: Awesome Multimodal Spatial Reasoning

**Summary:** Survey of spatial reasoning across all modalities and task types: 2D/3D, navigation,
VQA, embodied AI, manipulation.
**Source:** https://github.com/zhengxuJosh/Awesome-Multimodal-Spatial-Reasoning
**Tags:** survey, multimodal, 3D, navigation, embodied AI, benchmark, arXiv

### Scope by domain

| Domain | What's covered |
|---|---|
| 2D spatial | Image-based QA, referring expressions, relation detection |
| 3D scene | Point clouds, depth estimation, 3D object detection |
| Navigation | Embodied AI path planning, instruction following |
| Manipulation | Robot grasping, assembly (connects to assembly-planning.md) |

Includes a survey paper on arXiv and standardized benchmarks for cross-system comparison.
