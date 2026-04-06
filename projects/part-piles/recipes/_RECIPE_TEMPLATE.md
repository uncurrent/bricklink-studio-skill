---
name: {Recipe Name}
version: {N}
project: {project-name}
status: verified | draft
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
---

## Purpose

One sentence: what this recipe produces and why.

## Inputs

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| ... | ... | ... | ... | ... |

## Pipeline

Step-by-step, each step referencing a script:

### Step 1: {Name}
- **Script:** `scripts/{path}`
- **Command:** `python3 {script} {args}`
- **Output:** {what this step produces}

### Step 2: {Name}

...

## Batch Usage

Full command sequence to produce N outputs end-to-end.

## Output Spec

- **Format:** {.io, .ldr, .png…}
- **Naming:** {pattern, e.g., "Pocket {N}.io"}
- **Location:** {output path}
- **Quality criteria:** {what "good" looks like}

## Known Limitations

What this recipe does NOT handle or where it breaks down.

## History

How this recipe evolved. Link to `scripts/archive/` entries if relevant.
