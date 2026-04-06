# Skill Update Notes — Session 2026-04-05 (P7–P10)

These observations should be merged into the `bricklink-studio` skill files.

---

## → `learning/observations.md` (append)

```
## [UNVERIFIED] 2026-04-05 — Reducing tilt_strength ~0.55× is the key to flat piles
**Context:** Generating flat part piles (Y_MAX ≈ 150–165 LDU) with low overlap using rejection sampling
**Observation:** Reducing tilt_strength by ~0.55× for all part categories (vs the P6 baseline) keeps ey small for plates. A plate lying flat has ey≈4 LDU; standing vertical has ey≈40 LDU. With low tilt, parts fit into compressed Y range without collisions. This insight enabled P8 (6% forced) and is the single most impactful parameter for flat pile aesthetics.
**Reproducible:** yes — confirmed across P8, P10
**Promote to:** patterns.md

## [UNVERIFIED] 2026-04-05 — Gaussian-only beats two-layer system for flat piles
**Context:** Attempting to fill visible top-down gaps by adding a dedicated floor layer with uniform-in-ellipse distribution (P9)
**Observation:** Two-layer system (19 floor plates uniform-in-ellipse + 46 pile parts Gaussian) produced 9% forced vs P8's 6% forced. Floor plates in the same Y space compete with pile parts. Intuition is sound but result is worse than single-strategy Gaussian.
**Reproducible:** yes — confirmed in P9 vs P8 comparison
**Promote to:** failed.md

## [UNVERIFIED] 2026-04-05 — Poisson disk sampling for floor plates doesn't prevent 3D AABB collisions
**Context:** Using Poisson disk (min_dist between XZ centers) for floor plates in P10
**Observation:** Poisson disk guarantees XZ separation but not 3D. Two plates at similar XZ but different Y still collide in AABB check. Best result: 15% forced — worse than Gaussian (8%).
**Reproducible:** yes — P10 attempt 2
**Promote to:** failed.md

## [UNVERIFIED] 2026-04-05 — ~6–8% forced is the practical floor for flat piles with rejection sampling
**Context:** Multiple attempts (P8–P10) to reduce forced placements below 6% in flat configurations
**Observation:** With 65 parts in ~18×13×8 stud flat volume, rejection sampling maxes out at ~6–8% forced. P8 holds the record at 6%. The only escape is Blender rigid body physics (0% interpenetration). Taller piles (P7) can achieve 0% forced by expanding Y space instead.
**Reproducible:** yes — consistent across P8, P9, P10
**Promote to:** patterns.md
```

---

## → `learning/patterns.md` (append when promoted)

```
## 2026-04-05 — Reducing tilt_strength ~0.55× enables flat piles
**Context:** When Y_MAX ≤ 165 LDU (flat pile aesthetic)
**Pattern:** Reduce all tilt_strength values by ~0.55× vs the P6 baseline. This keeps parts near-flat (ey stays small), allowing them to fit in compressed Y range without AABB conflicts. Example values:
  - Large plates 0.18 → 0.10
  - Base plates 0.22–0.25 → 0.12–0.15
  - Bricks 2×4/2×2 0.35 → 0.20
  - Bricks 1×2/1×4 0.40 → 0.25
  - Slopes/accents 0.50–0.55 → 0.30–0.35
  - Technic 0.60–0.70 → 0.40–0.50
**Confirmed:** 3 times (P8, P9 floor layer, P10)
**Sub-skill:** model-generation (part-piles)

## 2026-04-05 — Flat pile overlap floor: ~6–8% with rejection sampling
**Context:** Generating flat dense piles (Y_MAX ≈ 150–165) with 65 parts
**Pattern:** Expect ~6–8% forced placements as the practical minimum. Do not spend iterations trying to push below this — it won't happen with pure rejection sampling. If 0% forced is required for flat piles, use Blender rigid body physics instead.
**Confirmed:** 3 times (P8=6%, P9=9%, P10=8%)
**Sub-skill:** model-generation (part-piles)
```

---

## → `learning/failed.md` (append)

```
## [ANTI-PATTERN] 2026-04-05 — Two-layer system (floor plates + Gaussian pile) for flat piles
**What was tried:** Floor layer: 19 plates with uniform-in-ellipse XZ distribution, near-zero Y. Pile layer: 46 parts with Gaussian XZ. (Pocket 9)
**What happened:** 9% forced — worse than single-strategy Gaussian P8 (6% forced).
**Avoid because:** Floor plates pre-fill the low-Y region. When pile parts are placed afterward, they have less available Y space and more conflicts. The gain in visual oval shape doesn't compensate for the collision increase.
**Alternative:** Stick to single Gaussian distribution for all parts with reduced tilt_strength.

## [ANTI-PATTERN] 2026-04-05 — Poisson disk XZ sampling for floor plates
**What was tried:** Poisson disk sampling (min_dist between XZ centers) for floor plates to prevent floor-floor collisions. (P10 attempt 2)
**What happened:** 15% forced at best — worse than Gaussian (8%).
**Avoid because:** Poisson disk is 2D (XZ only). AABB collision check is 3D. Two plates at similar XZ coordinates but different Y heights still produce 3D AABB overlaps. Poisson disk addresses the wrong dimension.
**Alternative:** Single Gaussian with reduced tilt_strength (P8 approach).

## [ANTI-PATTERN] 2026-04-05 — Increasing parts to 80 in flat Y_MAX=145 configuration
**What was tried:** 80 parts (vs 65) in Y_MAX=145 LDU flat pile. (P10 attempt 1)
**What happened:** 27–48% forced across all seeds.
**Avoid because:** 80 parts × average AABB volume > total pile volume. Physical impossibility for rejection sampling regardless of parameters.
**Alternative:** Keep parts at 65 for flat piles. 80 parts requires Y_MAX ≥ 240 (tall pile) or Blender physics.
```

---

## → `projects/part-piles/guide.md` — update Pockets Overview table

Add to the table:
```
| Pocket 7 | Generated v3+ | 65 | Tight sigma + tall Y_MAX → 0% forced, but too tall |
| Pocket 8 | Generated v3+ | 65 | Reduced tilt + flat Y_MAX → 6% forced ✓ best flat |
| Pocket 9 | Generated v3+ | 65 | Two-layer floor+pile → 9% forced, Z exact match |
| Pocket 10 | Generated v3+ | 65 | P8 approach, SIGMA_Z=33 → 8% forced, Z=12.3 studs |
```

And update algorithm-version in frontmatter: `algorithm-version: v4 (Pocket 8/10 flat pile)`
