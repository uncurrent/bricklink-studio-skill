# Skill Update Brief — Pockets Knowledge Collection

## Purpose

This document is a portable brief for collecting knowledge across chat sessions to update the `bricklink-studio` skill. Take it to each chat that worked on Pockets, ask the questions in Section 3, and bring back answers.

After collection → go to skill-creator chat with this document + answers.

---

## 1. What We Already Know (collected 2026-04-06)

### 1.1 Recipe 1 — Gaussian Rejection Sampling

**Origin:** Pockets 1–7, refined in P13 (Small) and P14 (Medium).

**Core algorithm (v3):** Random Gaussian XZ placement + triangular Y distribution + rotation-aware AABB collision + multi-seed search. Parts sorted largest-footprint-first. Rejection sampling: try N positions per part, pick least-overlapping.

**Pipeline:** `generator_pile.py` → `modifier_fill_gaps.py` → `modifier_settle_y.py` → `packager_io.sh`

**Scripts location:** `Pockets-recipe-1/`

**Key parameters (two presets):**

| Param | Small (P7/P13) | Medium (P14) |
|-------|---------------|-------------|
| SIGMA_X / SIGMA_Z | 44 / 32 | 58 / 46 |
| GAP | 2 LDU | 4 LDU |
| Y_MAX | 300 | 340 |
| MAX_TRIES | 1200 | 1500 |
| Seeds | 60 | 80 |
| Forced overlap | 0–2% | 0% |

**Modifiers (post-processing):**
- `modifier_fill_gaps.py` — top-down coverage analysis, adds small parts (1×1/1×2 plates, tiles, gears, pin) to fill visual gaps. Placed below main pile (Y=220–310).
- `modifier_settle_y.py` — gravity simulation: drops each part downward until it rests on another part or the floor. Binary search for Y position. Makes pile ~20% shorter/denser.

**What went well:** Rotation-aware AABB was the breakthrough (v3). Medium size with 0% forced. Multi-seed search reliably finds clean configurations. Fill+settle modifiers add realism as post-processing.

**What didn't work (documented in FAILED_APPROACHES.md):**
1. Editing model.lxfml instead of model.ldr — Stud.io renders LDR only
2. Y-rotation only (P4) — parts all face up, looks like a display
3. Fixed ellipsoid BV (P5) — 25% overlap, doesn't account for orientation
4. Uniform Y distribution (P4-5) — pile looks "fluffy", not gravity-settled
5. Gaussian without size ordering (P4-5) — big parts block center, 25% forced
6. ZIP creation in mounted workspace — EROFS error, must use /tmp
7. print() in stdout — corrupts LDR file, must use stderr

### 1.2 Recipe 2 — Sequential Outward Placement

**Origin:** Pockets 8–12, developed in a separate chat session.

**Core algorithm (v4):** Parts placed one-by-one from center outward. Each new part touches an existing part (touch-point formula with N_ANGLES=96 candidates). XZ-only collision detection. Random Y-rotation (0–360°). Best-of-60-seeds.

**Pipeline:** `generator_toplayer_v4.py` + modifiers applied via `generator_toplayer_with_modifiers.py`

**Scripts location:** `Pockets-recipe-2/`

**Key parameters:**

| Param | Value |
|-------|-------|
| OVAL_A / OVAL_B | 185 / 145 LDU |
| GAP | 0 |
| N_ANGLES | 96 |
| TOP_K | 10 |
| N_PARTS_MAX | 50 |
| N_SEEDS | 60 |
| TILT | brick 0.40, plate 0.07, tile 0.04 |

**Modifiers (applied to base output):**
- `modifier_rotation_shuffle.py` — diversifies rotations: 50% upright, 20% leaning, 17% on-side, 5% upside-down, 8% extreme diagonal
- `modifier_fill_small_parts.py` — Monte Carlo gap fill with small parts. Uses EXISTING_SCALE=0.65 workaround for AABB overestimation of tilted parts.

**Variant naming:** Base, B (rotation shuffle), C (small fillers), D (both mods)

**Known issues:** AABB of tilted bricks up to 2× nominal size. Top layer only — no hero/accent lower layers yet.

### 1.3 What We Know About Individual Pockets (P8–P12)

**P8** — Flat dense heap. Key discovery: reducing tilt_strength ×0.55 enables flat piles (Y_MAX=160). 6% forced — best flat result with Gaussian.

**P9** — Two-layer system (floor plates + Gaussian pile). 9% forced — WORSE than P8. Floor plates compete for Y space.

**P10** — Return to P8 approach, SIGMA_Z=33 for tighter Z footprint. 8% forced. Confirmed: Poisson disk for floor plates doesn't help (2D separation ≠ 3D AABB).

**P11** — 4-layer coverage system (NEW algorithm). Heroes+accents at Y=[0,175], gap-fill plates at Y=[182,210], tiny fill last. 3.3% forced. Breakthrough: Y-level separation means fill plates don't fight heroes for space. Uses 0.65× visual coverage correction.

**P12** — Sequential outward placement (became Recipe 2). Multiple versions (v1–v4) in Pocket 12/ folder. This is where the touch-point formula was developed.

### 1.4 Coloring System

