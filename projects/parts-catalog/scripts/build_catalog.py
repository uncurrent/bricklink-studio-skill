#!/usr/bin/env python3
"""
LEGO Parts Catalog Builder
===========================
Downloads Rebrickable CSV dumps and builds a SQLite database with:
- Full parts catalog with cross-system ID mapping (BrickLink / LDraw / LEGO)
- Color catalog with all known part+color combinations
- Frequency/rarity metrics based on set appearances
- Ready for BrickLink price enrichment (Phase 2)

Usage:
    python3 build_catalog.py                    # Download data + build DB
    python3 build_catalog.py --skip-download    # Rebuild DB from existing CSVs
    python3 build_catalog.py --download-prebuilt # Download pre-built DB from GitHub Releases
    python3 build_catalog.py --download-prebuilt --force  # Re-download even if up to date
    python3 build_catalog.py --check-update     # Check if a newer DB is available
"""

import csv
import gzip
import io
import json
import os
import sqlite3
import sys
import urllib.request
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_URL = "https://cdn.rebrickable.com/media/downloads/"
DATA_DIR = Path(__file__).parent / "data"
DB_PATH = Path(__file__).parent / "lego_catalog.db"
DB_VERSION_PATH = Path(__file__).parent / ".db_version"

# GitHub Releases — pre-built database
GITHUB_REPO = "uncurrent/lego-parts-catalog"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

CSV_FILES = [
    "colors.csv.gz",
    "parts.csv.gz",
    "part_categories.csv.gz",
    "elements.csv.gz",
    "part_relationships.csv.gz",
    "inventories.csv.gz",
    "inventory_parts.csv.gz",
    "sets.csv.gz",
    "themes.csv.gz",
]

# ─── Download pre-built DB from GitHub Releases ─────────────────────────────

def get_local_version():
    """Read the locally stored DB version tag, or None if not present."""
    if DB_VERSION_PATH.exists():
        return DB_VERSION_PATH.read_text().strip()
    return None


def save_local_version(tag, published_at=""):
    """Save the version tag to .db_version file."""
    info = f"{tag}\n"
    if published_at:
        info += f"published: {published_at}\n"
    DB_VERSION_PATH.write_text(info)


def fetch_latest_release():
    """Fetch latest release info from GitHub API. Returns (release_dict, tag)."""
    req = urllib.request.Request(GITHUB_API, headers={"Accept": "application/vnd.github.v3+json"})
    with urllib.request.urlopen(req) as resp:
        release = json.loads(resp.read().decode())
    return release, release.get("tag_name", "unknown")


def download_prebuilt(force=False):
    """Download the latest pre-built database from GitHub Releases.
    Skips download if local version matches the latest release (unless force=True)."""

    print("  Fetching latest release info...", end=" ", flush=True)
    try:
        release, tag = fetch_latest_release()
    except Exception as e:
        print(f"FAILED: {e}")
        print("\n  Could not fetch release info. Build from scratch instead:")
        print("    python3 build_catalog.py")
        sys.exit(1)

    published_at = release.get("published_at", "")[:10]  # YYYY-MM-DD
    print(f"found {tag} ({published_at})")

    # Check if we already have this version
    local_version = get_local_version()
    if not force and local_version == tag and DB_PATH.exists():
        db_size = DB_PATH.stat().st_size / (1024 * 1024)
        print(f"\n  ✓ Already up to date: {tag} ({db_size:.0f} MB)")
        print(f"  Use --force to re-download anyway.")
        return

    if local_version and local_version != tag:
        print(f"  Updating: {local_version} → {tag}")

    # Find the .db asset
    db_asset = None
    for asset in release.get("assets", []):
        if asset["name"].endswith(".db"):
            db_asset = asset
            break

    if not db_asset:
        print("  Error: No .db file found in latest release assets.")
        sys.exit(1)

    download_url = db_asset["browser_download_url"]
    size_mb = db_asset.get("size", 0) / (1024 * 1024)
    print(f"  Downloading {db_asset['name']} ({size_mb:.0f} MB)...", end=" ", flush=True)

    try:
        urllib.request.urlretrieve(download_url, DB_PATH)
        actual_size = DB_PATH.stat().st_size / (1024 * 1024)
        print(f"OK ({actual_size:.1f} MB)")
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

    # Save version info
    save_local_version(tag, published_at)

    print(f"\n✓ Pre-built database ready at: {DB_PATH}")
    print(f"  Release: {tag} ({published_at})")
    print(f"  Next: run `python3 query_catalog.py` for example queries")


