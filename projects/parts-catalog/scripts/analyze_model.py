#!/usr/bin/env python3
"""
Model Buildability Analyzer
=============================
Parses a BrickLink Studio .io file and checks every part+color
against the local catalog to assess:
1. Do all part+color combinations actually exist?
2. How common/rare is each combination?
3. How realistic is it for a user to build this from their own collection?

Usage:
    python3 analyze_model.py path/to/model.io
    python3 analyze_model.py path/to/model.ldr
    python3 analyze_model.py --instructions path/to/model.io
"""

import sqlite3
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent / "lego_catalog.db"

# LDraw color ID to name (common ones, for display)
LDRAW_COLORS = {}

# Hardcoded fallback color names for --instructions (no DB needed)
LDRAW_COLOR_NAMES = {
    0: "Black", 1: "Blue", 2: "Green", 3: "Dark Turquoise",
    4: "Red", 5: "Dark Pink", 6: "Brown", 7: "Light Gray",
    8: "Dark Gray", 9: "Light Blue", 10: "Bright Green",
    11: "Light Turquoise", 12: "Salmon", 13: "Pink",
    14: "Yellow", 15: "White", 19: "Tan", 22: "Purple",
    25: "Orange", 26: "Magenta", 27: "Lime", 28: "Dark Tan",
    29: "Bright Pink", 33: "Trans-Dark Blue", 34: "Trans-Green",
    36: "Trans-Red", 41: "Trans-Light Blue", 42: "Trans-Neon Green",
    46: "Trans-Yellow", 47: "Trans-Clear", 70: "Reddish Brown",
    71: "Light Bluish Gray", 72: "Dark Bluish Gray",
    78: "Light Nougat", 84: "Medium Nougat", 85: "Dark Purple",
    272: "Dark Blue", 288: "Dark Green", 308: "Dark Brown",
    320: "Dark Red", 326: "Bright Light Yellow",
    330: "Olive Green", 378: "Sand Green", 379: "Sand Blue",
    484: "Dark Orange",
}


# ─── Instruction parsing ─────────────────────────────────────────────────────

def parse_ldr_steps(content):
    """Parse LDraw content into a list of steps, each step being a list of parts."""
    steps = []
    current = []
    for line in content.split('\n'):
        s = line.strip()
        if s == '0 STEP':
            if current:
                steps.append(current)
            current = []
        elif s.startswith('1 '):
            tokens = s.split()
            if len(tokens) >= 15:
                color_id = int(tokens[1])
                part_num = tokens[14].replace('.dat', '')
                color_name = LDRAW_COLOR_NAMES.get(color_id, f"Color #{color_id}")
                # Extract position for display
                x, y, z = float(tokens[2]), float(tokens[3]), float(tokens[4])
                current.append({
                    'part_num': part_num,
                    'color_id': color_id,
                    'color_name': color_name,
                    'x': x, 'y': y, 'z': z,
                })
    if current:
        steps.append(current)
    return steps


def parse_ins_pages(content):
    """Parse model.ins XML and return page-level instruction metadata."""
    root = ET.fromstring(content)
    pages_info = []

    # Global settings
    setup = root.find('.//PageSetup')
    paper = setup.findtext('PaperType', '?') if setup is not None else '?'
    portrait = setup.findtext('IsPortrait', '?') if setup is not None else '?'

    for page in root.findall('.//Page'):
        page_guid = page.get('GUID', '')
        template = page.get('template', '')
        step = page.find('.//Step')
        step_info = {}
        if step is not None:
            idx = step.get('SerializedIndex')
            preview = step.find('StepPreview')
            if preview is not None:
                scale = (preview.get('cameraScale')
                         or preview.get('DefaultCameraControlInfo_cameraScale', ''))
                angle = (preview.get('cameraAngle')
                         or preview.get('DefaultCameraControlInfo_cameraAngle', ''))
                target_offset = preview.get('targetPosOffset', '')
                target_pos = (preview.get('TargetPos')
                              or preview.get('DefaultCameraControlInfo_TargetPos', ''))
            else:
                scale = angle = target_offset = target_pos = ''
            step_info = {
                'index': int(idx) if idx is not None else None,
                'camera_scale': scale,
                'camera_angle': angle,
                'target_offset': target_offset,
                'target_pos': target_pos,
            }
        pages_info.append({
            'guid': page_guid,
            'template': template,
            'step': step_info,
        })

    return {
        'paper': paper,
        'portrait': portrait,
        'pages': pages_info,
    }


