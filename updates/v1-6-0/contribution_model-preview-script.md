# Contribution: Model Preview Script (model_preview.sh)

**Chat date:** 2026-04-06
**What was developed:** Automated batch preview generation tool for .io files
**Pockets involved:** None directly — this is a cross-cutting production tool
**Location:** `BrickitStudio/model_preview.sh`

---

## 1. What Was Developed

A bash script (`model_preview.sh`) that automates generating preview images of BrickLink Studio `.io` files. For each `.io` file found in a target folder, it:

1. Opens the file in Studio via AppleScript-driven File → Open dialog
2. Prepares a clean viewport (hides panels with Cmd+/, hides ground with Cmd+B, deselects all with Escape)
3. Captures 4 screenshots:
   - **perspective_45.png** — Studio's default 3/4 perspective view (captured first, before any view switch)
   - **front_Z.png** — Front view (Keypad 1, looking along Z axis)
   - **right_X.png** — Right view (Keypad 4, looking along X axis)
   - **top_Y.png** — Top view (Keypad 5, looking along Y axis)
4. Saves all 4 images into a `{filename}_preview/` folder next to the original `.io` file
5. Closes the file (Cmd+W + dismiss save dialog) and moves to the next

The script supports `--force` flag to regenerate previews even if the `_preview/` folder already exists. Without `--force`, files with existing preview folders are skipped.

**Usage:**
```bash
cd ~/Dev/BrickitStudio
./model_preview.sh ./Pockets-recipe-1
./model_preview.sh --force ./Pockets-recipe-1
./model_preview.sh ./Pockets-recipe-1 && ./model_preview.sh ./Pockets-recipe-2
```

---

## 2. Evolution — Version by Version

### v1: Initial attempt — `open -a` with direct file path
- **Approach:** Used `open -a "Studio 2.0" file.io` to open files directly
- **Problem:** Studio's macOS app name was wrong — script couldn't find "Studio 2.0"
- **Discovery:** The app is installed at `/Applications/Studio 2.0/Studio.app` — the folder is "Studio 2.0" but the actual app binary is "Studio.app"

### v2: Fixed app name — `open -a` with full path
- **Approach:** Changed to `open -a "/Applications/Studio 2.0/Studio.app" file.io`
- **Problem:** Studio showed error: "The document could not be opened. Studio cannot open files in the 'Stud.io Format' format." Studio does NOT support opening `.io` files via macOS `open` command / file association. The user confirmed they always open files from within Studio (File → Open), never by double-clicking.
- **Key discovery:** Studio's `.io` file association is broken or non-existent on macOS. Files must be opened through Studio's own File → Open dialog.

### v3: AppleScript-driven File → Open dialog
- **Approach:** Rewrote `open_in_studio()` to:
  1. Activate Studio (bring to front)
  2. Send Cmd+O to open the File dialog
  3. Send Cmd+Shift+G to open macOS "Go to folder" path input
  4. Type the full absolute file path
  5. Press Enter twice (navigate → open)
- **Also added:** Studio launch at script start (`open -a` to launch the app, then wait 5 seconds before processing files)
- **Status:** File opening now works reliably

### v4: Window capture — Quartz CGWindowID approach
- **Approach:** Used Python + Quartz framework to find Studio's CGWindowID, then `screencapture -l{windowID}`
- **Problem:** Script hung/crashed at the capture step. The Python Quartz code to find the window ID was unreliable — possibly the process name in Quartz didn't match "Studio", or the window wasn't in the expected layer.
- **Key issue:** With `set -euo pipefail`, any failure in the Python subprocess killed the entire script silently

### v5: Perspective view — backtick key failure
- **Approach:** Used AppleScript `key code 50` (backtick) to toggle Studio's perspective mode
- **Problem:** The keystroke didn't register in Studio via AppleScript. Script hung waiting for the view to change.
- **Solution:** Removed the backtick keystroke entirely. Instead, capture Studio's DEFAULT view (which is already a 3/4 perspective) as the first screenshot, before switching to any orthographic projections.
- **Key insight:** Studio opens every file in a nice 3/4 perspective view by default. Capture this first, then switch to ortho views.

