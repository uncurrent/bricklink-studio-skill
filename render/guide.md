---
name: bricklink-studio/render
description: >
  Render photo-realistic images from BrickLink Studio models.
  Use when user wants: render, photo-realistic image, high quality image, screenshot of model,
  Blender render, visualize model, "сделай рендер", "сфотографируй модель" (Russian),
  "rendrer le modèle", "faire une photo" (French), "render machen", "Foto vom Modell" (German),
  "hacer render", "visualizar modelo" (Spanish), "レンダリングして", "モデルを撮影" (Japanese),
  "渲染模型", "生成图片" (Chinese).
  Requires computer_use for Studio rendering. Blender pipeline works without display if Blender is scripted.
compatibility:
  computer_use_only: studio-render
  any: blender-pipeline-guidance
---

# Render — Sub-skill

> **Language policy:** All entries written to skill files during this session must be in English.
> The user interface may be in any language.

---

## Render paths

Two approaches depending on context:

| Path | Tool required | Quality | Speed |
|---|---|---|---|
| **Studio Photo Realistic** | Computer Use (Cowork) | Good | Fast (30s–5min) |
| **Blender + Cycles** | Computer Use or scripted | Excellent | Slow (minutes–hours) |

Default: use Studio rendering unless user explicitly asks for Blender or needs higher quality.

---

## Studio Photo Realistic Render

### Pre-render checklist

1. Take a screenshot — verify the model is loaded and correct
2. Close panels that block the viewport (Step List, Parts palette) if they obscure composition
3. Position the camera — orbit with `Alt + right-click drag`, zoom with scroll
4. Check for contour-outlined bricks — overlapping parts will render incorrectly (see `gui-navigation/guide.md`)
5. Consider lighting: Studio uses default studio lighting; adjust in Render settings if needed

### Render steps

1. **Render → Photo Realistic Render** (menu bar) or press `F11`
2. In the render dialog, configure settings (see `references/settings.md`)
3. Click **Render** — progress bar appears in the dialog
4. Wait for completion:
   - Draft quality: 30–90 seconds
   - High quality: 2–10 minutes
   - Ultra quality: 10–60 minutes
5. When complete: **File → Save Render** → choose PNG or JPG

### After rendering

1. Take a screenshot of the render result — verify it looks correct
2. If the result is wrong — identify the issue from the table below before re-rendering
3. Save the render file before closing the dialog — it is not auto-saved

---

## Common Render Issues

| Symptom | Cause | Fix |
|---|---|---|
| Bricks appear with holes or gaps | Overlapping parts (clipping) | Fix part positions before rendering |
| Render is completely black | Camera inside a part or far from model | Press `F` to frame model, reposition camera |
| Studs missing or deformed | Low quality setting | Increase quality to High or Ultra |
| Background is wrong color | Background setting in render dialog | Change to White, Transparent, or Environment |
| Parts are wrong color | LDraw color ID mismatch | Verify colors in viewport before rendering |
| Render takes too long | Ultra quality + high resolution | Use High quality and smaller resolution for previews |

---

## Blender Rendering Pipeline

For photorealistic results beyond Studio's capabilities, export to Blender.
See full workflow in `gui-navigation/references/workflows.md` → Workflow 9.

Summary:
1. File → Export → LDraw (.ldr or .mpd)
2. Import into Blender via ExportLDraw or ldr_tools_blender
3. Apply materials (LEGO plastic shader, stud logos)
4. Render with Cycles

Use Blender when:
- Need physically accurate lighting (HDR environment, area lights)
- Need Rigid Body physics for part settling (pile shots)
- Need camera animation or turntable renders
- Studio render quality is insufficient for final output

---

## Reference Files

- `references/settings.md` — Studio render dialog options and recommended values