def resolve_part_names(part_nums):
    """Try to resolve part numbers to names using the catalog DB.
    Returns a dict {part_num: name}. Falls back gracefully if DB is missing."""
    names = {}
    if not DB_PATH.exists():
        return names
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        for pnum in part_nums:
            row = cur.execute("SELECT name FROM parts WHERE part_num = ?", (pnum,)).fetchone()
            if row:
                names[pnum] = row['name']
                continue
            # Try without suffix (e.g. 3070b → 3070)
            base = pnum.rstrip('abcdefghijklmnop')
            if base != pnum:
                row = cur.execute("SELECT name FROM parts WHERE part_num = ?", (base,)).fetchone()
                if row:
                    names[pnum] = row['name']
                    continue
            # Try stripping print codes (e.g. 98138pb090 → 98138)
            import re
            m = re.match(r'^(\d+)', pnum)
            if m and m.group(1) != pnum:
                row = cur.execute("SELECT name FROM parts WHERE part_num = ?", (m.group(1),)).fetchone()
                if row:
                    names[pnum] = row['name'] + ' (printed)'
        conn.close()
    except Exception:
        pass
    return names


def show_instructions(filepath):
    """Extract and display the step-by-step instruction layout from a .io file."""
    filepath = Path(filepath)

    if filepath.suffix != '.io':
        print("Error: --instructions only works with .io files (not .ldr)")
        sys.exit(1)

    with zipfile.ZipFile(filepath, 'r') as z:
        names = z.namelist()

        # Parse model.ldr for step content
        ldr_content = None
        for name in ['model.ldr', 'modelv2.ldr']:
            if name in names:
                ldr_content = z.read(name).decode('utf-8-sig')
                break
        if not ldr_content:
            print("Error: No model.ldr found in .io file")
            sys.exit(1)

        steps = parse_ldr_steps(ldr_content)

        # Parse model.ins for page layout (optional)
        ins_data = None
        if 'model.ins' in names:
            ins_content = z.read('model.ins').decode('utf-8-sig')
            ins_data = parse_ins_pages(ins_content)

        # Parse .info
        info = {}
        if '.info' in names:
            import json
            try:
                info = json.loads(z.read('.info').decode('utf-8'))
            except Exception:
                pass

    # ── Resolve part names from catalog DB (optional) ──

    all_part_nums = set()
    for step_parts in steps:
        for p in step_parts:
            all_part_nums.add(p['part_num'])
    part_names = resolve_part_names(all_part_nums)
    has_names = len(part_names) > 0

    # ── Display ──

    total_parts = sum(len(s) for s in steps)

    print(f"\n╔══════════════════════════════════════════════════════════════════╗")
    print(f"║  Building Instructions — {filepath.name:<38s} ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝")
    print(f"\n  Studio version:  {info.get('version', '?')}")
    print(f"  Total parts:     {info.get('total_parts', total_parts)}")
    print(f"  Total steps:     {len(steps)}")

    if ins_data:
        orient = "Portrait" if ins_data['portrait'] == 'True' else "Landscape"
        print(f"  Page layout:     {ins_data['paper']} {orient}")
        print(f"  Instruction pages: {len(ins_data['pages'])}")

    if has_names:
        print(f"  Parts catalog:   ✅ connected ({len(part_names)}/{len(all_part_nums)} parts resolved)")
    else:
        print(f"  Parts catalog:   ⚠️  not found (run build_catalog.py for part descriptions)")
    print()

    # Step-by-step listing
    running_total = 0
    for i, parts in enumerate(steps, 1):
        running_total += len(parts)

        # Camera info from .ins
        camera_note = ""
        if ins_data:
            # Find matching page by step index (0-based in .ins)
            for pg in ins_data['pages']:
                if pg['step'] and pg['step']['index'] == i - 1:
                    s = pg['step']
                    if s['camera_scale']:
                        camera_note = f"  [camera: scale={s['camera_scale']}"
                        if s['camera_angle']:
                            angles = s['camera_angle'].split()
                            if len(angles) == 2:
                                import math
                                pitch = float(angles[0]) * 180 / math.pi
                                yaw = float(angles[1]) * 180 / math.pi
                                camera_note += f"  pitch={pitch:.0f}°  yaw={yaw:.0f}°"
                        camera_note += "]"
                    break

        # Group duplicate parts in this step
        part_counts = defaultdict(int)
        for p in parts:
            key = (p['part_num'], p['color_id'], p['color_name'])
            part_counts[key] += 1

        new_label = f"+{len(parts)}" if len(parts) > 1 else "+1"
        print(f"  ── Step {i:2d}  ({new_label} part{'s' if len(parts) > 1 else ''}, total: {running_total}) {'─' * 30}{camera_note}")

        for (pnum, cid, cname), qty in part_counts.items():
            qty_str = f" ×{qty}" if qty > 1 else "    "
            pname = part_names.get(pnum, '')
            if pname:
                print(f"     {qty_str}  {pnum:<16s}  {cname:<20s}  {pname}")
            else:
                print(f"     {qty_str}  {pnum:<16s}  {cname}")

        print()

    # ── Summary table: parts by color ──
    color_counts = defaultdict(lambda: {'unique': 0, 'total': 0})
    for step_parts in steps:
        seen = set()
        for p in step_parts:
            color_counts[p['color_name']]['total'] += 1
            if p['part_num'] not in seen:
                color_counts[p['color_name']]['unique'] += 1
                seen.add(p['part_num'])

    print(f"  ── Color Summary {'─' * 46}")
    print(f"     {'Color':<25s}  {'Parts':>5s}  {'Pieces':>6s}")
    print(f"     {'─' * 25}  {'─' * 5}  {'─' * 6}")
    for cname, data in sorted(color_counts.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f"     {cname:<25s}  {data['unique']:>5d}  {data['total']:>6d}")
    print(f"     {'─' * 25}  {'─' * 5}  {'─' * 6}")
    print(f"     {'TOTAL':<25s}  {sum(d['unique'] for d in color_counts.values()):>5d}  {total_parts:>6d}")

    # ── Full parts list (unique) ──
    if has_names:
        print(f"\n  ── Parts List {'─' * 49}")
        print(f"     {'Part':<16s}  {'Name':<40s}  {'Colors'}")
        print(f"     {'─' * 16}  {'─' * 40}  {'─' * 20}")
        # Collect unique parts with their colors
        part_colors = defaultdict(set)
        part_qty = defaultdict(int)
        for step_parts in steps:
            for p in step_parts:
                part_colors[p['part_num']].add(p['color_name'])
                part_qty[p['part_num']] += 1
        for pnum in sorted(part_colors.keys()):
            pname = part_names.get(pnum, '???')
            colors = ', '.join(sorted(part_colors[pnum]))
            print(f"     {pnum:<16s}  {pname[:40]:<40s}  {colors}")
        print()


