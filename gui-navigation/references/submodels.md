# Submodels — Organization and Advanced Use

Submodels are grouped collections of parts that behave as a single object.
They are the primary tool for organizing large builds in Studio.

---

## Creating and Naming

1. Select the parts to group
2. Press `Ctrl+G` — a submodel is created
3. **Always give it a meaningful name** — double-click the submodel name in the Step List
   - Good: `roof-left`, `wheel-assembly`, `window-frame`
   - Bad: `SubModel Group 9`, `Group 1`

Poor naming makes Instructions Maker and future editing much harder.

---

## What Submodels Enable

| Action | How |
|---|---|
| Move as one unit | Select submodel in Step List → drag |
| Hide/show | Click eye icon next to submodel in Step List |
| Duplicate | `Ctrl+D` on selected submodel |
| Mirror copy | Select → **Copy and Mirror** button (bottom-right corner) |
| Enter to edit | Double-click submodel in viewport |
| Exit edit | Press `Escape` or click outside |

---

## Linked Duplicates

When you duplicate a submodel, both copies are **linked by default** — editing one updates all instances.

**When to use:** symmetric structures (both sides of a vehicle, repeated window assemblies, wheel pairs).

**To unlink a specific instance:** right-click → Submodel → Unlink.
After unlinking, that instance becomes independent and can be edited separately.

---

## Copy and Mirror

The **Copy and Mirror** button (bottom-right corner of viewport) creates a mirrored copy
of the selected submodel across the selected axis.

Use cases:
- Left/right halves of a ship or vehicle
- Symmetric architectural elements
- Wing pairs

**Workflow:** build one half → select its submodel → Copy and Mirror → position the result.

---

## Submodels and Instructions

Before entering Instruction Maker, organize the model into logical submodels:
- Removable roof
- Wheel assemblies
- Window frames
- Engine block

This dramatically simplifies step breakdown. Parts inside a submodel can be further
broken into steps via **View Steps** inside the submodel edit mode.

**Recommended approach for complex models:**
1. Rough breakdown into 3–4 large submodels first
2. Then enter each submodel and detail its internal steps
3. Then assemble the full instruction sequence in Instruction Maker

---

## Submodels and Performance

Large submodels with many parts can slow down viewport navigation.
If performance degrades: Edit → Preferences → Appearance → reduce Render Quality.
This does not affect the final render — only the viewport display.
