#!/bin/bash
zip -r bricklink-studio.skill bricklink-studio/ -x "*.pyc" -x "*/.DS_Store"
echo "✅ bricklink-studio.skill built"