def get_db():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run `python3 build_catalog.py` first.")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def parse_ldr(content):
    """Parse LDraw content and extract BOM (part_num → color_id → count)."""
    parts = defaultdict(lambda: defaultdict(int))
    for line in content.split('\n'):
        line = line.strip()
        if not line or not line.startswith('1 '):
            continue
        tokens = line.split()
        if len(tokens) < 15:
            continue
        color_id = int(tokens[1])
        part_file = tokens[14]
        part_num = part_file.replace('.dat', '')
        parts[part_num][color_id] += 1
    return parts


def parse_io_file(filepath):
    """Parse a .io file (ZIP containing model.ldr)."""
    with zipfile.ZipFile(filepath, 'r') as z:
        # Try model.ldr first, then modelv2.ldr
        for name in ['model.ldr', 'modelv2.ldr']:
            if name in z.namelist():
                with z.open(name) as f:
                    content = f.read().decode('utf-8-sig')
                    return parse_ldr(content)
    print("Error: No model.ldr found in .io file")
    sys.exit(1)


def load_ldraw_colors(conn):
    """Load LDraw color mapping from database."""
    global LDRAW_COLORS
    cur = conn.cursor()
    for row in cur.execute("SELECT id, name, rgb FROM colors"):
        LDRAW_COLORS[row['id']] = {'name': row['name'], 'rgb': row['rgb']}


