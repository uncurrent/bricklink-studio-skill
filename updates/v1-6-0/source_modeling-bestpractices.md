# Modeling Best Practices — Stud.io & Blender

## Stud.io: Random Pile of Parts

Stud.io has no built-in physics or scatter tools. The only option is manual part placement:

- **Viewport hotkeys:** R = rotate part, T = move
- **Part replacement:** select part → REPLACE tab on the left → search → double-click
- **Recoloring:** select part → choose color in the right panel
- **Top-down view:** lock the camera from above using the camera button → arrange all parts so the top view looks like a realistic pile
- **Key insight:** parts float in the air at different heights (Y) and arbitrary angles — from the right angle this looks like a heap
- **Export:** LDraw (.ldr/.mpd) for transfer to Blender

## Blender: Realistic Pile of Objects

### Rigid Body Physics (most realistic approach)
1. Add all objects → assign **Rigid Body** (Active)
2. Add a ground plane → **Rigid Body** (Passive)
3. Gravity + run simulation → objects fall and settle physically
4. **Collision Shape:** convex hull (for complex shapes), box (for simple ones)
5. Adjust Friction and Bounciness to match the desired material

### Geometry Nodes (procedural approach)
- **Distribute Points on Faces** → **Instance on Points** → randomize rotation/scale
- Poisson disk sampling for even distribution without overlaps
- Faster to iterate than physics

### Third-party Add-ons
- **MassFX** — paint a stroke and objects fall with rigid body
- **Scatter by KIRI Engine** — "Natural" mode designed specifically for piles
- **Scatter Objects** — paint objects onto a surface with randomization

## Workflow: Stud.io → Blender

The most powerful approach for LEGO visualization:

1. **Stud.io:** build the model → Export → LDraw (.ldr or .mpd)
2. **Blender import** via one of these add-ons:
   - `ExportLDraw` — supports .ldr, .mpd, .l3b
   - `ldr_tools_blender` — optimized for large scenes (100k+ parts), uses instancing
   - `ImportLDraw` — standard importer
3. **In Blender:** apply Rigid Body simulation for natural settling
4. **Render:** Cycles with auto LEGO materials, studs with the standard logo

### For Large Scenes (10k+ parts)
- Use Geometry Nodes instancing
- Display mode set to "Normal" resolution
- Configure stud type separately for performance

## Applicability to Brickit Pockets

Optimal pipeline for generating pocket models:

1. Stud.io — assemble the part set, arrange approximately
2. Export to LDraw
3. In Blender apply Rigid Body physics — parts settle naturally on their own
4. Render top-down view from Blender (Cycles) instead of the built-in Stud.io renderer
5. Result — a photorealistic pile of parts with physically correct settling
