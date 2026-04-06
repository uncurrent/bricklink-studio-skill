"""
Color palettes for LEGO part piles (BrickLink Studio / LDraw color IDs).

Each palette is a list of (ldraw_color_id, weight) tuples.
Weight is relative — the modifier normalizes them to probabilities.

Palette types:
  multicolor-*   — diverse, vibrant, many hues
  mono-*         — parts in similar / tonal color range

Color reference: bricklink-studio/bom-export/references/color-ids.md
"""

# ─── LDraw Color ID quick reference ────────────────────────────────
# Solids:
#   0  Black         1  Blue          2  Green         4  Red
#   5  Dark Pink     6  Brown         7  Light Gray    8  Dark Gray
#   9  Light Blue   10  Bright Green  11  Turquoise   13  Pink
#  14  Yellow       15  White         17  Light Green  19  Tan
#  22  Purple       25  Orange        26  Magenta      27  Lime
#  28  Dark Tan     29  Bright Pink   69  Light Flesh  70  Reddish Brown
#  71  Light Bluish Gray   72  Dark Bluish Gray   73  Medium Blue
#  85  Dark Purple   89  Royal Blue (Dark Azure)
# 191  Bright Light Orange  212  Bright Light Blue
# 226  Bright Light Yellow  272  Dark Blue   288  Dark Green
# 308  Dark Brown    320  Dark Red
#
# Transparent:
#  33  Trans Dark Blue   34  Trans Green   36  Trans Red
#  40  Trans White       41  Trans Light Blue   42  Trans Neon Green
#  43  Trans Very Lt Blue  46  Trans Yellow   47  Trans Clear
# ────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════
#  MULTICOLOR PALETTES
# ═══════════════════════════════════════════════════════════════════

MULTICOLOR_1 = {
    "name": "multicolor-1",
    "description": "Rainbow classic — based on Pocket 1 reference (28 colors, natural mix)",
    "colors": [
        # (ldraw_id, weight)  — weights from actual Pocket 1 part counts
        (15,  10),   # White
        (71,   7),   # Light Bluish Gray
        ( 2,   7),   # Green
        ( 4,   6),   # Red
        (14,   6),   # Yellow
        (13,   6),   # Pink
        ( 1,   5),   # Blue
        (27,   4),   # Lime
        (10,   4),   # Bright Green
        ( 8,   3),   # Dark Gray (actually Dark Bluish Gray in Studio)
        (19,   3),   # Tan
        (73,   2),   # Medium Blue
        ( 6,   2),   # Brown
        (25,   2),   # Orange
        (226,  2),   # Bright Light Yellow
        ( 0,   2),   # Black
        (69,   1),   # Light Flesh
        (85,   1),   # Dark Purple
        (89,   1),   # Dark Azure
        (22,   1),   # Purple
        (28,   1),   # Dark Tan
        (29,   1),   # Bright Pink
    ],
}

MULTICOLOR_2 = {
    "name": "multicolor-2",
    "description": "Rainbow warm shift — all hues present, warm colors get extra weight",
    "colors": [
        ( 4,   8),   # Red
        (14,   8),   # Yellow
        (25,   7),   # Orange
        ( 1,   6),   # Blue
        ( 2,   6),   # Green
        (15,   6),   # White
        (13,   5),   # Pink
        (27,   4),   # Lime
        (191,  4),   # Bright Light Orange
        (10,   3),   # Bright Green
        (71,   3),   # Light Bluish Gray
        (226,  3),   # Bright Light Yellow
        (73,   2),   # Medium Blue
        (19,   2),   # Tan
        ( 0,   2),   # Black
        (89,   2),   # Dark Azure
        (29,   2),   # Bright Pink
        ( 6,   1),   # Brown
        (320,  1),   # Dark Red
        (22,   1),   # Purple
    ],
}

MULTICOLOR_3 = {
    "name": "multicolor-3",
    "description": "Rainbow cool shift — all hues present, blues and greens lead",
    "colors": [
        ( 1,   8),   # Blue
        ( 2,   8),   # Green
        (89,   6),   # Dark Azure
        ( 4,   5),   # Red
        (14,   5),   # Yellow
        (15,   6),   # White
        (73,   5),   # Medium Blue
        (10,   5),   # Bright Green
        (27,   4),   # Lime
        (25,   3),   # Orange
        (13,   3),   # Pink
        (71,   3),   # Light Bluish Gray
        (11,   3),   # Turquoise
        (22,   2),   # Purple
        (212,  2),   # Bright Light Blue
        ( 0,   2),   # Black
        (19,   2),   # Tan
        (85,   1),   # Dark Purple
        (29,   1),   # Bright Pink
        (272,  1),   # Dark Blue
    ],
}

