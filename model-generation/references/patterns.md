# LDraw Generation Patterns

Ready-made LDraw snippets. Copy and adapt coordinates as needed.
All examples use identity rotation unless noted. Y is inverted (up = negative).

---

## Pattern 1: Straight Wall (1 stud thick, 2×4 bricks)

8 bricks wide, 3 rows tall, color 72 (Dark Bluish Gray)
```
0 // Row 1 (ground, Y=0 = ground level, first brick layer Y=-24)
1 72    0 -24  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72   40 -24  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72   80 -24  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72  120 -24  0 1 0 0 0 1 0 0 0 1 3001.dat

0 // Row 2 (staggered, Y=-48)
1 72  -20 -48  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72   20 -48  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72   60 -48  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72  100 -48  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72  140 -48  0 1 0 0 0 1 0 0 0 1 3001.dat

0 // Row 3 (Y=-72, same as row 1)
1 72    0 -72  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72   40 -72  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72   80 -72  0 1 0 0 0 1 0 0 0 1 3001.dat
1 72  120 -72  0 1 0 0 0 1 0 0 0 1 3001.dat
```

---

## Pattern 2: Floor / Platform (32×32 baseplate + plate layer)

```
0 // 32x32 baseplate at origin
1 28  0 0 0 1 0 0 0 1 0 0 0 1 3867.dat

0 // Optional: plate layer on top (Y=-8)
1 71  0 -8 0 1 0 0 0 1 0 0 0 1 3035.dat
1 71 80 -8 0 1 0 0 0 1 0 0 0 1 3035.dat
```

---

## Pattern 3: Simple Pitched Roof (slope 45°)

4 studs wide span, color 4 (Red)
```
0 // Left slope (facing right, standard orientation)
1 4   0 -96  0 1 0 0 0 1 0 0 0 1 3038.dat

0 // Right slope (rotated 180° around Y)
1 4  40 -96  0 -1 0 0 0 1 0 0 0 -1 3038.dat
```

---

## Pattern 4: Window Opening in Wall

Use 1×1 bricks around the opening + window part:
```
0 // Bricks left of window
1 71  0 -24 0 1 0 0 0 1 0 0 0 1 3004.dat

0 // Window frame
1 15  20 -24 0 1 0 0 0 1 0 0 0 1 3582.dat

0 // Bricks right of window
1 71  60 -24 0 1 0 0 0 1 0 0 0 1 3004.dat
```

---

## Pattern 5: Staircase (3 steps)

Each step: 1 stud deeper, 1 plate higher
```
0 // Step 1 (bottom)
1 71   0  -8  0 1 0 0 0 1 0 0 0 1 3020.dat

0 // Step 2
1 71   0 -16 -20 1 0 0 0 1 0 0 0 1 3020.dat
1 71   0 -24 -20 1 0 0 0 1 0 0 0 1 3020.dat

0 // Step 3
1 71   0 -24 -40 1 0 0 0 1 0 0 0 1 3020.dat
1 71   0 -32 -40 1 0 0 0 1 0 0 0 1 3020.dat
1 71   0 -40 -40 1 0 0 0 1 0 0 0 1 3020.dat
```

---

## Pattern 6: Technic Frame (beams + pins)

Simple 5-hole beam rectangle:
```
0 // Horizontal beams
1 72   0   0  0 0 0 1 0 1 0 -1 0 0 3702.dat
1 72   0 -40  0 0 0 1 0 1 0 -1 0 0 3702.dat

0 // Vertical beams (rotated 90° around Z)
1 72   0   0  0 1 0 0 0 0 -1 0 1 0 3702.dat
1 72 160   0  0 1 0 0 0 0 -1 0 1 0 3702.dat

0 // Pins at corners
1 0    0   0  0 1 0 0 0 1 0 0 0 1 3673.dat
1 0  160   0  0 1 0 0 0 1 0 0 0 1 3673.dat
```

---

## Pattern 7: Minifigure at Position

```
0 // Minifigure (standing, facing forward)
1 0    0 -48  0 1 0 0 0 1 0 0 0 1 970.dat    // hip
1 14   0 -24  0 1 0 0 0 1 0 0 0 1 973.dat    // torso (yellow)
1 14   0   0  0 1 0 0 0 1 0 0 0 1 3626cpb.dat // head
```

---

## Rotation Matrix Quick Reference

| Description | Matrix |
|---|---|
| No rotation (default) | `1 0 0  0 1 0  0 0 1` |
| 90° CW around Y | `0 0 -1  0 1 0  1 0 0` |
| 180° around Y | `-1 0 0  0 1 0  0 0 -1` |
| 90° CCW around Y | `0 0 1  0 1 0  -1 0 0` |
| 90° around X (tilt forward) | `1 0 0  0 0 1  0 -1 0` |
| 45° slope (Z axis) | `1 0 0  0 0.707 -0.707  0 0.707 0.707` |
