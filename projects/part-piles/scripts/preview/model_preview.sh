#!/bin/bash
# model_preview.sh — Generate preview images of .io files using BrickLink Studio
#
# Opens each .io file in Studio, captures screenshots from 4 angles:
#   - Front (Z projection)
#   - Right (X projection)
#   - Top   (Y projection)
#   - Perspective (45° isometric)
#
# Saves to <filename>_preview/ folder next to each .io file.
#
# Usage:
#   ./model_preview.sh <folder_path>
#   ./model_preview.sh ./Pockets
#
# Requirements:
#   - macOS
#   - BrickLink Studio 2.0 installed
#   - Accessibility permissions for Terminal/shell (System Settings → Privacy → Accessibility)
#
# Tip: Grant accessibility permissions BEFORE running, otherwise AppleScript keystrokes won't work.

set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────────────
STUDIO_APP="Studio"               # macOS app name (Studio.app inside /Applications/Studio 2.0/)
LOAD_WAIT=8                       # seconds to wait for a file to load in Studio
VIEW_SWITCH_WAIT=1.5              # seconds to wait after switching a camera view
ZOOM_FIT_WAIT=1                   # seconds to wait after zoom-to-fit
INTER_FILE_WAIT=2                 # seconds between files
IMG_FORMAT="png"                  # png or jpg
FORCE=false                       # set via --force flag

# ─── Helpers ────────────────────────────────────────────────────────────────

usage() {
    echo "Usage: $0 [--force] <folder_path>"
    echo ""
    echo "Scans <folder_path> for .io files and generates preview images."
    echo "Each file gets a <name>_preview/ folder with 4 screenshots."
    echo ""
    echo "Options:"
    echo "  --force    Regenerate previews even if folder already exists"
    exit 1
}

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

# Bring Studio to front and wait
activate_studio() {
    osascript -e "tell application \"/Applications/Studio 2.0/Studio.app\" to activate" 2>/dev/null || true
    sleep 0.5
}