def check_update():
    """Check if a newer version of the pre-built DB is available."""
    local_version = get_local_version()

    print("  Checking for updates...", end=" ", flush=True)
    try:
        release, tag = fetch_latest_release()
    except Exception as e:
        print(f"FAILED: {e}")
        return

    published_at = release.get("published_at", "")[:10]

    if local_version == tag:
        print(f"up to date ({tag})")
    elif local_version:
        print(f"update available: {local_version} → {tag} ({published_at})")
        print(f"  Run: python3 build_catalog.py --download-prebuilt")
    else:
        print(f"latest: {tag} ({published_at}), no local DB found")
        print(f"  Run: python3 build_catalog.py --download-prebuilt")


# ─── Download CSVs ───────────────────────────────────────────────────────────

def download_files():
    """Download all CSV dumps from Rebrickable CDN."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for filename in CSV_FILES:
        filepath = DATA_DIR / filename
        url = BASE_URL + filename

        print(f"  Downloading {filename}...", end=" ", flush=True)
        try:
            urllib.request.urlretrieve(url, filepath)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"OK ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"FAILED: {e}")
            sys.exit(1)

    print("  All files downloaded.\n")


def read_csv_gz(filename):
    """Read a gzipped CSV file and yield rows as dicts."""
    filepath = DATA_DIR / filename
    with gzip.open(filepath, "rt", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        yield from reader


# ─── Database Schema ──────────────────────────────────────────────────────────

SCHEMA = """
-- Color definitions (Rebrickable colors map to BrickLink & LDraw)
CREATE TABLE IF NOT EXISTS colors (
    id              INTEGER PRIMARY KEY,  -- Rebrickable color ID
    name            TEXT NOT NULL,
    rgb             TEXT,                 -- hex RGB
    is_trans        INTEGER DEFAULT 0     -- 1 = transparent
);

-- Part categories (Bricks, Plates, Tiles, etc.)
CREATE TABLE IF NOT EXISTS part_categories (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL
);

-- Parts catalog — main table
CREATE TABLE IF NOT EXISTS parts (
    part_num        TEXT PRIMARY KEY,      -- Rebrickable part number (≈ BrickLink ID)
    name            TEXT NOT NULL,
    part_cat_id     INTEGER REFERENCES part_categories(id),
    part_material   TEXT                   -- Plastic, Rubber, etc.
);

