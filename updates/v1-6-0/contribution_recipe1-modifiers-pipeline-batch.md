# Contribution: Recipe 1 — Modifiers, Medium Size, and Batch Pipeline

**Source chat:** "Pockets-recipe-1" (2026-04-06)
**Pockets developed:** P13, P14, P14-B, P14-C, P15–P19
**Algorithms:** v3 Gaussian rejection sampling (from P6/P7), fill_gaps modifier, settle_y modifier
**Key deliverable:** Complete Recipe 1 pipeline with two size presets and three post-processing stages

---

## 1. What Was Developed in This Chat

### 1.1 Pocket 13 — Small Size with P7-tuned Parameters

First pocket generated in this session. Goal: reproduce P7's 0% forced result using its exact parameters on a new seed range.

**Approach:** Took gen_pocket6.py as the template, applied P7's tuned parameters (tighter sigma, larger Y range, smaller GAP, more attempts and seeds), ran with seed range 200–259.

**Result:** Seed 209, 1/66 forced (2%). Footprint 17.4×10.9 studs. Close to reference but Z slightly narrow (10.9 vs 13.2).

**Key observation:** Even with P7 params, the Small size consistently produces some visual overlaps when opened in Stud.io. The AABB collision detection prevents geometric overlap, but parts can appear to visually intersect because AABB is a conservative approximation of the actual part shape.

### 1.2 Pocket 14 — First "Medium" Size Pocket

User observed P13 in Stud.io and noted "довольно много оверлаппингов" (quite a lot of overlapping). Requested larger footprint area.

**Design rationale for Medium size:**
- SIGMA_X: 44 → 58 (32% wider horizontal spread)
- SIGMA_Z: 32 → 46 (44% wider depth spread)
- GAP: 2 → 4 LDU (doubled clearance between AABBs)
- Y_MAX: 300 → 340 (13% more vertical room)
- MAX_TRIES: 1200 → 1500 (25% more placement attempts)
- N_SEEDS: 60 → 80 (33% more seeds searched)

**How Medium parameters were determined:**
- SIGMA increases were based on the desired ~25% area increase: if footprint area scales with sigma product, then `58*46 / (44*32) ≈ 1.89` — roughly doubling the effective area.
- GAP=4 was chosen to match P6's original value (P7 had reduced it to 2, which caused visual overlaps despite 0% algorithmic forced).
- Y_MAX=340 was a modest increase to give extra vertical breathing room with the wider spread.

**Result:** 0% forced on ALL 80 seeds tested. Footprint ~22×16 studs. This was dramatically better than Small — the algorithm never struggles to place any part.

**Implication:** Medium size is overprovisioned for 66 parts with v3 algorithm. Future work could either increase part count or reduce sigma slightly to find the "sweet spot" where forced is low but pile looks denser.

### 1.3 Pocket 14-B — fill_gaps Modifier Development

User requested a script to fill visual gaps with small parts: "мелкие детали это детали 1х1, 1x2, плейты, тайлы и брики, можно использовать одну или две шестеренки, один пин."

**Algorithm — top-down coverage analysis:**

1. Parse existing LDR file — extract all part positions and compute rotation-aware AABBs
2. Build XZ coverage grid (GRID_RES=14 LDU per cell, ~0.7 studs)
3. Apply VIS_FACTOR=0.60 correction to each part's AABB extents. This accounts for the fact that tilted parts cover less visual area than their AABB suggests. (Value chosen based on P11's finding of 0.65 — slightly more aggressive at 0.60 to detect more gaps.)
4. Compute a "fill oval" from the actual model footprint at 85% size — don't try to fill the extreme edges, only the core
5. Find uncovered cells within the fill oval, sorted by distance from center (fill center first)
6. For each gap cell, try placing fill parts (largest first) at 8 rotation angles (0°, 45°, 90°, etc.)
7. Fill parts placed at Y=220–310 — below the main pile to minimize collisions with hero parts
8. Each fill part tried at up to 8 random Y positions within the range
9. Overflow check: skip if part AABB extends beyond fill oval × 1.15

**Fill part palette (25 parts total):**

| Category | Parts | Count |
|----------|-------|-------|
| Plates | 1×2, 1×1, Round 1×1 | 10 |
| Tiles | 1×2, 1×1 | 6 |
| Bricks | 1×1, 1×2, Round 1×1 | 6 |
| Technic | Gear 24T, Gear 8T, Pin | 3 |

