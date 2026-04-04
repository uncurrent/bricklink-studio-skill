# CHANGELOG — bricklink-studio skill

Format: `[vX.Y.Z] YYYY-MM-DD — Description`
- Major (X): breaking restructure
- Minor (Y): new sub-skill or significant feature
- Patch (Z): fixes, renames, content updates

---

## [v1.0.4] 2026-04-05 — Fix: single SKILL.md requirement
- Renamed sub-skill SKILL.md files to guide.md (platform requires exactly one SKILL.md)
- Renamed README.md to README.txt
- Updated all internal links

## [v1.0.3] 2026-04-05 — README + authors
- Added README.txt with project overview, structure, compatibility table
- Authors: Slava Yaremenko (Head of Design, Brickit.app) with Claude

## [v1.0.2] 2026-04-05 — Feedback system + English policy + Git config
- Added User Feedback System (session rating + stats.md)
- Added Language Policy: all skill files must be in English
- Cleaned all Russian text from skill files (routing examples excepted)
- Added learning/stats.md for cross-user signal
- Added .gitignore (excludes observations.md and *.skill)
- Added CONTRIBUTING.md with PR workflow and entry formats

## [v1.0.1] 2026-04-05 — Learning system
- Added learning/ directory with observations, patterns, failed logs
- Added session auto-summary protocol to master SKILL.md
- Added CHANGELOG

## [v1.0.0] 2026-04-05 — Initial release
- Master skill with compatibility matrix and routing logic
- Sub-skill: gui-navigation (Computer Use / Cowork)
- Sub-skill: ldraw-format (all environments)
- Sub-skill: model-generation (all environments)
- Sub-skill: bom-export (all environments)
- References: panels, shortcuts, workflows, common-parts, patterns, color-ids
