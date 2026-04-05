# Performance — Large Models

## Snapping with Large Baseplates

When dragging a large object (baseplate, large submodel) with snapping enabled,
Studio checks every stud for connectivity — this causes significant lag.

**Fix:** disable snapping before dragging, then use Connect Tool for precise alignment.

1. Press `G` to toggle snapping off
2. Move the object roughly into position
3. Press `G` again to re-enable snapping
4. Use Connect Tool (toolbar) to snap specific studs together precisely

---

## Collision Detection

Collision detection consumes significant resources on large models.
Toggle it off when doing rough layout, re-enable for final positioning.

Location: toolbar toggle or Edit → Preferences.

**Note:** with Collision Detection off, Studio will not warn about overlapping parts.
The contour outline (ghost shape) visual indicator is also affected — enable detection
to see clipping warnings reliably.

---

## Viewport Render Quality

Reducing viewport quality speeds up navigation without affecting the final render.

Edit → Preferences → Appearance → Render Quality:
- **High** — best visual fidelity, slowest on large models
- **Normal** — good balance for most work
- **Low** — use for 1000+ part models or slow hardware

This setting only affects the viewport — Photo Realistic Render always uses its own quality setting.

---

## General Tips for Large Models

- Use submodels to hide parts of the build you're not currently working on
- Work in orthographic view (Numpad 5) when placing precise parts — less GPU load
- Save frequently (`Ctrl+S`) — Studio auto-saves but crashes can lose recent work
- For 10k+ parts: switch to Low viewport quality and use Geometry Nodes in Blender for renders