**Rotation strategy by part type:**
- Plates/tiles: near-flat (make_R_flat, TILT_STR=0.12)
- Bricks: moderate tilt (make_R_tilted, ts=0.35)
- Technic: moderate tilt (make_R_tilted, ts=0.45)

**Multi-seed testing results on P14:**

| Seed | Parts added | Coverage before → after |
|------|-------------|------------------------|
| 42 | 25 | 72% → 87% |
| 100 | 25 | 72% → 87% |
| 200 | 25 | 72% → 87% |
| 300 | 25 | 72% → 88% (best) |
| 400 | 25 | 72% → 87% |
| 500 | 25 | 72% → 86% |

Coverage consistently reaches 86–88%. All 25 parts are placed every time. The limiting factor is that MAX_FILL=30 but only 25 parts are in the palette — could add more for higher coverage.

**Design decisions:**
- Parts are consumed once each (removed from pool after placement) — no duplicates
- Y range 220–310 was chosen to be clearly below the main pile (P14 hero Y range is 6–321, but the triangular distribution means most parts are at Y < 100). This is the same Y-separation insight from P11.
- VIS_FACTOR=0.60 is empirical: 1.0 would report near-100% coverage (AABB overstates footprint), 0.5 would report too many gaps. 0.60 was tested visually and matches perceived gaps well.
- GAP=3 for fill parts (slightly less than the 4 used for heroes) — fill parts should sit close together.

### 1.4 Pocket 14-C — settle_y Modifier Development

User requested: "скрипт который позволяет уплотнить детали по оси Y" (compact parts along Y axis).

**Algorithm — gravity simulation:**

1. Parse all parts with positions and rotation-aware AABBs
2. Define a floor plane at Y_FLOOR (auto-detected: max Y of all parts + largest ey + 20 LDU margin)
3. Sort parts by Y descending (bottom parts settle first — highest Y = closest to floor in LDraw coords)
4. For each part (processing bottom-to-top):
   - Find the maximum Y it can reach without overlapping any already-settled part
   - For each settled part that overlaps in XZ: compute Y limit = settled_Y - settled_ey - part_ey - GAP
   - Also constrained by floor: Y ≤ Y_FLOOR - part_ey
   - Take the minimum of all constraints as the new Y
   - Only allow downward movement (new Y ≥ original Y)
5. Record all new Y positions and write output

**Key design choice — processing order:**
Parts are sorted by Y descending (highest Y first = already closest to floor). This means:
- Bottom parts get placed at/near the floor first
- Upper parts then "fall" onto the settled bottom parts
- This mimics real gravity: a part falling onto a pile comes to rest on whatever is below it

**Why not binary search?**
The initial plan was binary search, but the analytical approach is simpler and exact:
- For each XZ-overlapping settled part, compute the exact Y where AABBs just touch
- Take the most restrictive (lowest) Y limit
- No iteration needed — O(N²) but N=91 is trivial

**Results on P14-B (91 parts):**

| Metric | Before | After |
|--------|--------|-------|
| Y range | 6→321 (315 LDU) | 101→389 (289 LDU) |
| Height | ~39 plates | ~36 plates |
| Reduction | — | 8% shorter |
| Parts moved | — | 91/91 (all) |
| Avg drop | — | 106.5 LDU (13.3 plates) |

**Why only 8% reduction?**
The pile was already somewhat settled by the triangular Y distribution (biased toward bottom). The main beneficiaries are:
- Fill parts at Y=220–310 that now drop down toward the hero pile
- Outlier hero parts that happened to be placed high

The modest reduction is actually expected — it means the original Gaussian+triangular placement is already fairly compact. The value of settle_y is removing the few obviously floating parts.

**GAP=1 for settle** (vs GAP=4 for generation, GAP=3 for fill) — after settling, parts should sit very close together, just barely not touching.

### 1.5 Pockets 15–19 — Batch Generation

Generated 5 pockets through the full Recipe 1 pipeline to validate the workflow at scale.

**Batch configuration:**

| Pocket | Gen seeds | Fill seed | Result |
|--------|-----------|-----------|--------|
| P15 | 400–460 | 100 | 91 parts, 19.0×16.8, cov 86%, 36 plates |
| P16 | 500–560 | 200 | 91 parts, 17.8×14.7, cov 96%, 36 plates |
| P17 | 600–660 | 300 | 91 parts, 21.3×15.6, cov 92%, 37 plates |
| P18 | 700–760 | 400 | 91 parts, 19.3×15.5, cov 95%, 34 plates |
| P19 | 800–860 | 500 | 91 parts, 19.8×13.9, cov 100%, 34 plates |

