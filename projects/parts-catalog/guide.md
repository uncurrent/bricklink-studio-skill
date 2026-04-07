---
project: parts-catalog
status: active
created: 2026-04-07
---

# Parts Catalog — Project Guide

Cross-system LEGO parts catalog with color mapping, rarity metrics, and market data infrastructure.

**Canonical repo:** `github.com/uncurrent/lego-parts-catalog`

---

## Goal

A local SQLite database indexing all ~70,000 LEGO parts with:
- Cross-system ID mapping (BrickLink/Rebrickable ↔ LDraw ↔ LEGO Element ID)
- Color availability per part
- Frequency/rarity metrics (how many sets each part+color appears in)
- Rarity scores (0–100) with tiers (common → ultra_rare)
- Infrastructure for BrickLink price enrichment (Phase 2)

---

## Constraints

- Data source: Rebrickable CSV dumps (free, updated daily) + Rebrickable API for enrichment
- Storage: SQLite (single file, no server, supports complex queries)
- BrickLink API: requires seller status — not currently available. Schema is ready for when it becomes available.
- All scripts run locally on user's Mac (not in sandboxed environments)

---

## Sub-skills to Load

| Sub-skill | Why needed |
|---|---|
| `bom-export/guide.md` | Color ID mapping, BOM generation from catalog data |
| `knowledge/INDEX.md` | Cross-reference with tools and part recognition entries |

---

## Quick Start for Team

No API keys, no Rebrickable account, no CSV downloads needed.

```bash
# 1. Clone the repo
git clone https://github.com/uncurrent/lego-parts-catalog.git
cd lego-parts-catalog

# 2. Download the pre-built database (~250MB, one-time)
python3 build_catalog.py --download-prebuilt

# 3. Use it
python3 analyze_model.py --instructions path/to/model.io   # step-by-step instruction layout
python3 analyze_model.py path/to/model.io                  # buildability check
python3 query_catalog.py --search "2x4"                    # search parts
python3 query_catalog.py --part 3001                       # part details + colors

# 4. Check for updates (optional)
python3 build_catalog.py --check-update
```

**What team members DON'T need:**
- Rebrickable API key (only for `enrich_bricklink.py` enrichment)
- Any network access after the initial DB download
- CSV downloads or full rebuild

---

## Workflow

### Initial setup (one-time)

**Option A — Pre-built DB (recommended for team):**
1. `git clone https://github.com/uncurrent/lego-parts-catalog.git`
2. `python3 build_catalog.py --download-prebuilt`

**Option B — Build from scratch:**
1. `cd ~/Dev/BrickitStudio/Parts`
2. `python3 build_catalog.py` — downloads ~50MB of CSVs, builds SQLite DB (~2 min)
3. `python3 enrich_bricklink.py --rarity` — computes rarity scores (local, ~30 sec)
4. (Optional) `pip3 install requests && python3 enrich_bricklink.py --limit 500` — enriches top 500 parts via Rebrickable API

### Querying

- `python3 query_catalog.py` — summary stats
- `python3 query_catalog.py --part 3001` — full part details with all colors
- `python3 query_catalog.py --search "2x4"` — search by name
- `python3 query_catalog.py --color "Dark Red"` — parts in a color
- `python3 query_catalog.py --rarest` — rarest part+color combos
- `python3 query_catalog.py --export-all` — export to Excel (requires openpyxl)

### Model buildability analysis

- `python3 analyze_model.py path/to/model.io` — analyze a BrickLink Studio model
- `python3 analyze_model.py path/to/model.ldr` — analyze an LDraw file

The analyzer parses the model, extracts all part+color combinations, cross-references each against the catalog, and produces:
1. **Problem parts** — detailed view of parts not found or in wrong colors, with color substitution suggestions
2. **Rare parts** — table of rare/very_rare/ultra_rare combos in the model
3. **Full BOM** — every part with rarity score, tier, and catalog status
4. **Buildability verdict** — 🟢 EASY / 🟡 MODERATE / 🔴 HARD based on rarity distribution
5. **Interactive mode** — after the report: `problems`, `rare`, `common`, `part XXXX`, `colors`, `steps`, `all`, `quit`

### Instruction layout extraction

- `python3 analyze_model.py --instructions path/to/model.io` — extract step-by-step building instruction layout

Works **without the catalog DB** — reads only `model.ldr` and `model.ins` from the .io ZIP. Produces:
1. **Header** — Studio version, total parts/steps, page format (from `.info` + `model.ins`)
2. **Step-by-step listing** — parts added per step with quantities (×2, ×3), camera parameters (scale, pitch°, yaw°)
3. **Color summary** — unique parts and total pieces per color

### Database updates

