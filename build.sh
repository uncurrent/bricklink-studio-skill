#!/bin/bash
# Remove old archive first — zip -r only updates, leaving stale entries from deleted folders
rm -f bricklink-studio.skill
zip -r bricklink-studio.skill . \
  -x ".git/*" -x ".github/*" \
  -x "build.sh" -x "*.skill" \
  -x "*.pyc" -x "*.DS_Store" \
  -x "updates/*"
echo "✅ bricklink-studio.skill built"