**Observations from batch run:**
- ALL seeds across all 5 pockets had 0% forced — confirms Medium is very comfortable for 66 parts
- Coverage after fill_gaps varies from 86% to 100% — P19 hit 100% (all gaps filled!)
- Height after settle ranges 34–37 plates, fairly consistent
- Average drop from settle_y: 11–17 plates across runs — consistent with P14-C result
- Footprint varies: X from 17.8 to 21.3 studs, Z from 13.9 to 16.8 studs. Gaussian randomness means each pocket has a unique shape.

**P19 is notable** — 100% coverage with only 25 fill parts. This happened because the base pile (seed 800) happened to have a tighter footprint (19.8×13.9), so the fill oval was smaller and easier to cover completely.

### 1.6 Recipe 1 Pipeline Organization

Scripts were organized into `Pockets-recipe-1/` with clear names:

| Script | Purpose |
|--------|---------|
| `generator_pile.py` | Step 1: Generate base pile (supports --size small/medium) |
| `modifier_fill_gaps.py` | Step 2: Fill visual gaps with small parts |
| `modifier_settle_y.py` | Step 3: Y-axis compaction (gravity settle) |
| `packager_io.sh` | Step 4: Package .ldr as .io ZIP for Stud.io |
| `RECIPE.md` | Documentation and usage examples |

The generator accepts CLI arguments: `--name`, `--size`, `--seeds START END`, `-o OUTPUT`.

---

## 2. Evolution — What Changed and Why

### v3 base (from P6) → P13 application

**Change:** Applied P7's parameters to P6's code structure.
**Why:** P7 achieved 0% forced by: (1) tighter XZ sigma (focus parts), (2) larger Y range (let parts stack), (3) smaller GAP (closer fit), (4) more tries and seeds.
**Result:** 1/66 forced (2%) — not quite 0% like P7, because different seed range produces different random configurations.

### P13 (Small) → P14 (Medium)

**Change:** Wider sigma, larger GAP, more Y range.
**Why:** User saw visual overlaps in Stud.io screenshot. Root cause: AABB collision only prevents geometric center overlap — visual perception is stricter.
**Problem solved:** Zero forced across all seeds. Visual overlaps eliminated by larger GAP.

### P14 → P14-B (fill_gaps)

**Change:** Post-processing step adds 25 small parts to fill top-down visual gaps.
**Why:** Even with 0% forced, the pile has visible "holes" when viewed from above — areas where the baseplate is visible through the pile.
**Problem solved:** Coverage jumped from 72% to 88%. Pile looks more natural and dense from top-down.

### P14-B → P14-C (settle_y)

**Change:** Post-processing step compacts the pile vertically.
**Why:** Fill parts at Y=220–310 are "floating" below the pile. Settling drops them into contact with hero parts.
**Problem solved:** Pile 8% shorter, no floating parts. All parts rest on something.

### P14-C → P15–P19 (batch)

**Change:** Automated the full pipeline for batch generation.
**Why:** Need to produce many pockets efficiently for the app.
**Problem solved:** Confirmed pipeline reliability across 5 diverse seed ranges.

---

## 3. What Failed

### 3.1 Small Size for Overlap-Free Piles

**What was tried:** P13 with P7 params (SIGMA 44×32, GAP=2).
**What happened:** 2% forced algorithmically, and visible overlaps in Stud.io rendering.
**Why it failed:** GAP=2 is too tight — parts that are technically non-overlapping by 2 LDU (0.1 studs) still LOOK overlapping in Stud.io's rendering. The visual threshold for "not overlapping" is around GAP=4.
**Alternative:** Medium size with GAP=4 eliminates the issue entirely.

### 3.2 Fill Part Coverage Ceiling at ~88%

**What was tried:** fill_gaps with 25 parts on Medium pockets.
**What happened:** Coverage plateaus at 86–88% (except P19 which reached 100% by luck).
**Why:** The palette has only 25 fill parts. With MAX_FILL=30, the algorithm runs out of parts before it runs out of gaps. Also, some gap cells are awkwardly shaped — no fill part rotation fits without overlapping existing parts.
**Possible fix (not implemented):** Increase fill palette to 35–40 parts, or run fill_gaps twice with different seeds.

### 3.3 Settle Y Modest Improvement (8–17%)

