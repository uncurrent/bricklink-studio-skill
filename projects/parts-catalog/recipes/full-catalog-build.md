---
name: Full Catalog Build
version: 1
project: parts-catalog
status: verified
created: 2026-04-07
updated: 2026-04-07
---

## Purpose

Build a complete LEGO parts catalog with cross-system ID mapping and rarity scores from scratch.

## Inputs

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| rebuild | flag | false | — | Skip download, rebuild from existing CSVs |
| api_limit | int | 500 | 1–5000 | Number of top parts to enrich via API |

## Pipeline

### Step 1: Download and Build Database
- **Script:** `scripts/build_catalog.py`
- **Command:** `python3 build_catalog.py`
- **Output:** `lego_catalog.db` with all core tables + computed stats

### Step 2: Compute Rarity Scores
- **Script:** `scripts/enrich_bricklink.py`
- **Command:** `python3 enrich_bricklink.py --rarity`
- **Output:** `rarity_scores` table populated with scores and tiers

### Step 3: API Enrichment (optional)
- **Script:** `scripts/enrich_bricklink.py`
- **Command:** `python3 enrich_bricklink.py --limit 500`
- **Output:** `external_ids` and `part_images` tables populated

### Step 4: Verify
- **Script:** `scripts/query_catalog.py`
- **Command:** `python3 query_catalog.py`
- **Output:** Summary stats printed to terminal

## Batch Usage

```bash
cd ~/Dev/BrickitStudio/Parts
python3 build_catalog.py
python3 enrich_bricklink.py --rarity
pip3 install requests && python3 enrich_bricklink.py --limit 500
python3 query_catalog.py
```

## Output Spec

- **Format:** SQLite database (`lego_catalog.db`)
- **Location:** `~/Dev/BrickitStudio/Parts/`
- **Quality criteria:** All tables populated, rarity distribution has entries in all 5 tiers

## Known Limitations

- Download requires internet access (not available in Cowork sandbox)
- API enrichment requires Rebrickable API key in `rebrickable_key.txt`
- Full rebuild takes ~2 minutes