MULTICOLOR_4 = {
    "name": "multicolor-4",
    "description": "Rainbow vivid — minimal neutrals, maximum saturation across all hues",
    "colors": [
        ( 4,   7),   # Red
        ( 1,   7),   # Blue
        (14,   7),   # Yellow
        ( 2,   6),   # Green
        (25,   6),   # Orange
        (27,   6),   # Lime
        (89,   5),   # Dark Azure
        (26,   4),   # Magenta
        (10,   4),   # Bright Green
        (13,   4),   # Pink
        (320,  3),   # Dark Red
        (85,   3),   # Dark Purple
        (191,  3),   # Bright Light Orange
        (15,   3),   # White
        (272,  2),   # Dark Blue
        (288,  2),   # Dark Green
        (29,   2),   # Bright Pink
        ( 0,   1),   # Black
        (11,   1),   # Turquoise
    ],
}

MULTICOLOR_5 = {
    "name": "multicolor-5",
    "description": "Rainbow classic LEGO — heavy on the 6 iconic colors with supporting cast",
    "colors": [
        ( 4,   9),   # Red
        ( 1,   9),   # Blue
        (14,   9),   # Yellow
        ( 2,   7),   # Green
        (15,   7),   # White
        ( 0,   5),   # Black
        (25,   4),   # Orange
        (71,   4),   # Light Bluish Gray
        (72,   3),   # Dark Bluish Gray
        (19,   3),   # Tan
        (10,   2),   # Bright Green
        (73,   2),   # Medium Blue
        ( 6,   2),   # Brown
        (27,   2),   # Lime
        (13,   2),   # Pink
        (28,   1),   # Dark Tan
        (320,  1),   # Dark Red
        (272,  1),   # Dark Blue
        (226,  1),   # Bright Light Yellow
    ],
}

MULTICOLOR_6 = {
    "name": "multicolor-6",
    "description": "Rainbow modern — newer LEGO colors (coral, azure, lime) mixed with classics",
    "colors": [
        (89,   7),   # Dark Azure
        (13,   7),   # Pink / Coral
        (27,   6),   # Lime
        (191,  5),   # Bright Light Orange
        ( 4,   5),   # Red
        ( 1,   5),   # Blue
        (14,   5),   # Yellow
        (15,   5),   # White
        (212,  4),   # Bright Light Blue
        (29,   4),   # Bright Pink
        (226,  4),   # Bright Light Yellow
        ( 2,   3),   # Green
        (10,   3),   # Bright Green
        (11,   3),   # Turquoise
        (25,   2),   # Orange
        (71,   2),   # Light Bluish Gray
        (85,   2),   # Dark Purple
        ( 0,   1),   # Black
        (69,   1),   # Light Flesh
        (22,   1),   # Purple
    ],
}

SUNSET_WARM_1 = {
    "name": "sunset-warm-1",
    "description": "Sunset warm — reds, oranges, yellows dominate, cool accents",
    "colors": [
        ( 4,  10),   # Red
        (25,   9),   # Orange
        (14,   8),   # Yellow
        (191,  6),   # Bright Light Orange
        (320,  5),   # Dark Red
        (15,   5),   # White
        (226,  4),   # Bright Light Yellow
        (19,   4),   # Tan
        ( 1,   3),   # Blue (cool accent)
        (29,   3),   # Bright Pink
        (13,   3),   # Pink
        ( 0,   2),   # Black
        (71,   2),   # Light Bluish Gray
        (28,   2),   # Dark Tan
        ( 6,   2),   # Brown
        (27,   1),   # Lime (pop accent)
        (10,   1),   # Bright Green (pop accent)
    ],
}