def analyze_model(filepath):
    """Full analysis of a model file."""
    filepath = Path(filepath)

    # Parse model
    if filepath.suffix == '.io':
        parts = parse_io_file(filepath)
    elif filepath.suffix in ('.ldr', '.mpd'):
        content = filepath.read_text(encoding='utf-8-sig')
        parts = parse_ldr(content)
    else:
        print(f"Error: Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    # Stats
    total_pieces = sum(sum(colors.values()) for colors in parts.values())
    unique_parts = len(parts)
    unique_combos = sum(len(colors) for colors in parts.values())

    conn = get_db()
    load_ldraw_colors(conn)
    cur = conn.cursor()

    print(f"\n╔══════════════════════════════════════════════════════════╗")
    print(f"║  Model Buildability Analysis                             ║")
    print(f"╚══════════════════════════════════════════════════════════╝")
    print(f"\n  File:          {filepath.name}")
    print(f"  Total pieces:  {total_pieces}")
    print(f"  Unique parts:  {unique_parts}")
    print(f"  Part+color combos: {unique_combos}")

    # Check each part+color
    results = []
    missing_parts = []
    missing_colors = []
    not_in_catalog = []

    for part_num in sorted(parts.keys()):
        for color_id in sorted(parts[part_num].keys()):
            qty = parts[part_num][color_id]

            color_name = LDRAW_COLORS.get(color_id, {}).get('name', f'Unknown ({color_id})')
            color_rgb = LDRAW_COLORS.get(color_id, {}).get('rgb', '??????')

            # Check if part exists in catalog
            part_row = cur.execute(
                "SELECT name, part_cat_id FROM parts WHERE part_num = ?",
                (part_num,)
            ).fetchone()

            # Also try without suffix (e.g. 3023b → 3023)
            base_part_num = part_num.rstrip('abcdefghijklmnop')
            if not part_row and base_part_num != part_num:
                part_row = cur.execute(
                    "SELECT name, part_cat_id FROM parts WHERE part_num = ?",
                    (base_part_num,)
                ).fetchone()

            # Try with common suffixes
            if not part_row:
                for suffix in ['a', 'b', 'c', 'p01', 'pr0001']:
                    part_row = cur.execute(
                        "SELECT name, part_cat_id FROM parts WHERE part_num = ?",
                        (part_num + suffix,)
                    ).fetchone()
                    if part_row:
                        break

            if not part_row:
                not_in_catalog.append({
                    'part_num': part_num, 'color_id': color_id,
                    'color_name': color_name, 'qty': qty,
                    'status': 'NOT_IN_CATALOG'
                })
                results.append({
                    'part_num': part_num, 'part_name': f'??? ({part_num})',
                    'color_id': color_id, 'color_name': color_name, 'color_rgb': color_rgb,
                    'qty': qty, 'status': '❌ NOT IN CATALOG',
                    'num_sets': 0, 'total_qty': 0, 'rarity_score': 100, 'rarity_tier': 'unknown'
                })
                continue

            part_name = part_row['name']
            lookup_num = part_num

            # Check if this part+color combo exists
            pcs = cur.execute("""
                SELECT num_sets, total_quantity, first_year, last_year
                FROM part_color_stats
                WHERE part_num = ? AND color_id = ?
            """, (lookup_num, color_id)).fetchone()

            # Try base part num
            if not pcs and base_part_num != part_num:
                pcs = cur.execute("""
                    SELECT num_sets, total_quantity, first_year, last_year
                    FROM part_color_stats
                    WHERE part_num = ? AND color_id = ?
                """, (base_part_num, color_id)).fetchone()
                if pcs:
                    lookup_num = base_part_num

            # Try alternate/mold parts
            if not pcs:
                alternates = cur.execute("""
                    SELECT parent_part_num FROM part_relationships
                    WHERE child_part_num = ? AND rel_type IN ('A', 'M')
                    UNION
                    SELECT child_part_num FROM part_relationships
                    WHERE parent_part_num = ? AND rel_type IN ('A', 'M')
                """, (part_num, part_num)).fetchall()
                for alt in alternates:
                    pcs = cur.execute("""
                        SELECT num_sets, total_quantity, first_year, last_year
                        FROM part_color_stats
                        WHERE part_num = ? AND color_id = ?
                    """, (alt['parent_part_num'], color_id)).fetchone()
                    if pcs:
                        lookup_num = alt['parent_part_num']
                        break

            # Get rarity score
            rarity = cur.execute("""
                SELECT rarity_score, rarity_tier
                FROM rarity_scores
                WHERE part_num = ? AND color_id = ?
            """, (lookup_num, color_id)).fetchone()

            if pcs:
                status = '✅ EXISTS'
                num_sets = pcs['num_sets']
                total_qty = pcs['total_quantity']
                r_score = rarity['rarity_score'] if rarity else -1
                r_tier = rarity['rarity_tier'] if rarity else 'unknown'
            else:
                # Part exists but not in this color
                available_colors = cur.execute("""
                    SELECT c.name FROM part_color_stats pcs
                    JOIN colors c ON pcs.color_id = c.id
                    WHERE pcs.part_num = ?
                    ORDER BY pcs.num_sets DESC LIMIT 5
                """, (lookup_num,)).fetchall()
                alt_colors = ', '.join(r['name'] for r in available_colors)

                status = f'⚠️ COLOR NOT FOUND (try: {alt_colors})'
                missing_colors.append({
                    'part_num': part_num, 'part_name': part_name,
                    'color_id': color_id, 'color_name': color_name,
                    'available': alt_colors, 'qty': qty
                })
                num_sets = 0
                total_qty = 0
                r_score = 100
                r_tier = 'unavailable'

            results.append({
                'part_num': part_num, 'part_name': part_name,
                'color_id': color_id, 'color_name': color_name, 'color_rgb': color_rgb,
                'qty': qty, 'status': status,
                'num_sets': num_sets, 'total_qty': total_qty,
                'rarity_score': r_score, 'rarity_tier': r_tier
            })

    # ═══════════════════════════════════════════════════════════════
    # REPORT — Details first, summary at the end
    # ═══════════════════════════════════════════════════════════════

    # 1. Problem parts — detailed view
    problems = [r for r in results if '⚠️' in r['status'] or '❌' in r['status']]
    if problems:
        print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  ⚠️  PROBLEM PARTS ({len(problems)})")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for r in problems:
            print(f"\n  {r['status']}")
            print(f"    Part:      {r['part_num']} — {r['part_name']}")
            print(f"    Color:     #{r['color_rgb']} {r['color_name']} (LDraw ID: {r['color_id']})")
            print(f"    Qty needed: {r['qty']}")

            if '⚠️' in r['status']:
                lookup = r['part_num']
                base = lookup.rstrip('abcdefghijklmnop')
                available = cur.execute("""
                    SELECT c.name, c.rgb, pcs.num_sets, pcs.total_quantity
                    FROM part_color_stats pcs
                    JOIN colors c ON pcs.color_id = c.id
                    WHERE pcs.part_num = ? OR pcs.part_num = ?
                    ORDER BY pcs.num_sets DESC
                    LIMIT 8
                """, (lookup, base)).fetchall()
                if available:
                    print(f"    This part exists in these colors instead:")
                    for a in available:
                        print(f"      #{a['rgb']}  {a['name'][:25]:25s}  sets={a['num_sets']:4d}  qty={a['total_quantity']:6,}")

            elif '❌' in r['status']:
                print(f"    This part is not in the Rebrickable catalog.")
                print(f"    Likely a printed/decorated part or a very new release.")

    # 2. Rare parts — worth highlighting
    rare_parts = [r for r in results if r['rarity_tier'] in ('rare', 'very_rare', 'ultra_rare')]
    if rare_parts:
        print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  💎 RARE PARTS ({len(rare_parts)})")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        print(f"  {'Part':>10s}  {'Name':40s}  {'Color':25s}  {'Qty':>3s}  {'Sets':>5s}  {'Score':>5s}  {'Tier'}")
        print(f"  {'─'*10}  {'─'*40}  {'─'*25}  {'─'*3}  {'─'*5}  {'─'*5}  {'─'*12}")
        for r in sorted(rare_parts, key=lambda x: x['rarity_score'], reverse=True):
            print(f"  {r['part_num']:>10s}  {r['part_name'][:40]:40s}  "
                  f"#{r['color_rgb']} {r['color_name'][:18]:18s}  "
                  f"{r['qty']:>3d}  {r['num_sets']:>5d}  {r['rarity_score']:>5.1f}  {r['rarity_tier']}")

    # 3. Full BOM table
    print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  📋 FULL BOM ({len(results)} combos, {total_pieces} pieces)")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    print(f"  {'Part':>10s}  {'Name':40s}  {'Color':25s}  {'Qty':>3s}  {'Sets':>5s}  {'TotalQty':>8s}  {'Score':>5s}  {'Tier':12s}  Status")
    print(f"  {'─'*10}  {'─'*40}  {'─'*25}  {'─'*3}  {'─'*5}  {'─'*8}  {'─'*5}  {'─'*12}  {'─'*10}")

    for r in sorted(results, key=lambda x: x['rarity_score'], reverse=True):
        print(f"  {r['part_num']:>10s}  {r['part_name'][:40]:40s}  "
              f"#{r['color_rgb']} {r['color_name'][:18]:18s}  "
              f"{r['qty']:>3d}  {r['num_sets']:>5d}  {r['total_qty']:>8,}  "
              f"{r['rarity_score']:>5.1f}  {r['rarity_tier']:12s}  {r['status'][:10]}")

    # 4. Summary at the end
    exists_count = sum(1 for r in results if r['status'] == '✅ EXISTS')
    color_missing = sum(1 for r in results if '⚠️' in r['status'])
    not_found = sum(1 for r in results if '❌' in r['status'])

    tier_counts = defaultdict(int)
    tier_pieces = defaultdict(int)
    for r in results:
        tier_counts[r['rarity_tier']] += 1
        tier_pieces[r['rarity_tier']] += r['qty']

    easy_pieces = sum(r['qty'] for r in results if r['rarity_tier'] in ('common', 'uncommon'))
    medium_pieces = sum(r['qty'] for r in results if r['rarity_tier'] == 'rare')
    hard_pieces = sum(r['qty'] for r in results if r['rarity_tier'] in ('very_rare', 'ultra_rare', 'unavailable', 'unknown'))

    if total_pieces > 0:
        easy_pct = easy_pieces / total_pieces * 100
        medium_pct = medium_pieces / total_pieces * 100
        hard_pct = hard_pieces / total_pieces * 100
    else:
        easy_pct = medium_pct = hard_pct = 0

    avg_rarity = sum(r['rarity_score'] * r['qty'] for r in results) / total_pieces if total_pieces else 0

    if hard_pct > 30:
        verdict = "🔴 HARD — many rare parts, most users won't have these"
    elif hard_pct > 10:
        verdict = "🟡 MODERATE — some rare parts may need substitution"
    elif avg_rarity > 50:
        verdict = "🟡 MODERATE — uncommon color choices increase difficulty"
    else:
        verdict = "🟢 EASY — most users with a decent collection can build this"

    print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  📊 BUILDABILITY SUMMARY")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n  Catalog check:")
    print(f"    ✅ Part+color exists:        {exists_count}/{unique_combos}")
    print(f"    ⚠️  Part exists, wrong color:  {color_missing}/{unique_combos}")
    print(f"    ❌ Part not in catalog:      {not_found}/{unique_combos}")
    print(f"\n  Rarity distribution:")
    for tier in ['common', 'uncommon', 'rare', 'very_rare', 'ultra_rare', 'unavailable', 'unknown']:
        if tier in tier_counts:
            print(f"    {tier:15s}  {tier_counts[tier]:>3d} combos  ({tier_pieces[tier]:>3d} pieces)")
    print(f"\n  Buildability:")
    print(f"    Average rarity score:  {avg_rarity:.1f} / 100")
    print(f"    Easy to find pieces:   {easy_pieces:>3d} ({easy_pct:.0f}%)")
    print(f"    Medium difficulty:     {medium_pieces:>3d} ({medium_pct:.0f}%)")
    print(f"    Hard to find pieces:   {hard_pieces:>3d} ({hard_pct:.0f}%)")
    print(f"\n  Verdict: {verdict}")

    # Interactive mode
    interactive_menu._filepath = str(filepath)
    interactive_menu(results, missing_colors, not_in_catalog, conn)

    conn.close()


