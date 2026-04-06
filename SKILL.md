---
name: bricklink-studio
description: >
  Master skill for working with BrickLink Studio — LEGO digital modeling software.
  Use this skill whenever the user mentions: BrickLink, Studio, LEGO modeling, building instructions,
  LDraw files (.ldr, .mpd), LEGO parts lists, BOM for purchasing, rendering LEGO models,
  or any task involving designing or analyzing LEGO constructions.
  This skill routes to the appropriate sub-skill based on the task and available tools.
compatibility:
  any: ldraw-format, model-generation, bom-export
  computer_use_only: gui-navigation, render
---

# BrickLink Studio — Master Skill

BrickLink Studio is a free LEGO digital design application. This skill covers four domains.
Read this file first, then load the relevant sub-skill(s).

---

## Session Startup Checklist

At the start of every session, before any task:
1. Read `learning/patterns.md` — apply confirmed general patterns
2. Read `learning/failed.md` — know what to avoid generally
3. Check `projects/_INDEX.md` — if the task matches a known project type, load that project's files:
   - `projects/<name>/guide.md` — project constraints and workflow
   - `projects/<name>/patterns.md` — project-specific confirmed patterns (override general ones)
   - `projects/<name>/failed.md` — project-specific anti-patterns
4. Route to the correct sub-skill (see Routing Logic below)
5. At session end — run the **Session Auto-Summary Protocol**

**Two-level knowledge:**
- `learning/` — general, applies to all Studio work
- `projects/<name>/` — specific to one project type; takes precedence when loaded

---

## Core Principle: Script-First Development

This skill produces **scripts as primary artifacts**, not just answers or one-off commands.

1. **Write scripts, not commands.** When a task takes more than 3 tool calls or will likely be repeated, write a script. Save it. Name it clearly.

2. **Save every useful script.** After a script is written and works:
   - Save it to the project's `scripts/` folder
   - Add a docstring with: purpose, inputs, outputs, usage example
   - Update the project's `guide.md` scripts reference section

3. **Bind scripts to recipes.** If a script is part of a known pipeline, reference it in the recipe file. If it creates a new capability, consider whether it starts a new recipe or extends an existing one.

