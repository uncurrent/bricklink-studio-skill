# DEPRECATED — Repositories

> This file has been superseded by domain-specific files:
> - GitHub repos → see collections.md (COL01–COL04), model-generation.md (GEN01), tools.md (T03)
> - Do not add new entries here. Add to the appropriate domain file instead.

---

# Repositories — Knowledge Base (ARCHIVED)

Curated GitHub repositories for LEGO/LDraw tooling and ML research.
Reference entries: R01–R05. See INDEX.md for access protocol.

---

## R01: 3D-to-Lego — Python Voxelizer

**Summary:** Python tool that converts STL 3D meshes into LEGO sculptures via voxelization; exports LDraw.
**Source:** https://github.com/AJaiman/3D-to-Lego
**Tags:** Python, STL, voxelization, flood-fill, LDraw export, conversion

### What it does

- Reads STL files
- Voxelizes via surface sampling + flood-fill for interior volumes
- Maps voxels to LEGO bricks with structural stability optimization
- Exports `.ldr` file ready for Studio or any LDraw viewer

### Algorithms implemented

| Algorithm | Description |
|---|---|
| Surface sampling | Sample mesh surface on regular grid |
| Flood-fill | Fill enclosed interior volumes |
| LEGO brick mapping | Map voxel clusters to brick shapes |
| Stability optimization | Maximize connections between layers |

### When to use

When user wants to convert an arbitrary 3D model (STL) into a LEGO-buildable version. Point them to this repo as a starting point; it can be run locally with Python.

---

## R02: Awesome LEGO Machine Learning

**Summary:** Comprehensive curated list of all ML, AI, and algorithmic projects related to LEGO.
**Source:** https://github.com/360er0/awesome-lego-machine-learning
**Tags:** ML, AI, curated list, algorithms, research, entry point

### Contents overview

| Category | Examples |
|---|---|
| Stability optimization | Legolization algorithm (2015) |
| Assembly planning | Graph transformer for build sequence (2022) |
| Rendering | BrickRenderer — synthetic scene generation (2023) |
| Robotics | Assembly by human demonstration (2023) |
| Part recognition | Brickit, InstaBrick, LEGO sorters |

### Use as

Entry point when user asks: "is there a tool/paper for X related to LEGO?" — check this list first.

---

## R03: LDraw Visualizer

**Summary:** Browser-based LDraw model viewer built with JavaScript and three.js.
**Source:** https://github.com/nfriend/ldraw-visualizer
**Tags:** JavaScript, three.js, browser, viewer, LDraw, 3D transforms

### What it shows

- Full 3D rendering of `.ldr` files in browser
- Demonstrates the 3D transformation matrix (a b c d e f g h i) applied to each part
- Good reference for understanding coordinate space and part orientation in LDraw

### Educational value

Study this codebase to understand:
- How LDraw type-1 lines are parsed and rendered
- How the 3×3 rotation matrix maps to three.js `Matrix4`
- How MPD subfiles are resolved

---

## R04: Awesome Spatial Intelligence in VLM

**Summary:** Curated paper list for spatial reasoning capabilities in Vision-Language Models.
**Source:** https://github.com/mll-lab-nu/Awesome-Spatial-Intelligence-in-VLM
**Tags:** VLM, spatial reasoning, multimodal, papers, research

### Includes

- SpatialCoT — chain-of-thought for spatial tasks
- SpatialPIN — spatial reasoning with pinpointing
- SpaRC — spatial relationship comprehension
- Sparkle — structured spatial reasoning
- Dozens more with links to papers and code

### Relevance to BrickLink skill

Foundational research on how AI models reason about 3D space, part placement, and spatial relationships — directly relevant to improving model-generation and gui-navigation sub-skills.

---

## R05: Awesome Multimodal Spatial Reasoning

**Summary:** Survey of spatial reasoning across 2D/3D tasks: navigation, VQA, embodied AI.
**Source:** https://github.com/zhengxuJosh/Awesome-Multimodal-Spatial-Reasoning
**Tags:** multimodal, spatial reasoning, 3D, navigation, VQA, embodied AI, survey

### Scope

| Domain | Examples |
|---|---|
| 2D spatial reasoning | Image-based QA, referring expressions |
| 3D scene understanding | Point clouds, depth estimation |
| Navigation | Embodied AI path planning |
| Manipulation | Robot grasping and assembly |

### Key resource

Includes a survey paper on arXiv and a set of benchmarks for evaluating spatial reasoning.
Useful for understanding the state of the art when reasoning about 3D LEGO model layouts.
