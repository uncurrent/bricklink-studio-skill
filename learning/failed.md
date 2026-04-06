# Failed Patterns & Anti-patterns

Things that don't work, cause errors, or produce bad results.
Check this file before attempting anything unfamiliar.

Format per entry:
```
## YYYY-MM-DD — Short title
**What was tried:** description of the approach
**What happened:** the failure or bad outcome
**Avoid because:** root cause if known
**Alternative:** what to do instead (if known)
```

---

<!-- Failed patterns are appended below this line -->

## [ANTI-PATTERN] 2026-04-04 — Editing model.lxfml has no effect on Studio rendering
**What was tried:** Modifying the XML content of `model.lxfml` inside a .io ZIP archive
**What happened:** Studio viewport didn't change — model appeared exactly as before
**Avoid because:** Studio renders from `model.ldr` (LDraw format), not from LXFML. LXFML is secondary metadata only.
**Alternative:** Always edit `model.ldr`. LXFML can be left unchanged for programmatically generated files.
Source: BrickitStudio/Pockets session notes

## [ANTI-PATTERN] 2026-04-05 — Instructions layout breaks on large models
**What was tried:** Editing step views (camera angle/orientation) on earlier steps in large models
**What happened:** Studio corrupts page layout — steps shift, models misalign
**Avoid because:** Known Studio bug on large models with many steps
**Alternative:** Save file before editing any step view. Make backups at milestone points.
Source: https://rebrickable.com/help/studio-instructions/

## [ANTI-PATTERN] 2026-04-05 — Snapping causes slowdown on large objects
**What was tried:** Dragging large submodels or baseplates with snapping enabled
**What happened:** Every stud checked for connectivity — severe performance drop, UI freezes
**Avoid because:** Studio checks all studs on move; scales badly with part count
**Alternative:** Disable snapping (G), set Grid to Plate Height, use Connect Tool for final attachment
Source: https://brickbanter.com/2020/09/29/bricklink-studio-five-handy-tips/

## [ANTI-PATTERN] 2026-04-05 — Buffer Exchange drag arrows may not work
**What was tried:** Using Buffer Exchange in Instruction Maker — dragging the arrows on the part to set offset
**What happened:** Drag arrows don't respond
**Avoid because:** Known UI bug in Buffer Exchange
**Alternative:** Enter X/Y/Z offset values manually in the input fields in the sidebar
Source: https://open-l-gauge.eu/making-building-instructions-in-studio/

## [ANTI-PATTERN] 2026-04-06 — Opening .io files via macOS `open -a` or double-click fails
**What was tried:** `open -a "/Applications/Studio 2.0/Studio.app" file.io` to open an .io file
**What happened:** Studio shows "cannot open files in Stud.io Format" error dialog
**Avoid because:** Studio does not register as macOS file handler for .io files (Unity build omission).
The file association can be patched via Info.plist (CFBundleDocumentTypes + UTImportedTypeDeclarations),
but the patch is reset on every Studio update.
**Alternative:** Open files from within Studio via File → Open dialog (Cmd+O). For automation use
AppleScript: Cmd+O → Cmd+Shift+G → type absolute path → Enter → Enter.
Source: contribution_studio-macos-io-file-association.md, contribution_model-preview-script.md

## [ANTI-PATTERN] 2026-04-06 — Quartz CGWindowID for screencapture is unreliable
**What was tried:** Python + Quartz framework to find Studio's window ID, then `screencapture -l{windowID}`
**What happened:** Script hung or crashed. With `set -euo pipefail`, the failure killed the whole bash script silently.
**Avoid because:** Process name matching in Quartz may not match "Studio", and failures are silent in pipefail mode.
**Alternative:** Use AppleScript System Events to get window bounds: `position of window 1` + `size of window 1`,
then `screencapture -R x,y,w,h`.
Source: contribution_model-preview-script.md
