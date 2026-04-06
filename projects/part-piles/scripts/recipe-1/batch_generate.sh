#!/bin/bash
# batch_generate.sh — Generate N pockets using the full Recipe 1 pipeline
#
# Usage:
#   ./batch_generate.sh [count]    (default: 20)
#
# Each pocket gets a unique seed range for variety.
# Output: output/Pocket N.io

set -e
cd "$(dirname "$0")"

COUNT="${1:-20}"
SEED_SPAN=60       # seeds per pocket
SIZE="medium"

echo "=== Recipe 1: Generating $COUNT pockets ($SIZE) ===" >&2

for i in $(seq 1 "$COUNT"); do
    NAME="Pocket $i"
    SEED_START=$((100 + (i - 1) * SEED_SPAN))
    SEED_END=$((SEED_START + SEED_SPAN))
    LDR="/tmp/r1_p${i}.ldr"
    LDR_FILLED="/tmp/r1_p${i}_filled.ldr"
    LDR_SETTLED="/tmp/r1_p${i}_settled.ldr"
    IO="output/${NAME}.io"

    echo "" >&2
    echo "--- $NAME (seeds $SEED_START–$SEED_END) ---" >&2

    python3 generator_pile.py --name "$NAME" --size "$SIZE" \
        --seeds "$SEED_START" "$SEED_END" -o "$LDR"

    python3 modifier_fill_gaps.py "$LDR" "$LDR_FILLED" --seed "$i"

    python3 modifier_settle_y.py "$LDR_FILLED" "$LDR_SETTLED"

    bash packager_io.sh "$LDR_SETTLED" "$IO"

    rm -f "$LDR" "$LDR_FILLED" "$LDR_SETTLED"
done

echo "" >&2
echo "=== Done: $COUNT pockets in output/ ===" >&2
