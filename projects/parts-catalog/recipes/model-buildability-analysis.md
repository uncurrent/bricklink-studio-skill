---
name: Model Buildability Analysis
version: 1
project: parts-catalog
status: verified
created: 2026-04-07
updated: 2026-04-07
---

## Purpose

Analyze a BrickLink Studio (.io) or LDraw (.ldr) model to assess whether all parts exist in the specified colors and how realistic it is for Brickit app users to build from their own collection.

## Inputs

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| model_file | path | required | — | Path to .io or .ldr file |

## Prerequisites

The catalog database must be built first (see `full-catalog-build` recipe).
Rarity scores must be computed (`enrich_bricklink.py --rarity`).

## Pipeline

### Step 1: Analyze Model
- **Script:** `scripts/analyze_model.py`
- **Command:** `python3 analyze_model.py path/to/model.io`
- **Output:** Detailed report with problem parts, rare parts, full BOM, buildability verdict

### Step 2: Interactive Exploration (optional)
- After the report, the script enters interactive mode
- Commands: `problems`, `rare`, `common`, `part XXXX`, `colors`, `all`, `quit`

## Output Spec

- **Format:** Terminal output (structured report + interactive REPL)
- **Sections:**
  1. Problem parts — wrong color (with substitutions) and not in catalog
  2. Rare parts — table of rare/very_rare/ultra_rare entries
  3. Full BOM — all part+color combos with rarity, tier, status
  4. Buildability summary — catalog checks, rarity distribution, verdict
- **Verdict scale:** EASY (<10% hard) / MODERATE (10–30% hard) / HARD (>30% hard)

## Known Limitations

- Printed/decorated parts (e.g. `14769pz0`) may not be in Rebrickable catalog
- Does not account for user's actual collection — assesses general availability only

## Verified On

- Pochita model (115 pieces, 34 unique parts) — Verdict: MODERATE
  - 32/39 combos exist, 5/39 wrong color (Orange), 2/39 not in catalog (printed)
