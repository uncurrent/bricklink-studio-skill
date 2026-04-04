# BrickLink Studio — UI Panels Reference

## Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│  Menu Bar: File / Edit / View / Build / Render / Help   │
├──────────┬──────────────────────────────┬───────────────┤
│  PARTS   │                              │  PROPERTIES   │
│  PALETTE │        3D VIEWPORT           │  PANEL        │
│          │                              │               │
│ [Search] │   (main building area)       │ X / Y / Z     │
│          │                              │ rotation      │
│ Part     │                              │ color         │
│ list     │                              │               │
│          │                              │               │
├──────────┴──────────────────────────────┴───────────────┤
│  STEP PANEL (building instructions timeline)            │
└─────────────────────────────────────────────────────────┘
```

## Panel Descriptions

### Parts Palette (Left)
- Search field at top — accepts Part ID (e.g. `3001`) or name (e.g. `brick 2x4`)
- Categories tree below search
- Drag part from palette to viewport, or click to attach to cursor

### 3D Viewport (Center)
- Left mouse: select / place
- Right mouse: rotate camera
- Middle mouse / scroll: zoom
- `Numpad 1/3/7`: front/side/top view
- `Numpad 5`: toggle perspective/orthographic

### Properties Panel (Right)
- Shows selected part's position (X, Y, Z), rotation, Part ID, color
- Editable fields — type exact values for precision placement

### Step Panel (Bottom)
- Timeline of building steps for instructions
- Click step to navigate to that point in the build
- `+` button adds a new step

## Modal Dialogs to Know

| Dialog | How to trigger | What to do |
|---|---|---|
| New Model | File → New | Choose template or blank |
| Export LDraw | File → Export → LDraw | Set path, click Export |
| Render Settings | Render → Photo Realistic | Set res/quality, click Render |
| Part Properties | Right-click part → Properties | Edit position/color precisely |
