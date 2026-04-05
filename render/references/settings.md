# Studio Render Settings Reference

## Quality Presets

| Setting | Samples | Use case |
|---|---|---|
| **Draft** | Low | Quick check — composition, colors, rough result |
| **High** | Medium | Most presentations, social media, client previews |
| **Ultra** | High | Final output, print, marketing materials |

Rule of thumb: use Draft while iterating, High for final, Ultra only when truly needed.

---

## Resolution Presets

| Size | Use case |
|---|---|
| 800 × 600 | Quick draft |
| 1920 × 1080 | Presentation, screen, social media |
| 2560 × 1440 | High-res screen |
| 3840 × 2160 (4K) | Print, large format |

Square crops (1:1) useful for app icons and thumbnails — use 1024×1024 or 2048×2048.

---

## Background Options

| Option | Description |
|---|---|
| **White** | Clean product shot look |
| **Transparent** | PNG with alpha channel — for compositing |
| **Environment** | HDRI-based environment (if configured) |
| **Custom color** | Solid color backdrop |

For transparent backgrounds: always save as PNG (JPG does not support alpha).

---

## Lighting

Studio uses a default studio lighting rig. Options:
- **Studio lighting** (default) — even, no harsh shadows, product-shot look
- **Sun lighting** — directional light, outdoor look
- **Custom HDRI** — load an environment map for realistic reflections

For LEGO product shots: Studio lighting with white background is the standard look.

---

## Camera Field of View

Lower FOV (longer focal length) = less perspective distortion = more "catalog photo" look.
Adjust in camera settings or by zooming out and moving camera closer.
Recommended: 50–70mm equivalent focal length for most LEGO shots.

---

## Render Queue

Studio supports queuing multiple renders — useful for overnight batch rendering.

1. Configure render settings for the first view
2. Click **Add to Queue** instead of Render
3. Reposition camera, adjust settings, add to Queue again
4. When all views are queued: click **Render All**

Use for: multiple angles, turntable frames, before/after comparisons.

---

## Stud Logo

The LEGO logo embossed on studs significantly increases render time on stud-heavy models.

Toggle: render dialog → Details → Stud Logo.

| Situation | Recommendation |
|---|---|
| Final product shot, studs visible | Enable |
| Animation frames | Disable — saves time per frame |
| Top-down pile render | Disable — logos barely visible |
| Quick draft | Disable — not worth the time |

---

## Performance Tips

- Reduce resolution for test renders — same quality setting, just smaller
- Draft quality is sufficient for composition checks
- Close other applications before a long render to free memory
- For scenes with 1000+ parts: expect Draft = 1–3 min, High = 10–30 min
- Use Render Queue for multiple angles — set up all views, then walk away
- Disable Stud Logo for animations to cut per-frame render time significantly
