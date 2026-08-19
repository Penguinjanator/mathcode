# Skills

The repo-root `skills/` directory is not a runtime skill drop folder.
Project-local skills belong at `.mathcode/skills/<name>/SKILL.md`; standalone
`skills/*.md` files are ignored.

## Format

Each project skill gets its own directory. The directory name is the skill
name, and `SKILL.md` contains the instructions and frontmatter.

```markdown
---
name: my-skill
description: What this skill does
---

# My Skill Title

The actual skill content — tactics, patterns, reference material, etc.
```

## Built-in Skills

These domain skills are compiled into the binary (no `.md` file needed):

- `compilation-errors` — Common Lean 4 error patterns and fixes
- `group-theory` — Group theory proving patterns and key lemmas
- `number-theory` — Number theory tactics and Fermat/Euler theorems
- `parity-proofs` — Even/odd proof strategies
- `proof-golfing` — Proof optimization patterns
- `tactic-cascade` — Fast-to-slow tactic ordering reference
- `type-coercion-patterns` — Nat.card vs Fintype.card, Fact vs Prop, etc.

The optional `/lean` skill may recommend these strategies, but it does not
force a planner, tactic order, or proof scheme.
