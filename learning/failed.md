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
