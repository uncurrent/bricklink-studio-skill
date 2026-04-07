# Parts Catalog — Confirmed Patterns

## 2026-04-07 — Rebrickable CSV dumps are the best starting point
**Context:** Building a comprehensive LEGO parts database
**Pattern:** Download all 9 CSV dump files from Rebrickable CDN, load into SQLite. Covers parts, colors, elements, sets, inventories, relationships. Updated daily.
**Confirmed:** 1 time (initial catalog build)
**Why:** Free, no API key needed for bulk, comprehensive cross-system mappings

## 2026-04-07 — SQLite for parts data at scale
**Context:** Choosing storage format for ~70k parts with color relationships
**Pattern:** Use SQLite with WAL mode and generous cache. Create indexes on part_num, color_id, and composite (part_num, color_id). Batch inserts in groups of 10k–50k rows.
**Confirmed:** 1 time (catalog build: 1M+ inventory_parts rows loaded in ~30 sec)

## 2026-04-07 — Log-scaled normalization for rarity scoring
**Context:** Computing meaningful rarity scores across power-law distributed data
**Pattern:** Use math.log1p() for normalizing both set count and quantity. Linear normalization makes everything look "rare" because a few parts dominate.
**Confirmed:** 1 time (rarity distribution produces meaningful tiers)

## 2026-04-07 — .io file parsing: unzip + read model.ldr
**Context:** Analyzing BrickLink Studio models programmatically
**Pattern:** .io files are ZIP archives. Extract model.ldr, parse Type 1 lines (`1 <color> <x y z> <matrix> <part>.dat`). Strip `.dat` suffix to get part_num. Color is LDraw color ID (maps to Rebrickable color ID).
**Confirmed:** 1 time (Pochita model — 115 parts extracted correctly)

## 2026-04-07 — Cross-reference model parts via alternates/molds
**Context:** Some parts in .io files use variant IDs (e.g. `3023b` instead of `3023`)
**Pattern:** When part+color not found in catalog: try base part (strip suffix), try alternate/mold relationships from `part_relationships` table. This catches most "false negative" misses.
**Confirmed:** 1 time (Pochita model analysis)

## 2026-04-10 — .io files are fully parseable ZIP archives with rich instruction data
**Context:** Extracting step-by-step building instruction layout from Studio .io files
**Pattern:** .io files open with standard `zipfile.ZipFile()` (no password). Contain: `model.ldr` (parts + `0 STEP` markers), `model.ins` (XML with camera angles per step in radians, page layout), `model.lxfml` (LDD XML), `.info` (JSON metadata). Parse `model.ldr` for steps/parts, `model.ins` for camera data and page mapping. Camera angles: `degrees = radians × 180 / π`. Instruction data persists across saves.
**Confirmed:** 2 times (Toucan: 23 steps, 24 pages, camera angles extracted; Pochita: steps + instruction data present)
**Why:** No need for Studio GUI to read model data — all structure is accessible programmatically

## 2026-04-10 — --download-prebuilt enables zero-config team workflow
**Context:** Team members need the catalog DB without rebuilding from scratch
**Pattern:** `build_catalog.py --download-prebuilt` fetches the latest pre-built DB from GitHub Releases (~250MB). Version tracked in `.db_version` — subsequent calls skip download if already up to date. `--check-update` checks without downloading. This decouples "using the catalog" from "building the catalog."
**Confirmed:** 1 time (workflow designed and implemented)
**Why:** Team members don't need Rebrickable accounts, API keys, or 2-minute build times