**Location:** `Pockets-coloring/`

**11 palettes defined:**
- multicolor-1 through multicolor-6 (rainbow variations)
- sunset-warm-1, ocean-cool-1 (temperature themes)
- primary-bold-1 (classic LEGO)
- pastel-party-1 (light tones)
- neon-punch-1 (vivid saturated)

**Modifier:** `modifier_colorize.py` — reads LDR, reassigns colors using weighted random from palette. Batch script: `batch_colorize.py`.

### 1.5 Current Skill State

The `bricklink-studio` skill has:
- `projects/part-piles/guide.md` — documents up to P6 (v3 algorithm only)
- `learning/` — general patterns and failed approaches
- `SKILL_UPDATES.md` in Pockets/ — pending observations from P7–P10 session (not yet merged)
- No knowledge of Recipe 2, P11–P12 4-layer system, coloring, or production pipeline

### 1.6 Production Pipeline (built 2026-04-06)

**Recipe 1 batch:** `batch_generate.sh` — generates N pockets through full pipeline (generate → fill → settle → package). Each pocket gets unique seed range.

**Recipe 2 batch:** `batch_generate.py` — generates N pockets (base top layer only, no modifiers). Each pocket gets unique seed range.

**Colorizing batch:** `Pockets-coloring/batch_colorize.py` — takes a folder of .io files, applies all 11 palettes, outputs to a target folder.

**Model naming fix:** `0 Name: model.ldr` → `0 Name: {pocket_name}.ldr` in LDR header. Stud.io displays this in tab title.

---

## 2. What's Missing — Gaps to Fill

### From Recipe 2 development chat (P8–P12):

- [ ] **P11 full development history** — the 4-layer coverage system. How was it invented? What parameters were tuned? What failed before the Y-level separation idea?
- [ ] **P12 evolution v1→v2→v3→v4** — the sequential outward algorithm went through 4 versions. What changed in each? What problems did each solve?
- [ ] **Touch-point formula derivation** — how was the `touch_distance()` function developed? What alternatives were tried?
- [ ] **Modifier development** — how were rotation_shuffle and fill_small_parts developed? What ratios were tried before the final 50/20/17/5/8 split?
- [ ] **EXISTING_SCALE=0.65 workaround** — how was this number determined? Is it empirical?
- [ ] **What failed in Recipe 2 development** — equivalent of FAILED_APPROACHES.md but for the P8–P12 chat
- [ ] **P9 two-layer system details** — was this developed in Recipe 1 chat or Recipe 2 chat?

### From any chat that worked on coloring:

- [ ] **Palette design rationale** — how were the 11 palettes chosen? Based on real bag photos? Aesthetic intuition? User testing?
- [ ] **Color weight tuning** — how were the weights in each palette determined?
- [ ] **Mono palettes** — the code has placeholders for MONO_BLUE, MONO_RED etc. Were these ever developed?

### General:

- [ ] **Render settings** — any updates to top-down render parameters since P6?
- [ ] **Blender pipeline** — was it ever actually used? Any concrete results?
- [ ] **Part palette evolution** — Recipe 1 has 66 parts, Recipe 2 has 50. How were these part lists curated?

---

## 3. Questions to Ask in Each Chat

### Template: paste this at the start of each chat

> I'm collecting knowledge to update the bricklink-studio skill. This chat worked on Pockets development. I need you to tell me:
>
> 1. **What was developed here?** Which Pockets (P1–P19)? Which algorithms?
> 2. **What was the evolution?** Version by version — what changed, what problem each version solved.
> 3. **What failed?** Specific approaches tried and abandoned, with WHY they failed.
> 4. **What are the confirmed patterns?** Things that reliably work and should be reused.
> 5. **What parameters were tuned?** Before/after values, and how the final values were determined.
> 6. **Are there any scripts in the Pockets/ folder from this session?** What does each do?
> 7. **Any open questions or next steps that were discussed but not implemented?**

### Specific questions by topic:

**For the P11 (4-layer) chat:**
- How did you arrive at the Y-level separation idea?
- Why Y=[0,175] for heroes and Y=[182,210] for fill? How were these ranges chosen?
- What is the 0.65× visual coverage correction based on?
- Was FILL_OVAL vs OVAL separation discovered by accident or by design?

**For the P12 (sequential outward) chat:**
- Walk me through v1→v2→v3→v4 changes
- How was N_ANGLES=96 chosen? What about TOP_K=10?
- How does the touch_distance formula work geometrically?
- Why XZ-only collision (no Y check)?

**For the coloring chat:**
- What was the reference for palette design?
- Were palettes tested on actual renders? Which looked best?
- What's the plan for mono palettes?

---

## 4. Deliverable for Skill Creator

After collecting answers, bring to skill-creator chat:

1. **This document** (with gaps filled in)
2. **Request:** Update `bricklink-studio` skill with:
   - `projects/part-piles/` — full rewrite with both recipes, all experiments, production pipeline
   - `learning/patterns.md` — merge SKILL_UPDATES.md pending observations
   - `learning/failed.md` — merge all failed approaches from both recipes
   - New sub-section or project for coloring system
   - Update compatibility matrix if needed
   - Bump version in CHANGELOG
