#!/usr/bin/env python3
"""
Rebrickable API Enrichment (Phase 2)
======================================
Enriches the catalog with additional data from Rebrickable API:
- Part images (thumbnail URLs)
- External IDs mapping (BrickLink, LEGO, LDraw, BrickOwl)
- Known colors per part from the API (cross-checks with CSV data)
- Set year/theme details for rarity weighting

Also computes a "rarity score" combining:
- Number of sets the part+color appears in
- Total quantity produced across sets
- Year range (old retired colors = rarer in practice)

Setup:
    Put your Rebrickable API key in `rebrickable_key.txt` in this directory.
    Get a free key at: https://rebrickable.com/api/

Usage:
    python3 enrich_bricklink.py                   # Enrich top 500 most common parts
    python3 enrich_bricklink.py --part 3001       # Enrich a specific part
    python3 enrich_bricklink.py --limit 2000      # Enrich top N parts
    python3 enrich_bricklink.py --rarity          # Compute rarity scores for all part+color combos
"""

import argparse
import json
import math
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

DB_PATH = Path(__file__).parent / "lego_catalog.db"
KEY_PATH = Path(__file__).parent / "rebrickable_key.txt"

API_BASE = "https://rebrickable.com/api/v3/lego"
DELAY = 1.1  # Rebrickable rate limit: ~1 req/sec


# ─── Setup ────────────────────────────────────────────────────────────────────

def get_api_key():
    if not KEY_PATH.exists():
        print(f"Error: API key not found at {KEY_PATH}")
        print("Get a free key at https://rebrickable.com/api/")
        sys.exit(1)
    return KEY_PATH.read_text().strip()


def get_db():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run `python3 build_catalog.py` first.")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_schema(conn):
    """Add enrichment tables if they don't exist yet."""
    conn.executescript("""
        -- External ID mapping from Rebrickable API
        CREATE TABLE IF NOT EXISTS external_ids (
            part_num        TEXT NOT NULL,
            source          TEXT NOT NULL,   -- 'BrickLink', 'LEGO', 'LDraw', 'BrickOwl', 'Peeron'
            external_id     TEXT NOT NULL,
            PRIMARY KEY (part_num, source, external_id)
        );
        CREATE INDEX IF NOT EXISTS idx_extids_source ON external_ids(source);

        -- Part image URLs
        CREATE TABLE IF NOT EXISTS part_images (
            part_num        TEXT PRIMARY KEY,
            img_url         TEXT,
            fetched_at      TEXT
        );

        -- Rarity scores (computed)
        CREATE TABLE IF NOT EXISTS rarity_scores (
            part_num        TEXT NOT NULL,
            color_id        INTEGER NOT NULL,
            rarity_score    REAL NOT NULL,      -- 0 = most common, 100 = rarest
            rarity_tier     TEXT NOT NULL,       -- 'common', 'uncommon', 'rare', 'very_rare', 'ultra_rare'
            num_sets        INTEGER,
            total_qty       INTEGER,
            years_available INTEGER,             -- last_year - first_year
            is_retired      INTEGER DEFAULT 0,   -- 1 if last_year < current_year - 3
            PRIMARY KEY (part_num, color_id)
        );
        CREATE INDEX IF NOT EXISTS idx_rarity_score ON rarity_scores(rarity_score);
        CREATE INDEX IF NOT EXISTS idx_rarity_tier ON rarity_scores(rarity_tier);
    """)
    conn.commit()


# ─── API calls ────────────────────────────────────────────────────────────────

def api_get(api_key, endpoint, params=None):
    """Make an authenticated GET request to Rebrickable API."""
    if not HAS_REQUESTS:
        print("Error: requests not installed. Run: pip3 install requests")
        sys.exit(1)

    headers = {"Authorization": f"key {api_key}"}
    url = f"{API_BASE}/{endpoint}"
    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 429:
        print("  Rate limited, waiting 5s...", flush=True)
        time.sleep(5)
        return api_get(api_key, endpoint, params)  # retry
    else:
        return None


