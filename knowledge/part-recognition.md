# Part Recognition — Knowledge Base

Tools and research for identifying LEGO parts from photos using machine learning.
Reference entries: REC01–REC05. See INDEX.md for access protocol.

Practical use: when a user has an unknown part or wants to automate part identification
from images, these tools and methods are the starting point.

---

## REC01: Brickognize — Web App (Production)

**Summary:** Web app that recognizes any LEGO part, minifigure, or set from a photo. Uses synthetic
training data (photo-realistic renders) combined with few-shot real images.
**Source:** https://www.tramacsoft.com/brickognize
**Paper:** https://www.mdpi.com/1424-8220/23/4/1898 (Sensors 2023)
**Tags:** web app, recognition, Mask R-CNN, ConvNeXt, synthetic data

### Technical approach

- Model: **ConvNeXt-T** for classification; **Mask R-CNN** for detection
- Training data: ~20 real-world images per class + large volume of photo-realistic renders
- Results: **98.7% AP50** (controlled environment), **91.33% AP50** (uncontrolled)
- Covers: 76+ distinct parts, full minifigures and sets

### Key insight

Synthetic data (renders from LDraw models) can substitute for real labeled images,
dramatically reducing data collection cost. This is directly applicable to custom part classifiers.

### Planned features

- Multi-brick detection in a single image
- Export recognized parts directly to BrickLink Wanted List

---

## REC02: RebrickNet — Rebrickable Part Detector (Production)

**Summary:** Production part detection system integrated into Rebrickable.com. Identifies 300+ parts.
**Source:** https://rebrickable.com/rebricknet/
**Tags:** web app, production, rebrickable, part detection, color recognition

### Capabilities

- Detects and recognizes 300+ different LEGO part types
- Identifies colors in addition to part shapes
- Integrated into Rebrickable's web interface — no local install needed

### Use case

Fastest practical option for identifying an unknown part: go to rebrickable.com/rebricknet,
upload a photo, get the BrickLink/LDraw part ID directly.

---

## REC03: Hierarchical 2-Step Detection (Research, 2021)

**Summary:** Two-stage neural pipeline: first detect all bricks in the scene, then classify each one.
**Source:** https://github.com/360er0/awesome-lego-machine-learning (see 2021.04 entry)
**Paper:** Hierarchical 2-step neural-based LEGO bricks detection and labeling (2021)
**Tags:** detection, classification, two-stage, research

### Architecture

1. **Stage 1 (Detection):** Object detector locates all bricks in the image (bounding boxes)
2. **Stage 2 (Classification):** Classifier identifies the exact part ID per bounding box

### Why two stages

Single-stage classifiers struggle when multiple bricks are present in one image.
Two-stage approach handles cluttered scenes and stacked bricks much better.

### Comparison

Network for LEGO bricks classification (2022.07): benchmarks **28 different model architectures**
trained to recognize **447 LEGO parts** — useful reference if building a custom classifier.
Source: https://github.com/360er0/awesome-lego-machine-learning

---

## REC04: Mobile Apps for Part Recognition

**Summary:** Consumer mobile apps with real-time LEGO part recognition via phone camera.
**Tags:** mobile, iOS, Android, real-time, consumer

| App | Platform | Capability | URL |
|---|---|---|---|
| **Bricksee** | iOS/Android | Collection organizer + photo detection | — |
| **BrickMonkey** | iOS/Android | Minifig + part recognition | — |
| **Brickit** | iOS/Android | Detects parts in a pile, suggests builds | brickit.app |
| **InstaBrick** | iOS/Android | Part identification from photo | — |
| **Minifig Finder** | Web | Minifig identification via Mask R-CNN | — |

### Practical note

For identifying a single unknown part from a photo: **RebrickNet** (REC02) or **Brickognize** (REC01)
are most accurate. Mobile apps are convenient for scanning collections in bulk.

---

## REC05: Synthetic Dataset Generation for Recognition

**Summary:** Generating labeled training images from LDraw renders instead of photographing real bricks.
**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9967933/ (Brickognize paper, Section 3)
**Tags:** synthetic data, dataset, Blender, rendering, training data

### Method

1. Load LDraw part file into Blender
2. Randomize: background texture, lighting direction/intensity, camera angle, surface color
3. Render N images per part → automatic bounding box + mask annotations
4. Mix with small number of real images (20 per class) for fine-tuning

### Results from Brickognize

- Purely synthetic training → 91% AP50 on uncontrolled real images
- Synthetic + 20 real images → 98.7% AP50
- Conclusion: synthetic renders are an effective substitute for large labeled real datasets

### Tooling

See `datasets-rendering.md` for rendering pipeline tools (BrickRenderer, Lego Renderer for ML).
