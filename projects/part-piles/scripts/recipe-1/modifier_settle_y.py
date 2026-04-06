#!/usr/bin/env python3
"""
modifier_settle_y.py — Y-axis compaction (gravity settle) for Brickit Pockets

Takes an existing .ldr file and "drops" each part downward along Y
until it rests on the floor or on top of another part.
Result: a shorter, denser pile with no floating parts.

In LDraw coordinates: positive Y = downward, so "dropping" = increasing Y.

Algorithm:
  1. Parse all parts with positions + rotation-aware AABBs
  2. Define a floor plane at Y_FLOOR
  3. Sort parts by Y descending (lowest parts settle first)
  4. For each part: binary-search the maximum Y it can reach
     without overlapping any already-settled part or going below floor

Usage:
    python3 settle_y.py <input.ldr> <output.ldr> [--floor N]
"""

import math, sys

# ── Known part half-dimensions ────────────────────────────────────────────────
KNOWN_DIMS = {
    "3001.dat": (40,12,20), "3002.dat": (30,12,20), "3003.dat": (20,12,20),
    "3004.dat": (20,12,10), "3010.dat": (40,12,10), "3005.dat": (10,12,10),
    "3023.dat": (20, 4,10), "3022.dat": (20, 4,20), "3020.dat": (40, 4,20),
    "3710.dat": (40, 4,10), "3034.dat": (80, 4,20), "3795.dat": (60, 4,20),
    "3021.dat": (30, 4,20), "3024.dat": (10, 4,10),
    "3039.dat": (20,14,20), "3040b.dat": (20,14,10), "3062b.dat": (10,12,10),
    "14769.dat": (20, 3,20), "4073.dat": (10, 3,10),
    "3069b.dat": (20, 3,10), "3068b.dat": (20, 3,20), "3070b.dat": (10, 3,10),
    "61678.dat": (40, 8,20), "50950.dat": (30, 8,20),
    "32316.dat": (50,10,10), "43093.dat": (8,16,8), "2780.dat": (8,16,8),
    "3648b.dat": (12, 4,12), "3647.dat": (10, 4,10),
}

GAP = 1  # minimal clearance after settling (LDU)


def extents(dims, R):
    a, b, c = dims
    ex = abs(R[0][0])*a + abs(R[0][1])*b + abs(R[0][2])*c
    ey = abs(R[1][0])*a + abs(R[1][1])*b + abs(R[1][2])*c
    ez = abs(R[2][0])*a + abs(R[2][1])*b + abs(R[2][2])*c
    return ex, ey, ez


def overlaps_xz(p1_x, p1_z, p1_ex, p1_ez, p2_x, p2_z, p2_ex, p2_ez):
    """Check if two parts overlap in XZ plane (necessary for Y collision)."""
    return (abs(p1_x - p2_x) < p1_ex + p2_ex + GAP and
            abs(p1_z - p2_z) < p1_ez + p2_ez + GAP)


def max_y_before_collision(part, settled, y_floor):
    """
    Find the maximum Y this part can reach (drop down) without:
      - overlapping any settled part's AABB
      - going below the floor

    Returns the best (highest) Y value for the part center.
    """
    x, _, z, ex, ey, ez = part

    # Floor constraint: part center + ey must not exceed y_floor
    best_y = y_floor - ey

    # Check against each settled part
    for sx, sy, sz, sex, sey, sez in settled:
        # Only relevant if they overlap in XZ
        if not overlaps_xz(x, z, ex, ez, sx, sz, sex, sez):
            continue

        # To avoid Y overlap: |y - sy| >= ey + sey + GAP
        # Part is dropping DOWN (increasing Y), so it approaches from above (lower Y).
        # It must stop when: y + ey + GAP = sy - sey
        # i.e., y = sy - sey - ey - GAP
        y_limit = sy - sey - ey - GAP

        if y_limit < best_y:
            best_y = y_limit

    return best_y


