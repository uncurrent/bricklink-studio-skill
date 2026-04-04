# Contributing to bricklink-studio skill

## What to contribute

| File | Contribute? | How |
|---|---|---|
| `learning/patterns.md` | ✅ Yes | PR after a few sessions |
| `learning/failed.md` | ✅ Yes | PR after confirmed failure |
| `learning/stats.md` | ✅ Yes | PR each session |
| `learning/observations.md` | ❌ No | Local only, in .gitignore |
| `SKILL.md` files | ✅ Yes | PR with description |
| `references/*.md` | ✅ Yes | PR with description |
| `*.skill` | ❌ No | Generated artifact |

## Language policy

**All skill file content must be in English.**
This applies to every file in this repository without exception.
User interfaces and conversations can be in any language — skill files cannot.

## Workflow

```
fork → work locally for 2–3 sessions → PR
```

1. Fork the repo
2. Use the skill normally — Claude writes to your local `learning/` files
3. After a few sessions, review `learning/patterns.md` and `learning/failed.md`
4. Add context to each entry before submitting (OS, Studio version, date)
5. Open a PR — keep it focused: one topic per PR

## Entry format for patterns.md

Always include context so maintainers can assess generalizability:

```markdown
## YYYY-MM-DD — Short descriptive title
**Context:** When this applies (OS, Studio version, specific workflow)
**Pattern:** What to do, concisely
**Confirmed:** How many sessions / times observed
**Sub-skill:** Which sub-skill this belongs to
```

## Entry format for failed.md

```markdown
## YYYY-MM-DD — Short descriptive title
**What was tried:** Description of the approach
**What happened:** The failure or bad outcome
**Avoid because:** Root cause if known
**Alternative:** What to do instead (if known)
**Context:** OS, Studio version, conditions
```

## Resolving conflicts

If your pattern contradicts an existing one — note both in the PR description.
Maintainer will add a context qualifier (e.g. "Windows only", "Studio 2.1+") rather than removing either.

## Promoting patterns to sub-skills

When a pattern in `learning/patterns.md` has been confirmed by 3+ independent users,
the maintainer may integrate it directly into the relevant sub-skill's SKILL.md or references/.
The original entry in patterns.md is then marked `[INTEGRATED]` and dated.