# Open a file in Studio via File → Open dialog
open_in_studio() {
    local filepath="$1"
    # Convert to absolute path
    [[ "$filepath" != /* ]] && filepath="$(cd "$(dirname "$filepath")" && pwd)/$(basename "$filepath")"

    log "  Opening: $(basename "$filepath")"

    # Make sure Studio is running and in front
    activate_studio
    sleep 1

    # Use AppleScript to open file via File → Open (Cmd+O) + Go To dialog (Cmd+Shift+G)
    osascript <<APPLESCRIPT
        tell application "System Events"
            tell process "Studio"
                set frontmost to true
                delay 0.5

                -- Cmd+O to open file dialog
                keystroke "o" using {command down}
                delay 2

                -- Cmd+Shift+G to open "Go to folder" path input
                keystroke "g" using {command down, shift down}
                delay 1

                -- Type the full file path
                keystroke "$filepath"
                delay 0.5

                -- Press Enter to navigate to the path
                key code 36
                delay 1

                -- Press Enter again to open the file
                key code 36
            end tell
        end tell
APPLESCRIPT

    sleep "$LOAD_WAIT"
}

# Send a keypad key code to Studio (for camera views)
# Mac keypad codes: 1=83, 2=84, 3=85, 4=86, 5=87, 6=88, 7=89
send_keypad() {
    local keycode="$1"
    osascript -e "
        tell application \"System Events\"
            tell process \"$STUDIO_APP\"
                set frontmost to true
                key code $keycode
            end tell
        end tell
    "
    sleep "$VIEW_SWITCH_WAIT"
}

# Send a regular keystroke to Studio
send_keystroke() {
    local key="$1"
    local modifiers="${2:-}"
    if [ -n "$modifiers" ]; then
        osascript -e "
            tell application \"System Events\"
                tell process \"$STUDIO_APP\"
                    set frontmost to true
                    keystroke \"$key\" using {$modifiers}
                end tell
            end tell
        "
    else
        osascript -e "
            tell application \"System Events\"
                tell process \"$STUDIO_APP\"
                    set frontmost to true
                    keystroke \"$key\"
                end tell
            end tell
        "
    fi
}

# Zoom to fit the model in viewport
zoom_to_fit() {
    send_keystroke "0" "command down"
    sleep "$ZOOM_FIT_WAIT"
}

# Capture the Studio window to a file using its position and size
capture_window() {
    local output="$1"
    activate_studio
    sleep 0.3

    # Get window position and size from System Events
    local bounds
    bounds=$(osascript -e "
        tell application \"System Events\"
            tell process \"$STUDIO_APP\"
                set p to position of window 1
                set s to size of window 1
                return (item 1 of p) & \",\" & (item 2 of p) & \",\" & (item 1 of s) & \",\" & (item 2 of s)
            end tell
        end tell
    " 2>/dev/null) || true

    if [ -n "$bounds" ]; then
        # screencapture -R x,y,w,h — capture a specific rectangle
        screencapture -x -o -R"$bounds" "$output"
    else
        log "  ⚠ Could not get window bounds, capturing full screen"
        screencapture -x "$output"
    fi
    sleep 0.3
}

# Close the current file in Studio (Cmd+W)
close_current_file() {
    send_keystroke "w" "command down"
    sleep 1
    # If "Save?" dialog appears, press "Don't Save" (Cmd+D or click)
    osascript -e "
        tell application \"System Events\"
            tell process \"$STUDIO_APP\"
                -- Try to click Don't Save if dialog exists
                try
                    click button \"Don't Save\" of sheet 1 of window 1
                end try
                try
                    click button \"Don't Save\" of window 1
                end try
                -- Also try keystroke for Don't Save (Cmd+D on some dialogs)
                try
                    keystroke \"d\" using {command down}
                end try
            end tell
        end tell
    " 2>/dev/null || true
    sleep 1
}

# Prepare viewport: hide panels, hide ground for clean screenshots
prepare_viewport() {
    log "  Preparing viewport (hiding panels & ground)..."
    # Hide all panels — Cmd+/
    send_keystroke "/" "command down"
    sleep 0.5
    # Hide ground — Cmd+B
    send_keystroke "b" "command down"
    sleep 0.5
    # Deselect all — click empty or Escape
    osascript -e "
        tell application \"System Events\"
            tell process \"$STUDIO_APP\"
                key code 53
            end tell
        end tell
    "
    sleep 0.3
}

# ─── View capture definitions ──────────────────────────────────────────────
# Each view: (name, setup_function)
#
# Keypad key codes:
#   Front=83, Back=84, Left=85, Right=86, Top=87, Bottom=88, Ortho=89
#
# For the 45° perspective view, we rely on Studio's default perspective
# which is typically a nice 3/4 angle. We capture it first before
# switching to orthographic projections.

capture_perspective() {
    local outdir="$1"
    log "  📸 Perspective (45°) — default Studio view..."
    # Studio opens files in a 3/4 perspective view by default.
    # Just zoom to fit and capture — no view switch needed.
    zoom_to_fit
    capture_window "$outdir/perspective_45.$IMG_FORMAT"
}

capture_front() {
    local outdir="$1"
    log "  📸 Front (Z projection)..."
    send_keypad 83   # Keypad 1 = Front
    zoom_to_fit
    capture_window "$outdir/front_Z.$IMG_FORMAT"
}

capture_right() {
    local outdir="$1"
    log "  📸 Right (X projection)..."
    send_keypad 86   # Keypad 4 = Right
    zoom_to_fit
    capture_window "$outdir/right_X.$IMG_FORMAT"
}

capture_top() {
    local outdir="$1"
    log "  📸 Top (Y projection)..."
    send_keypad 87   # Keypad 5 = Top
    zoom_to_fit
    capture_window "$outdir/top_Y.$IMG_FORMAT"
}

# ─── Main ───────────────────────────────────────────────────────────────────

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) FORCE=true; shift ;;
        -h|--help) usage ;;
        -*) echo "Unknown option: $1" >&2; usage ;;
        *) break ;;
    esac
done

if [ $# -lt 1 ]; then
    usage
fi

TARGET_DIR="$1"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: '$TARGET_DIR' is not a directory" >&2
    exit 1
fi

# Find all .io files
IO_FILES=()
while IFS= read -r -d '' f; do
    IO_FILES+=("$f")
done < <(find "$TARGET_DIR" -name "*.io" -type f -print0 | sort -z)

if [ ${#IO_FILES[@]} -eq 0 ]; then
    echo "No .io files found in '$TARGET_DIR'" >&2
    exit 1
fi

log "Found ${#IO_FILES[@]} .io file(s) in: $TARGET_DIR"
log "═══════════════════════════════════════════════════════"

# Ensure Studio is running
log "Launching Studio..."
open -a "/Applications/Studio 2.0/Studio.app"
sleep 5
activate_studio

for io_file in "${IO_FILES[@]}"; do
    filename=$(basename "$io_file" .io)
    filedir=$(dirname "$io_file")
    preview_dir="$filedir/${filename}_preview"

    log ""
    log "Processing: $filename.io"

    # Skip if preview folder already exists (unless --force)
    if [ -d "$preview_dir" ] && [ "$FORCE" = false ]; then
        log "  ⏭ Preview already exists, skipping"
        continue
    fi

    # Create preview directory
    mkdir -p "$preview_dir"

    # Open file in Studio
    open_in_studio "$io_file"

    # Prepare clean viewport
    prepare_viewport

    # Capture all 4 views
    capture_perspective "$preview_dir"
    capture_front "$preview_dir"
    capture_right "$preview_dir"
    capture_top "$preview_dir"

    log "  ✅ Saved to: ${filename}_preview/"

    # Close file before opening next one
    close_current_file

    sleep "$INTER_FILE_WAIT"
done

log ""
log "═══════════════════════════════════════════════════════"
log "Done! Generated previews for ${#IO_FILES[@]} file(s)."
