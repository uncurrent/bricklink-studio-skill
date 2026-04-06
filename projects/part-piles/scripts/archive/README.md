# Archive — Historical Per-Pocket Generator Scripts

This folder contains the per-pocket generator scripts that were written during the development
of Pockets 6–14. They are **not meant to be run directly** — each script is hard-coded to its
pocket's specific parameters and seed range.

Their purpose is **reference**: to understand how Recipe 1 (v0→v3) and Recipe 2 (v1→v4) evolved,
what was tried at each step, and why the production scripts look the way they do.

For production generation use the scripts in `../recipe-1/` and `../recipe-2/`.

---

## Algorithm Evolution Timeline

### Recipe 1 — Gaussian Rejection Sampling

| Script | Pocket | Algorithm | Key milestone |
|--------|--------|-----------|---------------|
| `gen_pocket6.py` | P6 | v3 | **v3 debut** — rotation-aware AABB collision, multi-seed selection (seeds 42–61). Reduced forced overlap from 25% to 8%. |
| `gen_pocket9.py` | P9 | v3+ | Two-layer experiment: 19 floor plates (uniform-in-ellipse) + 46 pile parts (Gaussian). Achieved exact Z footprint match (13.2 studs) but 9% forced — worse than P8. Proved single-Gaussian is better for flat piles. |
| `gen_pocket10.py` | P10 | v3+ | Returned to P8 single-Gaussian approach with SIGMA_Z reduced from 36 to 33. 200 seeds searched. 8% forced, Z=12.3 studs. Established the practical forced-overlap floor (~6–8%) for flat piles with rejection sampling. |
| `gen_pocket11.py` | P11 | 4-layer | **4-layer coverage system**: hero bricks at Y=[0,175] → gap-fill plates at Y=[182,210] → tiny 1×1 fill. Y-level separation insight: fill parts never conflict with hero parts. First use of FILL_OVAL (85% of placement oval) + 0.65× VIS_FACTOR. 3.3% forced, 100% visual coverage. |
| `gen_pocket13.py` | P13 | v3 | Applied P7's parameters (SIGMA 44×32, GAP=2) to new seed range 200–259. 2% forced. Showed Small size has inherent visual overlap issue at GAP=2. |
| `gen_pocket14.py` | P14 | v3 Medium | **First Medium size pocket.** SIGMA 58×46, GAP=4, 80 seeds. 0% forced on all seeds. Established Medium as production standard. |
| `fill_gaps.py` | P14-B | fill modifier | Original standalone fill_gaps script (before it was generalized into `modifier_fill_gaps.py`). |
| `settle_y.py` | P14-C | settle modifier | Original standalone settle_y script (before it was generalized into `modifier_settle_y.py`). |

### Recipe 2 — Sequential Outward Placement

| Script | Version | Key milestone |
|--------|---------|---------------|
| `gen_pocket12_toplayer_v1.py` | v1 | Baseline sequential outward placement, N_ANGLES=8, all plates, always-closest-to-center. Result: mechanical concentric rings, too regular. |
| `gen_pocket12_toplayer_v2.py` | v2 | Continuous random Y-rotation, GAP=-4, N_ANGLES=72, TOP_K=6. Result: massive overlaps (GAP=-4 too aggressive), all parts in one flat plane, only plates. |
| `gen_pocket12_toplayer_v3.py` | v3 | XZ-only collision, Y assigned per-type (bricks stick up, plates lie flat), bricks added to palette, GAP=-6. Result: height variation + bricks visible, but still some overlaps. |
| `gen_pocket12_toplayer_v4.py` | v4 | **Production algorithm**: GAP=0, oval 185×145 LDU, TILT_STR=0.40 for bricks, N_ANGLES=96, TOP_K=10. 31 parts placed, 0 overlaps. |
| `gen_pocket12_BCD.py` | modifiers | First implementation of rotation_shuffle modifier (50/20/17/5/8% distribution) and fill_small_parts modifier (Monte Carlo, EXISTING_SCALE=0.65). Produced P12-B, P12-C, P12-D. |
| `mod_rotate.py` | — | Standalone rotation shuffle script (before merge into gen_pocket12_BCD.py). |
| `mod_fill.py` | — | Standalone fill script for Recipe 2 (before merge into gen_pocket12_BCD.py). |
