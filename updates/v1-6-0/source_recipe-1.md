# Pockets — Recipe 1

Generates realistic LEGO part piles for the Brickit Pockets feature.

Based on experience from Pockets 1–7: pure Gaussian placement with
rotation-aware AABB collision detection and multi-seed search.

## Pipeline

```
generator_pile.py  →  modifier_fill_gaps.py  →  modifier_settle_y.py  →  packager_io.sh
   (base pile)          (small details)           (Y compaction)           (.io for Stud.io)
```

### Scripts

| File | What it does |
|------|-------------|
| `generator_pile.py` | Generates the base pile. Rotation-aware AABB rejection sampling, multi-seed search. Supports Small and Medium sizes. |
| `modifier_fill_gaps.py` | Fills top-down visual gaps with small parts: 1×1/1×2 plates, tiles, bricks, gears, pin. |
| `modifier_settle_y.py` | Simulates gravity: drops each part down until it rests on another part or the floor. |
| `packager_io.sh` | Creates a ZIP-based .io file that opens in Stud.io. |

### Running

```bash
cd Pockets-recipe-1
python3 generator_pile.py --name "Pocket 15" --size medium --seeds 400 460 -o /tmp/p.ldr
python3 modifier_fill_gaps.py /tmp/p.ldr /tmp/pf.ldr --seed 42
python3 modifier_settle_y.py /tmp/pf.ldr /tmp/ps.ldr
bash packager_io.sh /tmp/ps.ldr "output/Pocket 15.io" 91
```

Options for `generator_pile.py`:
- `--size small` — tighter pile (~17×13 studs), good for small bags
- `--size medium` — wider pile (~22×16 studs), fewer overlaps
- `--seeds START END` — seed range for multi-seed search

Options for `modifier_settle_y.py`:
- `--floor N` — custom floor Y value

## Algorithm

v3 rotation-aware AABB rejection sampling:
1. Sort parts by footprint area (largest first)
2. For each part: try random Gaussian positions until no AABB overlap
3. Repeat over many seeds, pick the one with fewest forced placements

Key parameters by size:

| Parameter | Small | Medium |
|-----------|-------|--------|
| SIGMA_X | 44 | 58 |
| SIGMA_Z | 32 | 46 |
| GAP | 2 LDU | 4 LDU |
| Y_MAX | 300 | 340 |
| MAX_TRIES | 1200 | 1500 |

## History

Developed across Pockets 1–7, refined in P13 (Small) and P14 (Medium).
See `Pockets/POCKETS.md` for full evolution.
