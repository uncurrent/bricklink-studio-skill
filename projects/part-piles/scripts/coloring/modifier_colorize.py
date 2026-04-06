#!/usr/bin/env python3
"""
modifier_colorize.py — Recolor parts in an LDR file using a named palette.

Usage:
    python3 modifier_colorize.py <input.ldr> <palette_name> [--seed N] [--output path]

Examples:
    python3 modifier_colorize.py ../Pockets-recipe-1/output/pocket_7.ldr multicolor-1
    python3 modifier_colorize.py input.ldr multicolor-3 --seed 42 --output output/pocket_mc3.ldr

The script:
  1. Reads all part lines (type 1: "1 color x y z R[9] part.dat")
  2. Assigns each part a color drawn from the palette proportions
  3. Writes the recolored LDR file

Compatible with all existing generators and modifiers in Pockets-recipe-1/ and Pockets-receipe-2/.
"""

import sys
import os
import random
import argparse

# Add parent dir so we can import color_palettes from the same folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from color_palettes import get_palette, list_palettes


def build_color_picker(palette, rng):
    """
    Build a weighted random picker from palette colors.
    Returns a callable that returns a random LDraw color ID.
    """
    colors = palette["colors"]
    ids = [c[0] for c in colors]
    weights = [c[1] for c in colors]
    total = sum(weights)
    cumulative = []
    running = 0
    for w in weights:
        running += w / total
        cumulative.append(running)

    def pick():
        r = rng.random()
        for i, threshold in enumerate(cumulative):
            if r <= threshold:
                return ids[i]
        return ids[-1]  # float rounding safety

    return pick


def recolor_ldr(input_path, palette_name, seed=None, output_path=None):
    """
    Read input LDR, recolor parts using the named palette, write output.
    """
    palette = get_palette(palette_name)
    rng = random.Random(seed)
    pick_color = build_color_picker(palette, rng)

    if output_path is None:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "output",
            f"{base}_{palette_name}.ldr",
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    out_lines = []
    recolored = 0
    color_counts = {}

    for line in lines:
        stripped = line.strip()
        # Part lines start with "1 " (LDraw type 1 = part reference)
        if stripped.startswith("1 "):
            tokens = stripped.split()
            if len(tokens) >= 15:
                new_color = pick_color()
                tokens[1] = str(new_color)
                out_lines.append(" ".join(tokens) + "\n")
                recolored += 1
                color_counts[new_color] = color_counts.get(new_color, 0) + 1
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

    # Stats to stderr (pattern: write stats to stderr, data to file)
    print(f"Palette:   {palette_name} — {palette['description']}", file=sys.stderr)
    print(f"Input:     {input_path}", file=sys.stderr)
    print(f"Output:    {output_path}", file=sys.stderr)
    print(f"Recolored: {recolored} parts", file=sys.stderr)
    print(f"Seed:      {seed}", file=sys.stderr)
    print(f"\nColor distribution:", file=sys.stderr)
    for cid, count in sorted(color_counts.items(), key=lambda x: -x[1]):
        pct = count / recolored * 100 if recolored else 0
        print(f"  Color {cid:>5d}: {count:>3d} parts ({pct:5.1f}%)", file=sys.stderr)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Recolor LDR parts using a named color palette."
    )
    parser.add_argument("input", help="Input .ldr file path")
    parser.add_argument("palette", help="Palette name (e.g. multicolor-1)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (default: None)")
    parser.add_argument("--output", "-o", default=None, help="Output .ldr path")
    parser.add_argument("--list", action="store_true", help="List available palettes and exit")

    args = parser.parse_args()

    if args.list:
        print("Available palettes:")
        list_palettes()
        sys.exit(0)

    if not os.path.isfile(args.input):
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    out = recolor_ldr(args.input, args.palette, seed=args.seed, output_path=args.output)
    print(f"\nDone: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