### v6: Window capture — System Events bounds approach (current)
- **Approach:** Replaced Quartz with AppleScript System Events to get window position and size, then `screencapture -R x,y,w,h` to capture just that rectangle
- **Status:** Still being tested at time of session end. The approach is cleaner but may still have issues with AppleScript string concatenation for bounds.

---

## 3. What Failed — Specific Approaches Tried and Abandoned

### FAILED: `open -a` for .io files
- **What:** `open -a "Studio 2.0" file.io` or `open -a "/Applications/Studio 2.0/Studio.app" file.io`
- **Why it failed:** Studio does not register as a handler for `.io` files on macOS. Even with the correct app path, Studio shows "cannot open files in Stud.io Format" error dialog.
- **Root cause:** Studio's file association is broken. The user has never been able to open `.io` files by double-clicking — they always use File → Open from within Studio.
- **Alternative:** AppleScript-driven Cmd+O → Cmd+Shift+G → type path → Enter

### FAILED: Quartz CGWindowID for screencapture
- **What:** Python script using `Quartz.CGWindowListCopyWindowInfo()` to find Studio's main window by owner name containing "Studio", then passing the `kCGWindowNumber` to `screencapture -l`
- **Why it failed:** The Python script either couldn't find the window (process name mismatch) or crashed, and with `set -euo pipefail` this killed the entire bash script silently.
- **Alternative:** System Events `position of window 1` + `size of window 1` → `screencapture -R x,y,w,h`

### FAILED: Backtick key (key code 50) for perspective toggle
- **What:** Sending `key code 50` via AppleScript to toggle Studio's perspective mode
- **Why it failed:** The keystroke didn't register in Studio. Likely an issue with how Studio handles this specific key via accessibility API, or the key code differs on non-US keyboard layouts (user has Russian keyboard layout).
- **Alternative:** Don't switch to perspective at all — capture Studio's default 3/4 view before switching to any orthographic projections.

### NOT YET VERIFIED: `screencapture -R` with System Events bounds
- **Status:** Implemented but testing was not completed before session ended
- **Potential issues:** AppleScript string concatenation for bounds format, or `screencapture -R` format mismatch

---

## 4. Confirmed Patterns

### Studio.app lives inside a "Studio 2.0" folder
- **Path:** `/Applications/Studio 2.0/Studio.app`
- **AppleScript process name:** `"Studio"` (not "Studio 2.0")
- **For `open -a` (app launch only):** use full path `/Applications/Studio 2.0/Studio.app`
- **For `tell process`:** use `"Studio"`

### Studio cannot open .io files via macOS open command
- Files must be opened through Studio's own File → Open dialog
- AppleScript automation: Cmd+O → Cmd+Shift+G → type absolute path → Enter → Enter

### Studio's default view is a good 45° perspective
- When Studio opens a file, it shows a 3/4 perspective view
- Capture this FIRST, before sending any numpad view-switch keys
- After switching to orthographic views (Keypad 1/4/5), the perspective is lost

### Clean viewport for screenshots requires three steps
1. `Cmd+/` — hide all panels (toggle)
2. `Cmd+B` — hide ground plane (toggle)
3. `Escape` — deselect all parts (removes selection highlights)
- To RESTORE the UI: press `Cmd+/` again to show panels, `Cmd+B` to show ground

### Camera views via keypad key codes (AppleScript)
- Front (Z): `key code 83` (Keypad 1)
- Back: `key code 84` (Keypad 2)
- Left: `key code 85` (Keypad 3)
- Right (X): `key code 86` (Keypad 4)
- Top (Y): `key code 87` (Keypad 5)
- Bottom: `key code 88` (Keypad 6)
- Orthogonal: `key code 89` (Keypad 7)
- **Note:** These are KEYPAD codes, not number row codes. They work via AppleScript even on keyboards without a physical numpad.

