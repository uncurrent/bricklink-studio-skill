# Model Generation — Knowledge Base

Tools, algorithms, and research for generating LEGO models — from 3D mesh conversion
to AI-driven generation of new builds.
Reference entries: GEN01–GEN06. See INDEX.md for access protocol.

---

## GEN01: 3D-to-Lego — Python Voxelizer

**Summary:** Python tool that converts STL meshes into LEGO sculptures via voxelization + flood-fill.
Exports LDraw directly importable in Studio.
**Source:** https://github.com/AJaiman/3D-to-Lego
**Tags:** Python, STL, voxelization, flood-fill, LDraw, open source

### Pipeline

1. Load STL mesh
2. Surface sampling on regular grid (configurable resolution)
3. Flood-fill interior volumes
4. Map voxels → LEGO bricks (1×1, 1×2, 2×2, 2×4)
5. Stability optimization: maximize stud connections between layers
6. Export as `.ldr`

### Usage

```bash
git clone https://github.com/AJaiman/3D-to-Lego
cd 3D-to-Lego
pip install -r requirements.txt
python convert.py model.stl --output model.ldr
```

---

## GEN02: LSculpt — STL→LDraw CLI Converter

**Summary:** Established open-source command-line tool for STL/OBJ → LDraw via voxelization.
**Source:** https://lego.bldesign.org/LSculpt/
**Tags:** CLI, STL, OBJ, LDraw, voxelization, open source
**See also:** tools.md T01 for full details.

Key advantage over GEN01: supports **oriented plates** (slopes, wedges) for much better
surface quality on curved forms.

---

## GEN03: Legolization — Stability-Optimized Generation (2015)

**Summary:** Academic algorithm that converts 3D models to LEGO with explicit optimization for
physical structural stability.
**Source:** SIGGRAPH Asia 2015; see also algorithms.md A02 for full algorithm details.
**Tags:** stability, layer-by-layer, optimization, structural

The original formal treatment of voxel→LEGO conversion with quantitative stability metrics.
LSculpt and 3D-to-Lego are practical implementations of similar ideas.

---

## GEN04: Automatic Generation of Vivid LEGO Architectural Sculptures (2019)

**Summary:** System specifically for converting architectural 3D models (buildings, structures) into
LEGO sculptures with aesthetic and structural optimization.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2019 entry)
**Tags:** architecture, sculpture, generation, aesthetics

### Specialization over generic voxelization

- Preserves architectural details: windows, cornices, facades
- Handles thin walls and overhangs that pure voxelization misses
- Optimizes for visual fidelity from specific viewing angles

---

## GEN05: Building LEGO with Deep Generative Models of Graphs (2020)

**Summary:** Neural network that learns to generate new LEGO models step by step, represented as
growing graphs of part connections.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2020.12 entry)
**Paper:** Building LEGO Using Deep Generative Models of Graphs (NeurIPS 2020 workshop)
**Tags:** generative model, graph neural network, step-by-step generation, novel models

### How it works

1. Encode LEGO models as graphs (nodes = parts, edges = connections)
2. Train a graph variational autoencoder (GVAE) on a dataset of models
3. At generation time: sample from latent space → decode step by step (add one part at a time)
4. Constraint enforcement: only valid connections allowed at each step

### Significance

First neural approach to generating entirely new, buildable LEGO models — not converting
from 3D geometry, but inventing new designs from a learned distribution.

---

## GEN06: Stable Diffusion Models for LEGO Image Generation (2023)

**Summary:** Fine-tuned Stable Diffusion checkpoints for generating photorealistic LEGO minifigures
and Brickheadz from text prompts.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2023.08, 2023.09 entries)
**Tags:** Stable Diffusion, image generation, minifig, Brickheadz, text-to-image

| Model | Subject | Release |
|---|---|---|
| Lego Minifig XL | LEGO minifigures | 2023.08 |
| Lego Brickheadz XL | LEGO Brickheadz figures | 2023.09 |

### Practical use

Generate reference images for custom minifig or Brickheadz designs before building
them in Studio. Use the generated image as a visual target.

Not for generating LDraw models — output is images only, not buildable files.