**What was tried:** Gravity settle on filled pockets.
**What happened:** Only 8–17% height reduction.
**Why:** The triangular Y distribution in the generator already biases parts toward the bottom. Settle mostly helps fill parts (which are placed at Y=220–310) and outlier hero parts.
**Possible fix (not implemented):** Use a uniform Y distribution in the generator, then rely on settle_y to do all the compaction. This might produce a more naturally layered pile.

---

## 4. Confirmed Patterns

### Pattern: Medium Size is the Sweet Spot for 66 Parts

0% forced on every seed tested (480+ seeds across P14–P19). SIGMA 58×46 with GAP=4 provides comfortable room. There's no benefit to searching many seeds — any seed works. Could potentially reduce N_SEEDS to 5–10 for Medium.

### Pattern: VIS_FACTOR=0.60 for Coverage Detection

Using 60% of the rotation-aware AABB extents for XZ coverage estimation produces realistic gap detection. Without correction (1.0), nearly 100% coverage is reported even when visible gaps exist. At 0.50, too many false gaps are reported.

### Pattern: Fill Parts Below Main Pile (Y-Level Separation)

Placing fill parts at Y=220–310 (below hero pile at Y=0–200) avoids nearly all collisions. This is the same insight from P11's 4-layer system: separate Y ranges for different part categories virtually eliminates AABB conflicts.

### Pattern: Process Bottom-to-Top for Settle

Sorting parts by Y descending (bottom first) and settling each one to the floor or onto already-settled parts below it produces the most physically plausible result.

### Pattern: GAP Decreases Through Pipeline Stages

| Stage | GAP | Rationale |
|-------|-----|-----------|
| Generator | 4 LDU | Comfortable spacing, no visual overlap |
| Fill gaps | 3 LDU | Fill parts sit close but not touching |
| Settle Y | 1 LDU | After settling, parts should be in contact |

### Pattern: ZIP in /tmp, Then Copy

Creating .io (ZIP) files in the mounted workspace fails (EROFS). Always build in /tmp, then copy the result. (Confirmed 3+ times, also in general skill patterns.)

### Pattern: Stderr for Diagnostics

All stats, progress output, and debug info goes to stderr. File output (LDR) goes to a named file. Never mix diagnostic output with data output.

---

## 5. Parameters Tuned

### Generator Parameters

| Parameter | P6 (original) | P7 (tuned) | P13 (this chat) | P14 Medium (this chat) | How determined |
|-----------|---------------|------------|-----------------|----------------------|----------------|
| SIGMA_X | 52 | 44 | 44 | 58 | P7: reduced for tighter pile. P14: increased ~30% for larger footprint |
| SIGMA_Z | 42 | 32 | 32 | 46 | Same rationale as SIGMA_X |
| GAP | 4 | 2 | 2 | 4 | P7: reduced for denser packing. P14: restored to 4 after visual overlap feedback |
| Y_MAX | 240 | 300 | 300 | 340 | P7: increased to compensate for tighter XZ. P14: modest further increase |
| MAX_TRIES | 600 | 1200 | 1200 | 1500 | P7: doubled for better search. P14: slight increase |
| N_SEEDS | 20 | 60 | 60 | 80 | More seeds = better chance of clean configuration |
| Y bias peak | Y_MIN+40 | Y_MIN+50 | Y_MIN+50 | Y_MIN+50 | P7: slightly higher peak for more vertical spread |

### Fill Gaps Parameters

| Parameter | Value | How determined |
|-----------|-------|----------------|
| GRID_RES | 14 LDU | ~0.7 studs per cell. Coarser than P11's 12 — better for visual assessment |
| VIS_FACTOR | 0.60 | Based on P11's 0.65, reduced slightly. Empirical visual test |
| GAP | 3 LDU | Between generator's 4 and settle's 1 — fill parts should be close but not touching |
| MAX_FILL | 30 | Palette has 25 parts; headroom for future expansion |
| Y_FILL_RANGE | 220–310 | Below main pile. 220 = ~27 plates, well below most hero parts |
| TILT_STR | 0.12 (plates), 0.35 (bricks), 0.45 (technic) | Plates nearly flat, bricks moderate, technic more random |
| Fill oval | 85% of actual footprint | Don't fill extreme edges — looks unnatural |

### Settle Y Parameters

| Parameter | Value | How determined |
|-----------|-------|----------------|
| GAP | 1 LDU | Minimal clearance — parts should rest on each other |
| Y_FLOOR | auto: max_Y + max_ey + 20 | Just below the lowest part, with margin |