def parse_ldr(path):
    """Parse LDR, return (header_lines, parts).
    parts = list of (line_str, x, y, z, R, ex, ey, ez, part_id)
    """
    header = []
    parts = []

    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("1 "):
                tokens = line.split()
                color = tokens[1]
                x, y, z = float(tokens[2]), float(tokens[3]), float(tokens[4])
                R = [[float(tokens[5 + i*3 + j]) for j in range(3)] for i in range(3)]
                pid = tokens[14]

                dims = KNOWN_DIMS.get(pid, (20, 10, 20))
                ex, ey, ez = extents(dims, R)

                # Store rotation matrix string for output
                r_str = " ".join(tokens[5:14])

                parts.append({
                    "color": color,
                    "x": x, "y": y, "z": z,
                    "R": R, "r_str": r_str,
                    "ex": ex, "ey": ey, "ez": ez,
                    "pid": pid,
                })
            else:
                header.append(line)

    return header, parts


def main():
    if len(sys.argv) < 3:
        print("Usage: settle_y.py <input.ldr> <output.ldr> [--floor N]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Default floor: auto-detect from model (max Y + margin)
    y_floor = None
    if "--floor" in sys.argv:
        idx = sys.argv.index("--floor")
        y_floor = float(sys.argv[idx + 1])

    header, parts = parse_ldr(input_path)
    n = len(parts)
    print(f"Parsed {n} parts from {input_path}", file=sys.stderr)

    # Stats before
    ys_before = [p["y"] for p in parts]
    y_min_before = min(ys_before)
    y_max_before = max(ys_before)
    y_range_before = y_max_before - y_min_before
    print(f"Y range before: {y_min_before:.0f}→{y_max_before:.0f} "
          f"({y_range_before:.0f} LDU ≈ {y_range_before/8:.0f} plates)", file=sys.stderr)

    # Auto floor: slightly below the current lowest point
    if y_floor is None:
        max_ey = max(p["ey"] for p in parts)
        y_floor = y_max_before + max_ey + 20
        print(f"Auto floor: Y={y_floor:.0f}", file=sys.stderr)

    # Sort by Y descending — settle bottom parts first (highest Y = closest to floor)
    parts_sorted = sorted(range(n), key=lambda i: -parts[i]["y"])

    settled = []  # (x, y, z, ex, ey, ez) of settled parts
    new_ys = [None] * n  # new Y values indexed by original order

    for idx in parts_sorted:
        p = parts[idx]
        part_tuple = (p["x"], p["y"], p["z"], p["ex"], p["ey"], p["ez"])

        new_y = max_y_before_collision(part_tuple, settled, y_floor)

        # Don't move part UP — only down (or keep in place if already at floor)
        # Actually we always want to drop, so new_y should be >= original y
        # (higher Y = lower position). If new_y < original y, keep original.
        final_y = max(new_y, p["y"])

        new_ys[idx] = final_y
        settled.append((p["x"], final_y, p["z"], p["ex"], p["ey"], p["ez"]))

    # Stats after
    ys_after = [y for y in new_ys]
    y_min_after = min(ys_after)
    y_max_after = max(ys_after)
    y_range_after = y_max_after - y_min_after
    n_moved = sum(1 for i in range(n) if abs(new_ys[i] - parts[i]["y"]) > 0.5)
    avg_drop = sum(new_ys[i] - parts[i]["y"] for i in range(n)) / n

    print(f"\nSettle results:", file=sys.stderr)
    print(f"  Y range after: {y_min_after:.0f}→{y_max_after:.0f} "
          f"({y_range_after:.0f} LDU ≈ {y_range_after/8:.0f} plates)", file=sys.stderr)
    print(f"  Height reduction: {y_range_before:.0f}→{y_range_after:.0f} LDU "
          f"({(1-y_range_after/max(y_range_before,1))*100:.0f}% shorter)", file=sys.stderr)
    print(f"  Parts moved: {n_moved}/{n}", file=sys.stderr)
    print(f"  Avg drop: {avg_drop:.1f} LDU ({avg_drop/8:.1f} plates)", file=sys.stderr)

    # Write output
    with open(output_path, "w") as f:
        for line in header:
            if line.startswith("0 Pocket ") and "Name" not in line:
                f.write(line + " (settled)\n")
            else:
                f.write(line + "\n")
        for i, p in enumerate(parts):
            f.write(f"1 {p['color']} {p['x']:.2f} {new_ys[i]:.2f} {p['z']:.2f} "
                    f"{p['r_str']} {p['pid']}\n")

    print(f"Written: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