4. **Catalog what you build.** At the end of a session, if new scripts were created:
   - List them in the session summary
   - Note which recipe they belong to (or if they're standalone utilities)
   - Update `patterns.md` if a new reusable pattern emerged

5. **Prefer recipes over improvisation.** When the user asks to generate something that matches an existing recipe, **use the recipe**. Don't reinvent the pipeline. If the recipe needs modification, fork it — don't silently deviate.

6. **Experiments graduate to recipes.** When an experimental script proves itself:
   - Clean it up (docstring, CLI args, error handling)
   - Move from workspace/archive to `scripts/`
   - Write a recipe file or update an existing one
   - Mark the experiment as "graduated" in `observations.md`

---

## Compatibility Matrix

| Sub-skill | claude.ai chat | Claude Code | API / other models | Cowork (Computer Use) |
|---|---|---|---|---|
| `ldraw-format` | ✅ | ✅ | ✅ | ✅ |
| `model-generation` | ✅ | ✅ | ✅ | ✅ |
| `bom-export` | ✅ | ✅ | ✅ | ✅ |
| `knowledge` | ✅ | ✅ | ✅ | ✅ |
| `gui-navigation` | ❌ | ❌ | ❌ | ✅ only |
| `render` | ❌ | ❌ | ❌ | ✅ only |

**Rule:** If `computer_use` / `bash_tool` with display access is NOT available — skip `gui-navigation` and `render` entirely.
Work via LDraw text format instead.

---

## Routing Logic

Read the user's request, then load the appropriate sub-skill(s):

Trigger phrases below are examples in multiple languages — the skill works regardless of user language.
All skill file content is always written in English.

| User intent | Sub-skill to load |
|---|---|
| Open Studio, click, build in GUI / "Открой Studio" (RU) / "ouvre Studio" (FR) / "öffne Studio" (DE) / "abre Studio" (ES) | `gui-navigation/guide.md` |
| Render, photo-realistic image / "сделай рендер" (RU) / "fais un rendu" (FR) / "render machen" (DE) / "hacer render" (ES) / "レンダリング" (JA) / "渲染" (ZH) | `render/guide.md` |
| Parse .ldr/.mpd file / "Разбери файл" (RU) / "analyse ce fichier" (FR) / "datei analysieren" (DE) / "analiza archivo" (ES) | `ldraw-format/guide.md` |
| Create model, generate construction / "Создай модель" (RU) / "crée un modèle" (FR) / "erstelle Modell" (DE) / "crea modelo" (ES) / "モデル作成" (JA) / "创建模型" (ZH) | `model-generation/guide.md` |
| Parts list, BOM, buy on Bricklink / "Список деталей" (RU) / "liste de pièces" (FR) / "Teileliste" (DE) / "lista de piezas" (ES) | `bom-export/guide.md` |
| Convert STL/3D to LEGO, voxelization, algorithms, ML tools, research papers | `knowledge/INDEX.md` |

Multiple sub-skills can be loaded simultaneously if the task spans domains (e.g. generate + export BOM).

---

## Key Concepts (shared across all sub-skills)

**LDraw format** — open text-based standard for LEGO models. Files: `.ldr` (single model), `.mpd` (multi-model / instructions).

**Part ID** — numeric identifier for each LEGO part, shared between LDraw and BrickLink catalog (e.g. `3001` = standard 2x4 brick).

**Color ID** — LDraw uses its own numeric color system (e.g. `4` = red). BrickLink uses different IDs. Mapping is in `bom-export/references/color-ids.md`.

**Studio file format** — `.io` files are ZIP archives containing LDraw data + Studio metadata. Can be unzipped and read as LDraw.

---

## Learning System

During every working session, Claude actively maintains the `learning/` directory.

### Three-mode operation

| Mode | Trigger | Action |
|---|---|---|
| 🔵 **Explore** | Unknown situation, no pattern exists | Try it, write to `observations.md` as `[UNVERIFIED]` |
| 🟢 **Confirm** | User says "remember this", "it works", "save it" (any language) | Promote observation to `patterns.md` |
| 🔴 **Reject** | User says "doesn't work", "don't do this" (any language) | Move to `failed.md` as anti-pattern |

### Rules

- **Always check `learning/patterns.md` and `learning/failed.md` at the start of a session** before doing anything — they override default sub-skill instructions
- Known confirmed patterns → use directly, no experimentation
- Contradiction with `failed.md` → warn user before attempting
- New approach tried → always write to `observations.md` immediately, don't wait

### Writing to observations.md

Append an entry whenever something noteworthy happens:
```
## [UNVERIFIED] YYYY-MM-DD — Short title
**Context:** what was being attempted
**Observation:** what was noticed
**Reproducible:** yes / no / unknown
**Promote to:** patterns.md / failed.md / discard
```

---

## Session Auto-Summary Protocol

**Run this at the end of every working session**, or when user signals end of session in any language
("done", "wrap up", "save", "закончили", "подведи итоги" (RU), "c'est fini", "on s'arrête" (FR),
"fertig", "speichern" (DE), "terminado", "guardar" (ES), "終わり", "保存して" (JA), "完成了", "保存" (ZH), etc.).

### Steps

1. **Read `learning/observations.md`** — find all `[UNVERIFIED]` entries from today
   Also read `projects/<active-project>/observations.md` if a project was active this session
2. **For each entry**, propose one of:
   - ✅ Promote to `patterns.md` — if it worked reliably
     - General insight → `learning/patterns.md`
     - Project-specific → `projects/<name>/patterns.md`
   - ❌ Move to `failed.md` — if it failed or caused problems
     - General → `learning/failed.md` | Project-specific → `projects/<name>/failed.md`
   - 🗑️ Discard — if it was a one-off, not generalizable
3. **Present the proposal to user** — short list, one line per entry
4. **Wait for confirmation** — then write the promoted entries to their files
5. **Append an entry to `CHANGELOG`** using semver format `[vX.Y.Z] YYYY-MM-DD`
   - Patch (Z): fixes, renames, content tweaks
   - Minor (Y): new sub-skill or major feature added
   - Major (X): breaking restructure
   - Current version is in the latest CHANGELOG entry — increment accordingly
6. **Repackage the skill** if significant patterns were added:
   ```bash
   cd ~/Dev/BrickLink\ Studio\ Skill && ./build.sh
   ```

### Summary format for user

Present summary in the user's language — but all writes to skill files must be in English.

```
📋 Session summary YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Observations this session: N
Sub-skills used: gui-navigation, model-generation
Proposed:
  ✅ → patterns.md: "Short pattern title in English"
  ❌ → failed.md:   "What did not work, in English"
  🗑️  Discard:      "One-off, not generalizable"

Confirm?
```

After confirmation, also:
6. **Request user rating** (see User Feedback section below)
7. **Update `learning/stats.md`** with session data

---

## Language Policy

> **All skill file content must be written in English**, regardless of the language the user speaks.
> This ensures compatibility across all models and contributors worldwide.

This applies to:
- All entries in `learning/observations.md`, `learning/patterns.md`, `learning/failed.md`
- All entries in `learning/stats.md`
- All CHANGELOG entries
- Any new reference content added during a session

The user interface (summaries, questions, explanations) should be in the user's language.
Skill file content is always English.

---

## User Feedback System

After the session summary is confirmed, request a rating:

```
How was this session?
⭐⭐⭐⭐⭐  Everything worked great
🔄  Claude asked too many clarifying questions  
⚠️  A pattern from the skill did not work as expected
❌  Something went wrong — [describe briefly]
```

Log the rating to `learning/stats.md` (see format below).
If rating is ⚠️ or ❌ — ask one follow-up question to understand what failed, then log it.

---

## Session Statistics

Maintain `learning/stats.md` to track skill usage over time.
Update at the end of every session after user confirms summary.

### stats.md entry format

```markdown
## YYYY-MM-DD — Session N
**Sub-skills used:** gui-navigation, model-generation
**Observations logged:** 3
**Promoted to patterns:** 1
**Moved to failed:** 1
**Discarded:** 1
**User rating:** ⭐⭐⭐⭐⭐ / 🔄 / ⚠️ / ❌
**User note:** (optional, verbatim if provided)
```

This file is tracked in git — it provides signal to maintainers about which sub-skills are
used most, which patterns fail, and overall skill health across users.

---

## Sub-skill Index

- `gui-navigation/guide.md` — Navigate Studio UI, place and move parts (Computer Use only)
- `render/guide.md` — Photo-realistic rendering via Studio or Blender (Computer Use only)
- `ldraw-format/guide.md` — Read, parse, validate LDraw and .io files
- `model-generation/guide.md` — Generate LDraw code from natural language descriptions
- `bom-export/guide.md` — Extract parts list, map to BrickLink catalog, estimate cost
- `knowledge/INDEX.md` — Curated external knowledge: algorithms, tools, repos, research (read INDEX first, then category files as needed)

## Project Index

Projects are specific recurring build types with their own isolated knowledge.
Always check `projects/_INDEX.md` at session start.

- `projects/part-piles/` — 🟢 Active: random part pile renders for app graphics
- `projects/brickheadz/` — 🟡 Placeholder: Brickheadz-style figures
- `projects/_template/` — Template for new projects (copy to start a new one)