def fetch_part_details(api_key, part_num):
    """Fetch part details including image URL."""
    return api_get(api_key, f"parts/{part_num}/")


def fetch_part_colors(api_key, part_num):
    """Fetch all known colors for a part."""
    results = []
    data = api_get(api_key, f"parts/{part_num}/colors/", {"page_size": 200})
    if data and "results" in data:
        results.extend(data["results"])
        # Handle pagination
        while data.get("next"):
            time.sleep(DELAY)
            data = requests.get(data["next"],
                                headers={"Authorization": f"key {api_key}"}).json()
            if "results" in data:
                results.extend(data["results"])
    return results


def fetch_external_ids(api_key, part_num):
    """Fetch external IDs (BrickLink, LEGO, LDraw mappings)."""
    data = api_get(api_key, f"parts/{part_num}/external_ids/")
    if data and "results" in data:
        return data["results"]
    return []


# ─── Enrichment ───────────────────────────────────────────────────────────────

def enrich_part(api_key, conn, part_num):
    """Enrich a single part with API data."""
    cur = conn.cursor()
    enriched = 0

    # 1. Part details + image
    existing = cur.execute(
        "SELECT fetched_at FROM part_images WHERE part_num = ?", (part_num,)
    ).fetchone()

    if not existing:
        details = fetch_part_details(api_key, part_num)
        if details:
            cur.execute(
                "INSERT OR REPLACE INTO part_images (part_num, img_url, fetched_at) VALUES (?, ?, ?)",
                (part_num, details.get("part_img_url", ""), datetime.now(timezone.utc).isoformat())
            )
            enriched += 1
        time.sleep(DELAY)

    # 2. External IDs (BrickLink, LEGO, LDraw mapping)
    existing_ids = cur.execute(
        "SELECT COUNT(*) FROM external_ids WHERE part_num = ?", (part_num,)
    ).fetchone()[0]

    if existing_ids == 0:
        ext_data = fetch_external_ids(api_key, part_num)
        if ext_data:
            for source_data in ext_data:
                source = source_data.get("source", "")
                for ext_id in source_data.get("external_ids", []):
                    cur.execute(
                        "INSERT OR IGNORE INTO external_ids (part_num, source, external_id) VALUES (?, ?, ?)",
                        (part_num, source, str(ext_id))
                    )
                    enriched += 1
        time.sleep(DELAY)

    conn.commit()
    return enriched


# ─── Rarity scoring ──────────────────────────────────────────────────────────

