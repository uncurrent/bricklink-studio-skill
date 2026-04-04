#!/bin/bash
zip -r bricklink-studio.skill . \
  -x ".git/*" -x ".github/*" \
  -x "build.sh" -x "*.skill" \
  -x "*.pyc" -x "*.DS_Store"
echo "✅ bricklink-studio.skill built"