-- Element IDs (LEGO's design+color combo codes)
CREATE TABLE IF NOT EXISTS elements (
    element_id      TEXT PRIMARY KEY,      -- LEGO Element ID
    part_num        TEXT REFERENCES parts(part_num),
    color_id        INTEGER REFERENCES colors(id),
    design_id       TEXT                   -- LEGO Design ID (when differs from part_num)
);

-- Part relationships (alternates, molds, prints, pairs)
CREATE TABLE IF NOT EXISTS part_relationships (
    rel_type        TEXT NOT NULL,         -- A=Alternate, M=Mold, P=Print, B=Sub-Part, T=Pattern
    child_part_num  TEXT NOT NULL,
    parent_part_num TEXT NOT NULL
);

-- Themes (for sets)
CREATE TABLE IF NOT EXISTS themes (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    parent_id       INTEGER REFERENCES themes(id)
);

-- Sets catalog
CREATE TABLE IF NOT EXISTS sets (
    set_num         TEXT PRIMARY KEY,      -- e.g. "75192-1"
    name            TEXT NOT NULL,
    year            INTEGER,
    theme_id        INTEGER REFERENCES themes(id),
    num_parts       INTEGER
);

-- Inventories (a set can have multiple inventory versions)
CREATE TABLE IF NOT EXISTS inventories (
    id              INTEGER PRIMARY KEY,
    version         INTEGER,
    set_num         TEXT REFERENCES sets(set_num)
);

-- Inventory parts — which parts in which colors are in each inventory
CREATE TABLE IF NOT EXISTS inventory_parts (
    inventory_id    INTEGER REFERENCES inventories(id),
    part_num        TEXT,
    color_id        INTEGER,
    quantity        INTEGER DEFAULT 1,
    is_spare        INTEGER DEFAULT 0,
    img_url         TEXT
);

-- ═══════════════════════════════════════════════════════════════════
-- COMPUTED: part+color frequency & rarity metrics
-- ═══════════════════════════════════════════════════════════════════

-- How many sets contain each part+color combo
CREATE TABLE IF NOT EXISTS part_color_stats (
    part_num        TEXT NOT NULL,
    color_id        INTEGER NOT NULL,
    num_sets        INTEGER DEFAULT 0,    -- in how many distinct sets
    total_quantity  INTEGER DEFAULT 0,    -- total pieces across all sets
    first_year      INTEGER,              -- earliest set year
    last_year       INTEGER,              -- latest set year
    PRIMARY KEY (part_num, color_id)
);

-- Overall part stats (across all colors)
CREATE TABLE IF NOT EXISTS part_stats (
    part_num        TEXT PRIMARY KEY,
    num_colors      INTEGER DEFAULT 0,    -- how many colors this part comes in
    num_sets        INTEGER DEFAULT 0,    -- how many sets contain this part (any color)
    total_quantity  INTEGER DEFAULT 0,    -- total pieces across all sets
    first_year      INTEGER,
    last_year       INTEGER
);

-- BrickLink price data (placeholder for Phase 2 enrichment)
CREATE TABLE IF NOT EXISTS bricklink_prices (
    part_num        TEXT NOT NULL,
    color_id        INTEGER NOT NULL,
    avg_price       REAL,                 -- average sale price (USD)
    min_price       REAL,
    max_price       REAL,
    num_lots        INTEGER,              -- how many lots for sale
    total_qty       INTEGER,              -- total pieces for sale
    fetched_at      TEXT,                 -- ISO timestamp
    PRIMARY KEY (part_num, color_id)
);
"""

INDEXES = """
CREATE INDEX IF NOT EXISTS idx_parts_cat ON parts(part_cat_id);
CREATE INDEX IF NOT EXISTS idx_elements_part ON elements(part_num);
CREATE INDEX IF NOT EXISTS idx_elements_color ON elements(color_id);
CREATE INDEX IF NOT EXISTS idx_inv_set ON inventories(set_num);
CREATE INDEX IF NOT EXISTS idx_invparts_inv ON inventory_parts(inventory_id);
CREATE INDEX IF NOT EXISTS idx_invparts_part ON inventory_parts(part_num);
CREATE INDEX IF NOT EXISTS idx_invparts_color ON inventory_parts(color_id);
CREATE INDEX IF NOT EXISTS idx_invparts_partcolor ON inventory_parts(part_num, color_id);
CREATE INDEX IF NOT EXISTS idx_sets_year ON sets(year);
CREATE INDEX IF NOT EXISTS idx_sets_theme ON sets(theme_id);
CREATE INDEX IF NOT EXISTS idx_pcs_sets ON part_color_stats(num_sets);
CREATE INDEX IF NOT EXISTS idx_ps_sets ON part_stats(num_sets);
CREATE INDEX IF NOT EXISTS idx_rel_child ON part_relationships(child_part_num);
CREATE INDEX IF NOT EXISTS idx_rel_parent ON part_relationships(parent_part_num);
"""


# ─── Load data ────────────────────────────────────────────────────────────────

def build_database():
    """Build SQLite database from downloaded CSV files."""

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=OFF")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA cache_size=-200000")  # 200MB cache
    cur = conn.cursor()

    # Create schema
    cur.executescript(SCHEMA)

    # --- Colors ---
    print("  Loading colors...", end=" ", flush=True)
    rows = list(read_csv_gz("colors.csv.gz"))
    cur.executemany(
        "INSERT OR IGNORE INTO colors (id, name, rgb, is_trans) VALUES (?, ?, ?, ?)",
        [(int(r["id"]), r["name"], r["rgb"], r.get("is_trans", "f") in ("t", "True", "1")) for r in rows]
    )
    print(f"{len(rows)} colors")

    # --- Part categories ---
    print("  Loading part categories...", end=" ", flush=True)
    rows = list(read_csv_gz("part_categories.csv.gz"))
    cur.executemany(
        "INSERT OR IGNORE INTO part_categories (id, name) VALUES (?, ?)",
        [(int(r["id"]), r["name"]) for r in rows]
    )
    print(f"{len(rows)} categories")

    # --- Parts ---
    print("  Loading parts...", end=" ", flush=True)
    count = 0
    batch = []
    for r in read_csv_gz("parts.csv.gz"):
        batch.append((r["part_num"], r["name"], int(r["part_cat_id"]), r.get("part_material", "")))
        count += 1
        if len(batch) >= 10000:
            cur.executemany("INSERT OR IGNORE INTO parts (part_num, name, part_cat_id, part_material) VALUES (?, ?, ?, ?)", batch)
            batch = []
    if batch:
        cur.executemany("INSERT OR IGNORE INTO parts (part_num, name, part_cat_id, part_material) VALUES (?, ?, ?, ?)", batch)
    print(f"{count} parts")

    # --- Elements (LEGO Element IDs → part+color mapping) ---
    print("  Loading elements...", end=" ", flush=True)
    count = 0
    batch = []
    for r in read_csv_gz("elements.csv.gz"):
        batch.append((r["element_id"], r["part_num"], int(r["color_id"]), r.get("design_id", "")))
        count += 1
        if len(batch) >= 10000:
            cur.executemany("INSERT OR IGNORE INTO elements (element_id, part_num, color_id, design_id) VALUES (?, ?, ?, ?)", batch)
            batch = []
    if batch:
        cur.executemany("INSERT OR IGNORE INTO elements (element_id, part_num, color_id, design_id) VALUES (?, ?, ?, ?)", batch)
    print(f"{count} elements")

    # --- Part relationships ---
    print("  Loading part relationships...", end=" ", flush=True)
    count = 0
    batch = []
    for r in read_csv_gz("part_relationships.csv.gz"):
        batch.append((r["rel_type"], r["child_part_num"], r["parent_part_num"]))
        count += 1
        if len(batch) >= 10000:
            cur.executemany("INSERT OR IGNORE INTO part_relationships (rel_type, child_part_num, parent_part_num) VALUES (?, ?, ?)", batch)
            batch = []
    if batch:
        cur.executemany("INSERT OR IGNORE INTO part_relationships (rel_type, child_part_num, parent_part_num) VALUES (?, ?, ?)", batch)
    print(f"{count} relationships")

    # --- Themes ---
    print("  Loading themes...", end=" ", flush=True)
    rows = list(read_csv_gz("themes.csv.gz"))
    cur.executemany(
        "INSERT OR IGNORE INTO themes (id, name, parent_id) VALUES (?, ?, ?)",
        [(int(r["id"]), r["name"], int(r["parent_id"]) if r.get("parent_id") else None) for r in rows]
    )
    print(f"{len(rows)} themes")

    # --- Sets ---
    print("  Loading sets...", end=" ", flush=True)
    count = 0
    batch = []
    for r in read_csv_gz("sets.csv.gz"):
        batch.append((r["set_num"], r["name"], int(r["year"]), int(r["theme_id"]), int(r["num_parts"])))
        count += 1
        if len(batch) >= 10000:
            cur.executemany("INSERT OR IGNORE INTO sets (set_num, name, year, theme_id, num_parts) VALUES (?, ?, ?, ?, ?)", batch)
            batch = []
    if batch:
        cur.executemany("INSERT OR IGNORE INTO sets (set_num, name, year, theme_id, num_parts) VALUES (?, ?, ?, ?, ?)", batch)
    print(f"{count} sets")

    # --- Inventories ---
    print("  Loading inventories...", end=" ", flush=True)
    rows = list(read_csv_gz("inventories.csv.gz"))
    cur.executemany(
        "INSERT OR IGNORE INTO inventories (id, version, set_num) VALUES (?, ?, ?)",
        [(int(r["id"]), int(r["version"]), r["set_num"]) for r in rows]
    )
    print(f"{len(rows)} inventories")

    # --- Inventory parts (largest table — millions of rows) ---
    print("  Loading inventory parts (this may take a minute)...", end=" ", flush=True)
    count = 0
    batch = []
    for r in read_csv_gz("inventory_parts.csv.gz"):
        batch.append((
            int(r["inventory_id"]),
            r["part_num"],
            int(r["color_id"]),
            int(r["quantity"]),
            1 if r.get("is_spare", "f") in ("t", "True", "1") else 0,
            r.get("img_url", ""),
        ))
        count += 1
        if len(batch) >= 50000:
            cur.executemany(
                "INSERT INTO inventory_parts (inventory_id, part_num, color_id, quantity, is_spare, img_url) VALUES (?, ?, ?, ?, ?, ?)",
                batch
            )
            batch = []
    if batch:
        cur.executemany(
            "INSERT INTO inventory_parts (inventory_id, part_num, color_id, quantity, is_spare, img_url) VALUES (?, ?, ?, ?, ?, ?)",
            batch
        )
    print(f"{count} rows")

    conn.commit()

    # --- Create indexes ---
    print("  Creating indexes...", end=" ", flush=True)
    cur.executescript(INDEXES)
    print("OK")

    # --- Compute part+color stats ---
    print("  Computing part+color frequency stats...", end=" ", flush=True)
    cur.execute("""
        INSERT OR REPLACE INTO part_color_stats (part_num, color_id, num_sets, total_quantity, first_year, last_year)
        SELECT
            ip.part_num,
            ip.color_id,
            COUNT(DISTINCT s.set_num) AS num_sets,
            SUM(ip.quantity) AS total_quantity,
            MIN(s.year) AS first_year,
            MAX(s.year) AS last_year
        FROM inventory_parts ip
        JOIN inventories inv ON ip.inventory_id = inv.id
        JOIN sets s ON inv.set_num = s.set_num
        WHERE ip.is_spare = 0
        GROUP BY ip.part_num, ip.color_id
    """)
    pcs_count = cur.execute("SELECT COUNT(*) FROM part_color_stats").fetchone()[0]
    print(f"{pcs_count} combinations")

    # --- Compute overall part stats ---
    print("  Computing overall part stats...", end=" ", flush=True)
    cur.execute("""
        INSERT OR REPLACE INTO part_stats (part_num, num_colors, num_sets, total_quantity, first_year, last_year)
        SELECT
            part_num,
            COUNT(DISTINCT color_id) AS num_colors,
            SUM(num_sets) AS num_sets,
            SUM(total_quantity) AS total_quantity,
            MIN(first_year) AS first_year,
            MAX(last_year) AS last_year
        FROM part_color_stats
        GROUP BY part_num
    """)
    ps_count = cur.execute("SELECT COUNT(*) FROM part_stats").fetchone()[0]
    print(f"{ps_count} parts with stats")

    conn.commit()

    # --- Summary ---
    print("\n  ════════════════════════════════════════")
    print("  DATABASE SUMMARY")
    print("  ════════════════════════════════════════")
    for table in ["colors", "part_categories", "parts", "elements", "part_relationships",
                   "themes", "sets", "inventories", "inventory_parts", "part_color_stats", "part_stats"]:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:25s} {count:>10,}")

    db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"\n  Database size: {db_size_mb:.1f} MB")
    print(f"  Location: {DB_PATH}")

    conn.close()


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    skip_download = "--skip-download" in sys.argv
    prebuilt = "--download-prebuilt" in sys.argv
    force = "--force" in sys.argv
    do_check = "--check-update" in sys.argv

    print("╔══════════════════════════════════════════╗")
    print("║   LEGO Parts Catalog Builder             ║")
    print("╚══════════════════════════════════════════╝\n")

    if do_check:
        check_update()
        sys.exit(0)

    if prebuilt:
        print("Downloading pre-built database from GitHub Releases...\n")
        download_prebuilt(force=force)
        sys.exit(0)

    if not skip_download:
        print("Step 1: Downloading Rebrickable CSV dumps...")
        download_files()
    else:
        print("Step 1: Skipping download (using existing CSVs)\n")

    print("Step 2: Building SQLite database...")
    build_database()

    print("\n✓ Done! Your catalog is ready.")
    print("  Next: run `python3 query_catalog.py` for example queries")