OCEAN_COOL_1 = {
    "name": "ocean-cool-1",
    "description": "Ocean cool — blues, greens, purples with warm sparks",
    "colors": [
        ( 1,  10),   # Blue
        ( 2,   8),   # Green
        (89,   7),   # Dark Azure
        (73,   6),   # Medium Blue
        (10,   5),   # Bright Green
        (272,  4),   # Dark Blue
        (22,   4),   # Purple
        (85,   4),   # Dark Purple
        (15,   5),   # White
        (212,  3),   # Bright Light Blue
        (11,   3),   # Turquoise
        (27,   3),   # Lime
        (14,   2),   # Yellow (warm spark)
        (71,   2),   # Light Bluish Gray
        ( 0,   2),   # Black
        ( 4,   1),   # Red (warm spark)
        (25,   1),   # Orange (warm spark)
    ],
}

PRIMARY_BOLD_1 = {
    "name": "primary-bold-1",
    "description": "Primary bold — strong primaries (R/G/B/Y) with classic neutrals",
    "colors": [
        ( 4,   9),   # Red
        ( 1,   9),   # Blue
        (14,   9),   # Yellow
        ( 2,   8),   # Green
        (15,   7),   # White
        ( 0,   5),   # Black
        (25,   4),   # Orange
        (71,   4),   # Light Bluish Gray
        (72,   3),   # Dark Bluish Gray
        (10,   3),   # Bright Green
        (73,   2),   # Medium Blue
        (19,   2),   # Tan
        (27,   2),   # Lime
        (13,   1),   # Pink
        (320,  1),   # Dark Red
        (272,  1),   # Dark Blue
    ],
}

PASTEL_PARTY_1 = {
    "name": "pastel-party-1",
    "description": "Pastel party — light tones: lavender, pink, light blue, lime, mint",
    "colors": [
        (212,  9),   # Bright Light Blue
        (29,   8),   # Bright Pink
        (226,  7),   # Bright Light Yellow
        (27,   7),   # Lime
        (17,   6),   # Light Green
        (13,   5),   # Pink
        (15,   5),   # White
        ( 9,   5),   # Light Blue
        (191,  4),   # Bright Light Orange
        (11,   4),   # Turquoise
        (73,   3),   # Medium Blue
        (19,   3),   # Tan
        (71,   3),   # Light Bluish Gray
        (69,   2),   # Light Flesh
        (14,   2),   # Yellow
        ( 1,   1),   # Blue (depth accent)
        ( 2,   1),   # Green (depth accent)
    ],
}

NEON_PUNCH_1 = {
    "name": "neon-punch-1",
    "description": "Neon punch — saturated vivids: magenta, azure, lime, orange, dark red",
    "colors": [
        (26,   9),   # Magenta
        (89,   8),   # Dark Azure
        (27,   8),   # Lime
        (25,   7),   # Orange
        (320,  6),   # Dark Red
        (10,   5),   # Bright Green
        ( 4,   5),   # Red
        (85,   4),   # Dark Purple
        (14,   4),   # Yellow
        (15,   4),   # White
        ( 1,   3),   # Blue
        ( 0,   3),   # Black
        (191,  3),   # Bright Light Orange
        (272,  2),   # Dark Blue
        (288,  2),   # Dark Green
        (72,   2),   # Dark Bluish Gray
    ],
}


# ═══════════════════════════════════════════════════════════════════
#  MONOCHROME / TONAL PALETTES  (to be added after photo reference)
# ═══════════════════════════════════════════════════════════════════

# Placeholder — will be populated from real bag photos
# MONO_BLUE = { ... }
# MONO_RED  = { ... }
# etc.


# ═══════════════════════════════════════════════════════════════════
#  REGISTRY — all palettes accessible by name
# ═══════════════════════════════════════════════════════════════════

ALL_PALETTES = {
    p["name"]: p for p in [
        MULTICOLOR_1,
        MULTICOLOR_2,
        MULTICOLOR_3,
        MULTICOLOR_4,
        MULTICOLOR_5,
        MULTICOLOR_6,
        SUNSET_WARM_1,
        OCEAN_COOL_1,
        PRIMARY_BOLD_1,
        PASTEL_PARTY_1,
        NEON_PUNCH_1,
    ]
}


def get_palette(name):
    """Return palette dict by name, or raise KeyError."""
    if name not in ALL_PALETTES:
        available = ", ".join(sorted(ALL_PALETTES.keys()))
        raise KeyError(f"Unknown palette '{name}'. Available: {available}")
    return ALL_PALETTES[name]


def list_palettes():
    """Print all available palettes with descriptions."""
    for name, pal in sorted(ALL_PALETTES.items()):
        n_colors = len(pal["colors"])
        print(f"  {name:20s} — {pal['description']}  ({n_colors} colors)")