- `python3 build_catalog.py --check-update` — check if a newer pre-built DB is available
- `python3 build_catalog.py --download-prebuilt` — download latest if newer than local
- `python3 build_catalog.py --download-prebuilt --force` — re-download regardless
- `python3 build_catalog.py` — full rebuild from Rebrickable CSVs
- `python3 build_catalog.py --skip-download` — rebuild from existing CSVs

---

## .io File Internal Structure

A BrickLink Studio `.io` file is a ZIP archive (no password needed — standard `zipfile.ZipFile()` works):

| File | Format | Contents |
|------|--------|----------|
| `model.ldr` | LDraw text | Parts list with `0 STEP` markers. Each `1` line = one part (color, 4×3 matrix, part ID). Primary parseable model source. |
| `model.ins` | XML | Full Instruction Maker layout: page setup, per-step camera settings (scale, pitch, yaw in radians), page template assignments, style definitions. |
| `model.lxfml` | XML | LEGO Digital Designer-compatible model representation. |
| `modelv2.ldr` | LDraw text | Alternative LDraw for compatibility. |
| `model2.ldr` | LDraw text | Extended LDraw with Studio-specific metadata. |
| `thumbnail.png` | PNG | Rendered model thumbnail. |
| `.info` | JSON | Metadata: Studio version, total parts count, parts DB version. |
| `errorPartList.err` | Text | Validation failures (usually empty). |

**Key notes:**
- Step data is split: `model.ldr` has `0 STEP` boundaries + parts; `model.ins` has camera angles + page layout
- Camera angles in `model.ins` are in radians — convert: `degrees = radians × 180 / π`
- Steps map 1:1 to pages in simple models (`template="OneByOne"`); complex models may use multi-step pages

---

## Database Schema

### Core tables (from CSV dumps)
- `parts` (~70k) — part_num, name, category, material
- `colors` (~220) — id, name, RGB hex, is_trans
- `part_categories` (~70) — category names
- `elements` (~90k) — LEGO Element ID → part+color mapping
- `part_relationships` (~30k) — alternates, mold variants, prints
- `themes`, `sets`, `inventories`, `inventory_parts` — full set data

### Computed tables
- `part_color_stats` — per part+color: num_sets, total_quantity, year range
- `part_stats` — per part: num_colors, num_sets, total_quantity
- `rarity_scores` — per part+color: score 0–100, tier (common/uncommon/rare/very_rare/ultra_rare)

### Enrichment tables
- `external_ids` — cross-system IDs from Rebrickable API
- `part_images` — thumbnail URLs
- `bricklink_prices` — placeholder for market data (Phase 2)

---

## Rarity Scoring

Score 0–100 (higher = rarer), combining:
- 50% — inverse log of set count
- 30% — inverse log of total quantity
- 10% — short production run boost (≤2 years)
- 10% — retired status boost (last seen >3 years ago)

Tiers: common (0–24), uncommon (25–49), rare (50–74), very_rare (75–89), ultra_rare (90–100)

---

## Key Settings / Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Data source | cdn.rebrickable.com CSV dumps | 9 files, ~50MB compressed |
| DB format | SQLite with WAL mode | Single file, ~250MB |
| API | Rebrickable v3 | Key in `rebrickable_key.txt` |
| Rate limit | 1.1 sec between API calls | Rebrickable limit: ~1 req/sec |
| Pre-built DB | github.com/uncurrent/lego-parts-catalog/releases | Versioned via `.db_version` file |

---

## Scripts Reference

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `build_catalog.py` | Download CSVs + build SQLite DB; or `--download-prebuilt` from GitHub Releases | stdlib only |
| `query_catalog.py` | Query DB + export to Excel | openpyxl (optional) |
| `enrich_bricklink.py` | API enrichment + rarity scoring | requests (for API) |
| `analyze_model.py` | Analyze .io/.ldr buildability; or `--instructions` for step layout | stdlib only |

---

## Database Repository

Pre-built DB (~250MB) is too large to bundle with the skill. Published separately:

**`github.com/uncurrent/lego-parts-catalog`**

**How it works:**
1. Maintainer builds: `python3 build_catalog.py` + `python3 enrich_bricklink.py --rarity`
2. Maintainer publishes: `./release.sh v1.0.0` → uploads DB as GitHub Release asset
3. Team downloads: `python3 build_catalog.py --download-prebuilt` → fetches latest release
4. Version tracked in `.db_version` — subsequent runs skip if already up to date

---

## Integration Points (future)

- **bom-export:** Annotate BOM with rarity tier and color substitution suggestions
- **model-generation:** Filter part palette by rarity to ensure buildable models
- **part-piles coloring:** Weight palettes by real-world production volumes
- **knowledge:** Empirical data to complement curated entries

---

## Known Limitations

- BrickLink API requires seller status (not available)
- Rarity doesn't account for set sales volume (LEGO doesn't publish this)
- Rebrickable CDN is blocked in Cowork sandbox — scripts must run locally
- `--instructions` mode requires a Studio .io file (not plain .ldr without model.ins)