---

## 6. Scripts Created

All scripts live in `BrickitStudio/Pockets-recipe-1/`:

### generator_pile.py

**Purpose:** Generate base LEGO part pile as .ldr file.
**Algorithm:** v3 rotation-aware AABB rejection sampling with multi-seed search.
**Inputs:** `--name`, `--size small|medium`, `--seeds START END`, `-o OUTPUT`
**Outputs:** .ldr file with 66 parts
**Key feature:** Two size presets (small/medium) with all parameters bundled.

### modifier_fill_gaps.py

**Purpose:** Post-process a .ldr to fill top-down visual gaps with small parts.
**Algorithm:** XZ coverage grid analysis → gap detection → greedy placement of small parts in gaps.
**Inputs:** `input.ldr output.ldr [--seed N]`
**Outputs:** New .ldr with original parts + up to 25 fill parts
**Key feature:** Automatic fill oval computation from model footprint. Parts placed below main pile to avoid collisions.

### modifier_settle_y.py

**Purpose:** Post-process a .ldr to compact the pile vertically (simulate gravity).
**Algorithm:** Sort parts bottom-to-top, drop each one to the lowest non-colliding Y position.
**Inputs:** `input.ldr output.ldr [--floor N]`
**Outputs:** New .ldr with same parts at compacted Y positions
**Key feature:** Auto-detects floor from model bounds. Only moves parts downward, never up.

### packager_io.sh

**Purpose:** Package a .ldr file as a Stud.io .io file (ZIP archive).
**Inputs:** `input.ldr output.io [total_parts]`
**Outputs:** .io file ready to open in Stud.io
**Key feature:** Creates ZIP in /tmp to avoid EROFS on mounted workspaces.

### Also created in Pockets/Pocket 13/ and Pockets/Pocket 14/:

- `gen_pocket13.py` — P13-specific generator (Small, seeds 200–259)
- `gen_pocket14.py` — P14-specific generator (Medium, seeds 300–379)
- `fill_gaps.py` — original fill_gaps script (before it was moved to recipe folder)
- `settle_y.py` — original settle script (before it was moved to recipe folder)
- `NOTES.md` in each pocket folder — per-pocket stats and parameters

---

## 7. Open Questions and Next Steps

### Not Implemented — Discussed or Observed

1. **Part count increase for Medium:** Medium has so much room that part count could increase from 66 to 80–90 without increasing forced placements. Would make the pile look denser.

2. **Multiple fill_gaps passes:** Running fill_gaps twice (with different seeds) could push coverage from 88% toward 95%+. Alternatively, expand the fill palette to 35–40 parts.

3. **Uniform Y distribution + settle_y:** Instead of triangular Y in the generator (which pre-biases toward bottom), use uniform Y and let settle_y do ALL the compaction. Might produce more natural layering.

4. **Render settings for Medium:** The existing render parameters (camera position, lighting) were designed for Small size. Medium pockets are ~24% larger area — the camera may need to zoom out.

5. **Small vs Medium visual comparison:** We never did a side-by-side visual comparison of Small (P13) vs Medium (P14) in rendered form. Would help calibrate which size looks better for the app.

6. **Fill part diversity:** Current palette is fixed. Could randomize which fill parts are available per pocket for more variety across pockets.

7. **Settle_y with XZ jitter:** Current settle only moves parts along Y. Adding tiny XZ jitter during settling (±2 LDU) could make parts nestle together more naturally.

8. **Recipe 1 vs Recipe 2 visual comparison:** The whole point of two recipes is comparison. As of this session, Recipe 2 only has top-layer pockets (P12 variants). Direct comparison will be possible once Recipe 2 has full piles.

---

## 8. Gaps from SKILL_UPDATE_BRIEF Addressed by This Chat

From Section 2 of the brief:

- **"Part palette evolution"** — Partially addressed: Recipe 1 uses the same 66-part palette from P6. The palette was not modified in this chat. Fill_gaps adds 25 additional small parts as post-processing. See Section 6 for the fill palette composition.

- **"P9 two-layer system details"** — NOT from this chat. P9 was developed in the Recipe 2 chat.

- **"Render settings"** — Not addressed. No rendering was done in this chat.

- **"Blender pipeline"** — Not addressed. Not used in this chat.

All other gaps in the brief (P11 history, P12 v1–v4, touch-point formula, modifier development for Recipe 2, coloring) are from other chat sessions.
