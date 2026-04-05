# Projects — Index

Project-specific knowledge lives here. Each project folder is self-contained:
its own guide, patterns, and failed anti-patterns — independent from the general `learning/` files.

**When to load a project file:**
- User's task matches a known project type below → load `projects/<name>/guide.md` first
- Then load the relevant sub-skills as usual
- Project patterns override general `learning/patterns.md` when they conflict

**When NOT to load project files:**
- Generic Studio tasks with no project context → use general `learning/` only
- Exploring something new → start general, create a new project folder if it becomes recurring

---

## Active Projects

| Project | Folder | What it is | Status |
|---|---|---|---|
| Part Piles | `part-piles/` | Random piles of LEGO parts for app graphics / bag imagery | 🟢 Active |
| Brickheadz | `brickheadz/` | Brickheadz-style figures (oversized head, minimal body) | 🟡 Placeholder |

---

## Adding a New Project

1. Copy `_template/` → rename to `projects/<project-name>/`
2. Fill in `guide.md`: what the project is, goals, constraints, relevant sub-skills
3. Add a row to the table above
4. As you work: write observations to `observations.md`, promote to `patterns.md` / `failed.md`
5. Add to `SKILL.md` sub-skill index if the project becomes a major recurring context