def interactive_menu(results, missing_colors, not_in_catalog, conn):
    """Interactive post-analysis menu."""
    cur = conn.cursor()

    COMMANDS = """
  ── Interactive Mode ──
  Type a command:
    all         Full BOM table (wide format)
    problems    Only ⚠️ and ❌ entries with details
    rare        Only rare / very_rare / ultra_rare parts
    common      Only common / uncommon parts
    part XXXX   Detailed info for a specific part number
    colors      Color summary (which colors are used)
    steps       Step-by-step instruction layout (from .io file)
    quit        Exit
"""

    print(COMMANDS)

    while True:
        try:
            cmd = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        if cmd == 'quit' or cmd == 'q':
            break

        elif cmd == 'all':
            print(f"\n  {'Part':>10s}  {'Name':40s}  {'Color':25s}  {'Qty':>3s}  {'Sets':>5s}  {'TotalQty':>8s}  {'Rarity':>6s}  {'Tier':12s}  Status")
            print(f"  {'─'*10}  {'─'*40}  {'─'*25}  {'─'*3}  {'─'*5}  {'─'*8}  {'─'*6}  {'─'*12}  {'─'*30}")
            for r in sorted(results, key=lambda x: x['rarity_score'], reverse=True):
                print(f"  {r['part_num']:>10s}  {r['part_name'][:40]:40s}  "
                      f"#{r['color_rgb']} {r['color_name'][:18]:18s}  "
                      f"{r['qty']:>3d}  {r['num_sets']:>5d}  {r['total_qty']:>8,}  "
                      f"{r['rarity_score']:>5.1f}  {r['rarity_tier']:12s}  {r['status']}")

        elif cmd == 'problems':
            problems = [r for r in results if '⚠️' in r['status'] or '❌' in r['status']]
            if not problems:
                print("  No problems found — all parts exist in the specified colors!")
                continue

            print(f"\n  ── Problem Parts ({len(problems)}) ──\n")
            for r in problems:
                print(f"  {r['status']}")
                print(f"    Part:  {r['part_num']} — {r['part_name']}")
                print(f"    Color: #{r['color_rgb']} {r['color_name']} (LDraw ID: {r['color_id']})")
                print(f"    Qty needed: {r['qty']}")

                if '⚠️' in r['status']:
                    # Show what colors this part DOES come in
                    lookup = r['part_num']
                    base = lookup.rstrip('abcdefghijklmnop')
                    available = cur.execute("""
                        SELECT c.name, c.rgb, pcs.num_sets, pcs.total_quantity
                        FROM part_color_stats pcs
                        JOIN colors c ON pcs.color_id = c.id
                        WHERE pcs.part_num = ? OR pcs.part_num = ?
                        ORDER BY pcs.num_sets DESC
                        LIMIT 10
                    """, (lookup, base)).fetchall()
                    if available:
                        print(f"    Available in:")
                        for a in available:
                            print(f"      #{a['rgb']}  {a['name'][:25]:25s}  sets={a['num_sets']:4d}  qty={a['total_quantity']:6,}")

                elif '❌' in r['status']:
                    # Try to find similar parts by name
                    print(f"    This part is not in the Rebrickable catalog.")
                    print(f"    It may be a custom/printed part or very new release.")

                print()

        elif cmd == 'rare':
            rare = [r for r in results if r['rarity_tier'] in ('rare', 'very_rare', 'ultra_rare')]
            if not rare:
                print("  No rare parts in this model!")
                continue

            print(f"\n  ── Rare Parts ({len(rare)}) ──\n")
            print(f"  {'Part':>10s}  {'Name':40s}  {'Color':25s}  {'Qty':>3s}  {'Sets':>5s}  {'Score':>5s}  {'Tier':12s}")
            print(f"  {'─'*10}  {'─'*40}  {'─'*25}  {'─'*3}  {'─'*5}  {'─'*5}  {'─'*12}")
            for r in sorted(rare, key=lambda x: x['rarity_score'], reverse=True):
                print(f"  {r['part_num']:>10s}  {r['part_name'][:40]:40s}  "
                      f"#{r['color_rgb']} {r['color_name'][:18]:18s}  "
                      f"{r['qty']:>3d}  {r['num_sets']:>5d}  {r['rarity_score']:>5.1f}  {r['rarity_tier']}")

        elif cmd == 'common':
            common = [r for r in results if r['rarity_tier'] in ('common', 'uncommon')]
            print(f"\n  ── Common/Uncommon Parts ({len(common)}) ──\n")
            print(f"  {'Part':>10s}  {'Name':40s}  {'Color':25s}  {'Qty':>3s}  {'Sets':>5s}  {'Score':>5s}")
            print(f"  {'─'*10}  {'─'*40}  {'─'*25}  {'─'*3}  {'─'*5}  {'─'*5}")
            for r in sorted(common, key=lambda x: x['rarity_score']):
                print(f"  {r['part_num']:>10s}  {r['part_name'][:40]:40s}  "
                      f"#{r['color_rgb']} {r['color_name'][:18]:18s}  "
                      f"{r['qty']:>3d}  {r['num_sets']:>5d}  {r['rarity_score']:>5.1f}")

        elif cmd.startswith('part '):
            part_num = cmd.split(None, 1)[1].strip()
            matching = [r for r in results if r['part_num'] == part_num]
            if not matching:
                # Try partial match
                matching = [r for r in results if part_num in r['part_num']]
            if not matching:
                print(f"  Part '{part_num}' not found in this model.")
                continue

            for r in matching:
                print(f"\n  Part: {r['part_num']} — {r['part_name']}")
                print(f"  Color: #{r['color_rgb']} {r['color_name']} (LDraw ID: {r['color_id']})")
                print(f"  Qty in model: {r['qty']}")
                print(f"  Status: {r['status']}")
                print(f"  Rarity: {r['rarity_score']:.1f} / 100 ({r['rarity_tier']})")
                print(f"  Appears in {r['num_sets']} sets, {r['total_qty']:,} total pieces ever produced")

                # Show all colors this part comes in
                lookup = r['part_num']
                base = lookup.rstrip('abcdefghijklmnop')
                all_colors = cur.execute("""
                    SELECT c.name, c.rgb, pcs.num_sets, pcs.total_quantity,
                           pcs.first_year, pcs.last_year
                    FROM part_color_stats pcs
                    JOIN colors c ON pcs.color_id = c.id
                    WHERE pcs.part_num = ? OR pcs.part_num = ?
                    ORDER BY pcs.num_sets DESC
                """, (lookup, base)).fetchall()

                if all_colors:
                    print(f"\n  All known colors for this part ({len(all_colors)}):")
                    for ac in all_colors:
                        marker = " ◄ USED" if ac['name'] == r['color_name'] else ""
                        print(f"    #{ac['rgb']}  {ac['name'][:25]:25s}  "
                              f"sets={ac['num_sets']:4d}  qty={ac['total_quantity']:6,}  "
                              f"({ac['first_year']}-{ac['last_year']}){marker}")

        elif cmd == 'colors':
            color_summary = defaultdict(lambda: {'count': 0, 'pieces': 0})
            for r in results:
                key = f"#{r['color_rgb']} {r['color_name']}"
                color_summary[key]['count'] += 1
                color_summary[key]['pieces'] += r['qty']

            print(f"\n  ── Colors Used ──\n")
            for color, data in sorted(color_summary.items(), key=lambda x: x[1]['pieces'], reverse=True):
                print(f"  {color:30s}  {data['count']:>2d} parts  {data['pieces']:>3d} pieces")

        elif cmd == 'steps':
            # Need the original filepath — stored in interactive_menu context
            if not hasattr(interactive_menu, '_filepath'):
                print("  Steps info is only available for .io files.")
                continue
            fp = interactive_menu._filepath
            if Path(fp).suffix != '.io':
                print("  Steps info is only available for .io files (not .ldr).")
                continue
            show_instructions(fp)

        else:
            print(f"  Unknown command: '{cmd}'")
            print(COMMANDS)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_model.py <path/to/model.io>")
        print("       python3 analyze_model.py <path/to/model.ldr>")
        print("       python3 analyze_model.py --instructions <path/to/model.io>")
        sys.exit(1)

    if '--instructions' in sys.argv:
        sys.argv.remove('--instructions')
        if len(sys.argv) < 2:
            print("Usage: python3 analyze_model.py --instructions <path/to/model.io>")
            sys.exit(1)
        show_instructions(sys.argv[1])
    else:
        analyze_model(sys.argv[1])