### Zoom to fit after every view switch
- `Cmd+0` (Zoom to Fit) should be sent after every camera view change
- Without this, the model may be off-center or at wrong zoom level

### Ghostty terminal works for AppleScript automation
- Ghostty needs to be added to System Settings → Privacy & Security → Accessibility
- Same requirement as Terminal.app or iTerm2

---

## 5. Parameters Tuned

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| LOAD_WAIT | 8 sec | Time for Studio to fully load a .io file after File → Open. May need increase for complex models. |
| VIEW_SWITCH_WAIT | 1.5 sec | Time after sending a keypad view switch for Studio to rerender. |
| ZOOM_FIT_WAIT | 1 sec | Time after Cmd+0 zoom-to-fit for viewport to settle. |
| INTER_FILE_WAIT | 2 sec | Pause between closing one file and opening the next. |
| File open dialog delays | 2 sec after Cmd+O, 1 sec after Cmd+Shift+G, 0.5 sec after typing path, 1 sec between Enter presses | Empirical — the macOS file dialog is slow, especially the Go To Folder sheet. |

**Not yet tuned (open questions):**
- Whether LOAD_WAIT=8 is enough for large models (100+ parts)
- Whether the bounds-based screencapture works reliably across different window sizes and monitor setups (Retina vs non-Retina)

---

## 6. Scripts Created

### `BrickitStudio/model_preview.sh`
- **Purpose:** Batch generate 4-angle preview images for all .io files in a folder
- **Input:** Folder path as CLI argument
- **Output:** `{filename}_preview/` folders with `perspective_45.png`, `front_Z.png`, `right_X.png`, `top_Y.png`
- **Flags:** `--force` to regenerate existing previews
- **Dependencies:** macOS, BrickLink Studio, Accessibility permissions for terminal app
- **Technique:** Bash + AppleScript (osascript) + screencapture
- **Pipeline position:** Post-generation tool. Run after generating .io files with Recipe 1 or Recipe 2 batch scripts. Useful for QA review of generated pockets without manually opening each file.

---

## 7. Open Questions and Next Steps

### Not yet resolved:
1. **Window capture reliability** — The `screencapture -R` approach with System Events bounds was implemented but not fully tested. May have issues with:
   - Retina displays (coordinates may need 2x scaling)
   - Multiple monitors (window position may be relative to primary display)
   - Studio's title bar / toolbar being included in or excluded from the capture
2. **Backtick key for perspective** — Could potentially work with a different key code or via menu bar access (View → Perspective). Not explored further since the default-view-first approach works.
3. **Studio "Don't Save" dialog** — The close_current_file function tries three approaches to dismiss the save dialog (click button by name, keystroke Cmd+D). Not verified which one actually works in Studio's dialog.

### Discussed but not implemented:
1. **Cropping/trimming** — Auto-crop screenshots to remove empty space around the model (could use ImageMagick `convert -trim`)
2. **Thumbnail generation** — Smaller versions for quick browsing
3. **Parallel processing** — Opening multiple Studio instances (likely not feasible — Studio may only support one instance)
4. **LDView alternative** — LDView has command-line rendering (`LDView model.ldr -SaveSnapshot=output.png`) which would be more reliable than screencapture. Not chosen because user preferred the Studio + screencapture approach. Could be revisited if screencapture proves too fragile.
5. **Python/trimesh rendering** — Fully autonomous rendering by parsing LDraw geometry. Most reliable but significantly more complex to implement.

### Gaps this chat identified in the broader pipeline:
- There is no standard way to quickly QA a batch of generated .io files. This preview script is the first tool for that purpose.
- The preview script could be integrated into the batch generation pipeline (run automatically after `batch_generate.sh` or `batch_generate.py`).