def compute_rarity_scores(conn):
    """
    Compute a rarity score for every part+color combination.

    Score formula (0–100, higher = rarer):
    - Base: inverse log of num_sets (fewer sets → higher score)
    - Boost: inverse log of total_quantity
    - Boost: if "retired" (last seen > 3 years ago)
    - Boost: if short production run (few years available)
    """
    cur = conn.cursor()
    current_year = datetime.now().year

    # Get max values for normalization
    max_sets = cur.execute("SELECT MAX(num_sets) FROM part_color_stats").fetchone()[0] or 1
    max_qty = cur.execute("SELECT MAX(total_quantity) FROM part_color_stats").fetchone()[0] or 1

    rows = cur.execute("""
        SELECT part_num, color_id, num_sets, total_quantity, first_year, last_year
        FROM part_color_stats
    """).fetchall()

    print(f"  Computing rarity scores for {len(rows):,} part+color combos...")

    batch = []
    for part_num, color_id, num_sets, total_qty, first_year, last_year in rows:
        # Normalized inverse log scores (0 = common, 1 = rare)
        sets_score = 1.0 - (math.log1p(num_sets) / math.log1p(max_sets))
        qty_score = 1.0 - (math.log1p(total_qty) / math.log1p(max_qty))

        years_available = (last_year - first_year + 1) if first_year and last_year else 1
        is_retired = 1 if last_year and last_year < current_year - 3 else 0

        # Short production boost (available < 3 years)
        short_run_boost = 0.1 if years_available <= 2 else 0.0

        # Retired boost
        retired_boost = 0.1 if is_retired else 0.0

        # Combined score (0–100)
        raw_score = (sets_score * 0.5 + qty_score * 0.3 + short_run_boost + retired_boost)
        rarity_score = round(min(raw_score * 100, 100), 2)

        # Tier
        if rarity_score >= 90:
            tier = "ultra_rare"
        elif rarity_score >= 75:
            tier = "very_rare"
        elif rarity_score >= 50:
            tier = "rare"
        elif rarity_score >= 25:
            tier = "uncommon"
        else:
            tier = "common"

        batch.append((part_num, color_id, rarity_score, tier, num_sets, total_qty, years_available, is_retired))

        if len(batch) >= 50000:
            cur.executemany("""
                INSERT OR REPLACE INTO rarity_scores
                (part_num, color_id, rarity_score, rarity_tier, num_sets, total_qty, years_available, is_retired)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            batch = []

    if batch:
        cur.executemany("""
            INSERT OR REPLACE INTO rarity_scores
            (part_num, color_id, rarity_score, rarity_tier, num_sets, total_qty, years_available, is_retired)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)

    conn.commit()

    # Print distribution
    print("\n  Rarity distribution:")
    for tier in ["common", "uncommon", "rare", "very_rare", "ultra_rare"]:
        count = cur.execute("SELECT COUNT(*) FROM rarity_scores WHERE rarity_tier = ?", (tier,)).fetchone()[0]
        print(f"    {tier:15s} {count:>8,}")

    # Show some examples of ultra-rare
    print("\n  Top 15 ultra-rare part+color combos:")
    for row in cur.execute("""
        SELECT rs.part_num, p.name, c.name AS color, rs.rarity_score,
               rs.num_sets, rs.total_qty, rs.years_available, rs.is_retired
        FROM rarity_scores rs
        JOIN parts p ON rs.part_num = p.part_num
        JOIN colors c ON rs.color_id = c.id
        ORDER BY rs.rarity_score DESC
        LIMIT 15
    """):
        retired = " [retired]" if row[7] else ""
        print(f"    {row[3]:5.1f}  {row[0]:12s}  {row[1][:30]:30s}  {row[2][:20]:20s}  "
              f"sets={row[4]}  qty={row[5]}{retired}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Enrich catalog with Rebrickable API + rarity scores")
    parser.add_argument("--part", help="Enrich a specific part number")
    parser.add_argument("--limit", type=int, default=500, help="Enrich top N most common parts")
    parser.add_argument("--rarity", action="store_true", help="Compute rarity scores (no API needed)")
    args = parser.parse_args()

    conn = get_db()
    ensure_schema(conn)

    if args.rarity:
        print("Computing rarity scores...")
        compute_rarity_scores(conn)
        print("\n✓ Done. Query with: SELECT * FROM rarity_scores ORDER BY rarity_score DESC")

    elif args.part:
        api_key = get_api_key()
        print(f"Enriching part {args.part}...")
        count = enrich_part(api_key, conn, args.part)
        print(f"  Fetched {count} data points.")

        # Show results
        cur = conn.cursor()
        print("\n  External IDs:")
        for row in cur.execute("SELECT source, external_id FROM external_ids WHERE part_num = ?", (args.part,)):
            print(f"    {row[0]:15s}  {row[1]}")

        img = cur.execute("SELECT img_url FROM part_images WHERE part_num = ?", (args.part,)).fetchone()
        if img and img[0]:
            print(f"\n  Image: {img[0]}")

    else:
        api_key = get_api_key()
        cur = conn.cursor()
        parts = cur.execute("""
            SELECT part_num FROM part_stats
            ORDER BY num_sets DESC
            LIMIT ?
        """, (args.limit,)).fetchall()

        print(f"Enriching top {len(parts)} parts with Rebrickable API data...")
        total = 0
        for i, row in enumerate(parts):
            count = enrich_part(api_key, conn, row[0])
            total += count
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i+1}/{len(parts)} parts, {total} data points fetched")

        print(f"\n✓ Done. Fetched {total} data points for {len(parts)} parts.")
        print("\nNow computing rarity scores...")
        compute_rarity_scores(conn)

    conn.close()


if __name__ == "__main__":
    main()
