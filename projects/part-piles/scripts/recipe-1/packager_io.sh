#!/bin/bash
# packager_io.sh — Package a .ldr file as a Stud.io .io file
#
# Usage:
#   ./packager_io.sh <input.ldr> <output.io> [total_parts]
#
# Example:
#   ./packager_io.sh /tmp/pile.ldr "Pockets/Pocket 15.io" 91

set -e

INPUT="$1"
OUTPUT="$2"
TOTAL_PARTS="${3:-66}"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: $0 <input.ldr> <output.io> [total_parts]" >&2
    exit 1
fi

# Make paths absolute so they survive cd into tmpdir
[[ "$INPUT" != /* ]] && INPUT="$(pwd)/$INPUT"
[[ "$OUTPUT" != /* ]] && OUTPUT="$(pwd)/$OUTPUT"
mkdir -p "$(dirname "$OUTPUT")"

TMPDIR=$(mktemp -d)
cp "$INPUT" "$TMPDIR/model.ldr"
echo "{\"version\":\"2.26.3_1\",\"total_parts\":${TOTAL_PARTS},\"parts_db_version\":215}" > "$TMPDIR/.info"
echo '[]' > "$TMPDIR/errorPartList.err"

TMPZIP=$(mktemp).io
cd "$TMPDIR" && zip -r "$TMPZIP" model.ldr .info errorPartList.err > /dev/null
cp "$TMPZIP" "$OUTPUT"

rm -rf "$TMPDIR" "$TMPZIP"
echo "Packaged: $OUTPUT ($TOTAL_PARTS parts)" >&2
