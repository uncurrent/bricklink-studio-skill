# Datasets & Rendering — Knowledge Base

Tools and methods for generating synthetic LEGO training data, rendering pipelines,
and available datasets for ML projects.
Reference entries: RND01–RND05. See INDEX.md for access protocol.

---

## RND01: BrickRenderer (2023)

**Summary:** Tool that renders photorealistic training images of LDraw parts — designed specifically
for generating ML training data at scale.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2023.06 entry)
**Tags:** rendering, synthetic data, LDraw, training data, ML pipeline

### What it generates

- Individual part renders: multiple angles, lighting conditions, backgrounds
- Output: RGB images + bounding box annotations + segmentation masks
- Scale: designed for processing thousands of parts in batch

### Use case

Build a custom part recognition model for parts not yet covered by Brickognize or RebrickNet.
Feed BrickRenderer output directly into a classifier training pipeline.

---

## RND02: Lego Renderer for ML Projects (2020)

**Summary:** Python scripts + Blender utilities for rendering LEGO scenes for deep learning /
computer vision projects.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2020.01 entry)
**Tags:** Python, Blender, rendering, normals, masks, depth, synthetic data

### Outputs per render

| Channel | Description |
|---|---|
| RGB image | Photorealistic color render |
| Depth map | Per-pixel distance from camera |
| Normal map | Per-pixel surface orientation |
| Segmentation mask | Per-part color-coded mask |

### Why useful

Multi-channel output enables training not just classifiers but also depth estimators,
pose estimators, and segmentation models — all from a single rendering pass.

### Workflow

```python
# Blender Python API example (conceptual)
import bpy
load_ldraw_model("part_3001.ldr")
set_random_background()
set_random_lighting()
render_all_channels(output_dir="./data/3001/")
```

---

## RND03: BrickRegistration — 3D Scene Generator with Segmentation (2021)

**Summary:** Tool for generating synthetic 3D scenes containing multiple LEGO parts with automatic
segmentation information included.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (2021.11 entry)
**Tags:** 3D scenes, segmentation, multi-part, synthetic, registration

### Distinction from single-part renders

Generates scenes with **multiple parts** in realistic arrangements — random piles,
stacked configurations, parts on surfaces. Includes instance segmentation masks,
which is essential for training object detectors.

### Use case

Training a detector that handles messy piles of bricks (like Brickit's pile-scanning feature).

---

## RND04: Brickognize Synthetic Dataset Method

**Summary:** Protocol for creating labeled training data using ~20 real photos per class +
large synthetic renders. Achieves near-real performance.
**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9967933/
**Tags:** training protocol, few-shot, synthetic, real images, fine-tuning

See also: part-recognition.md REC05 for full details on the method.

**Key numbers:**
- 20 real images + synthetic renders → **98.7% AP50**
- Purely synthetic → **91.33% AP50**

### Dataset structure recommendation

```
data/
├── part_3001/          # Brick 2×4
│   ├── real/           # 20 real photos
│   └── synthetic/      # N renders from BrickRenderer
├── part_3004/          # Brick 1×2
│   ├── real/
│   └── synthetic/
...
```

---

## RND05: Available LEGO Datasets (Public)

**Summary:** Publicly available labeled datasets of LEGO bricks for training and benchmarking.
**Tags:** dataset, public, classification, detection, benchmark

| Dataset | Contents | Source |
|---|---|---|
| LEGO Brick renders | ~1.5M renders of individual parts | https://data.nvision2.eecs.yorku.ca/LegoDataset/ |
| Photos + renders combined | ~155k photos + ~1.5M renders | Scientific Data (Nature), 2023 |
| Roboflow LEGO detection | Annotated detection dataset | https://universe.roboflow.com/autodash/lego-bricks-uwgtj |
| LegoBrickClassification | Synthetic dataset, 15 parts | https://github.com/korra-pickell/LEGO-Classification-Dataset |

### Nature dataset (2023)

Photos and rendered images of LEGO bricks, published in Scientific Data:
https://www.nature.com/articles/s41597-023-02682-2
Largest public LEGO image dataset as of 2024.
